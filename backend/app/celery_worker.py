import os
import json
import logging
from celery import Celery
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from .deps import SessionLocal
from .models import Listing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "real_estate_worker",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0")
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'app.celery_worker.store_listing': {'queue': 'listings'},
        'app.celery_worker.cleanup_old_listings': {'queue': 'maintenance'},
    }
)

@celery_app.task(bind=True, max_retries=3)
def store_listing(self, listing_data: dict):
    """Store a single listing in the database"""
    db: Session = SessionLocal()
    
    try:
        # Check if listing already exists
        existing_listing = db.query(Listing).filter(
            Listing.url == listing_data.get("url")
        ).first()
        
        if existing_listing:
            # Update existing listing
            for key, value in listing_data.items():
                if hasattr(existing_listing, key) and key != 'id':
                    setattr(existing_listing, key, value)
            
            existing_listing.updated_at = datetime.utcnow()
            existing_listing.raw_data = json.dumps(listing_data)
            
            db.commit()
            logger.info(f"Updated listing: {listing_data.get('url')}")
            return {"status": "updated", "listing_id": existing_listing.id}
        
        else:
            # Create new listing
            new_listing = Listing(
                source=listing_data.get("source"),
                title=listing_data.get("title"),
                price=listing_data.get("price"),
                location=listing_data.get("location"),
                url=listing_data.get("url"),
                description=listing_data.get("description"),
                property_type=listing_data.get("property_type"),
                rooms=listing_data.get("rooms"),
                area_sqm=listing_data.get("area_sqm"),
                raw_data=json.dumps(listing_data)
            )
            
            db.add(new_listing)
            db.commit()
            db.refresh(new_listing)
            
            logger.info(f"Created new listing: {listing_data.get('url')}")
            return {"status": "created", "listing_id": new_listing.id}
    
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Integrity error for listing {listing_data.get('url')}: {e}")
        return {"status": "error", "message": "Duplicate listing"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing listing {listing_data.get('url')}: {e}")
        
        # Retry the task
        try:
            raise self.retry(countdown=60, exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for listing: {listing_data.get('url')}")
            return {"status": "failed", "message": str(e)}
    
    finally:
        db.close()

@celery_app.task
def store_listings_batch(listings_data: list):
    """Store multiple listings in batch"""
    results = []
    
    for listing_data in listings_data:
        result = store_listing.delay(listing_data)
        results.append(result.id)
    
    return {"batch_size": len(listings_data), "task_ids": results}

@celery_app.task
def cleanup_old_listings(days_old: int = 30):
    """Clean up old listings that are no longer active"""
    db: Session = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Mark old listings as inactive instead of deleting
        updated_count = db.query(Listing).filter(
            Listing.created_at < cutoff_date
        ).update({"is_active": False})
        
        db.commit()
        
        logger.info(f"Marked {updated_count} old listings as inactive")
        return {"status": "success", "updated_count": updated_count}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error during cleanup: {e}")
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()

@celery_app.task
def get_scraping_stats():
    """Get statistics about scraping activities"""
    db: Session = SessionLocal()
    
    try:
        total_listings = db.query(Listing).count()
        active_listings = db.query(Listing).filter(Listing.is_active == True).count()
        
        # Count by source
        sources = db.query(Listing.source, db.func.count(Listing.id)).group_by(
            Listing.source
        ).all()
        
        return {
            "total_listings": total_listings,
            "active_listings": active_listings,
            "sources": dict(sources)
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()

# Periodic tasks (uncomment to enable)
# from celery.schedules import crontab
# 
# celery_app.conf.beat_schedule = {
#     'cleanup-old-listings': {
#         'task': 'app.celery_worker.cleanup_old_listings',
#         'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
#     },
# }

if __name__ == "__main__":
    celery_app.start()
