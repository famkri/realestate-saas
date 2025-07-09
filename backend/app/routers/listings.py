from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import Optional, List
from datetime import datetime, timedelta
import csv
import io

from ..deps import get_db, get_current_active_user
from ..models import Listing, User

router = APIRouter()

@router.get("/listings")
async def get_listings(
    # Pagination
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    
    # Filters
    source: Optional[str] = Query(None, description="Filter by source (kleinanzeigen, immowelt, etc.)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    min_rooms: Optional[float] = Query(None, ge=0, description="Minimum number of rooms"),
    max_rooms: Optional[float] = Query(None, ge=0, description="Maximum number of rooms"),
    min_area: Optional[float] = Query(None, ge=0, description="Minimum area in sqm"),
    max_area: Optional[float] = Query(None, ge=0, description="Maximum area in sqm"),
    
    # Sorting
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    
    # Date filters
    created_after: Optional[datetime] = Query(None, description="Filter listings created after this date"),
    created_before: Optional[datetime] = Query(None, description="Filter listings created before this date"),
    
    # Dependencies
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get listings with advanced filtering and pagination"""
    
    # Build query
    query = db.query(Listing).filter(Listing.is_active == True)
    
    # Apply filters
    if source:
        query = query.filter(Listing.source == source)
    
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    
    if location:
        query = query.filter(Listing.location.ilike(f"%{location}%"))
    
    if property_type:
        query = query.filter(Listing.property_type == property_type)
    
    if min_rooms is not None:
        query = query.filter(Listing.rooms >= min_rooms)
    
    if max_rooms is not None:
        query = query.filter(Listing.rooms <= max_rooms)
    
    if min_area is not None:
        query = query.filter(Listing.area_sqm >= min_area)
    
    if max_area is not None:
        query = query.filter(Listing.area_sqm <= max_area)
    
    if created_after:
        query = query.filter(Listing.created_at >= created_after)
    
    if created_before:
        query = query.filter(Listing.created_at <= created_before)
    
    # Apply sorting
    if hasattr(Listing, sort_by):
        order_column = getattr(Listing, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)
    
    # Get total count for pagination info
    total_count = query.count()
    
    # Apply pagination
    listings = query.offset(skip).limit(limit).all()
    
    # Convert to dict for JSON response
    listings_data = [listing.to_dict() for listing in listings]
    
    return {
        "listings": listings_data,
        "total_count": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total_count
    }

@router.get("/listings/stats")
async def get_listings_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get statistics about listings"""
    
    total_listings = db.query(Listing).filter(Listing.is_active == True).count()
    
    # Count by source
    sources = db.query(Listing.source, db.func.count(Listing.id)).filter(
        Listing.is_active == True
    ).group_by(Listing.source).all()
    
    # Average price
    avg_price = db.query(db.func.avg(Listing.price)).filter(
        and_(Listing.is_active == True, Listing.price.isnot(None))
    ).scalar()
    
    # Recent listings (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_count = db.query(Listing).filter(
        and_(Listing.is_active == True, Listing.created_at >= yesterday)
    ).count()
    
    return {
        "total_listings": total_listings,
        "sources": dict(sources),
        "average_price": round(avg_price, 2) if avg_price else None,
        "recent_listings_24h": recent_count
    }

@router.get("/listings/export")
async def export_listings(
    format: str = Query("csv", regex="^(csv|json)$", description="Export format"),
    # Same filters as get_listings
    source: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    location: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    min_rooms: Optional[float] = Query(None, ge=0),
    max_rooms: Optional[float] = Query(None, ge=0),
    min_area: Optional[float] = Query(None, ge=0),
    max_area: Optional[float] = Query(None, ge=0),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export listings to CSV or JSON"""
    
    # Build query (same logic as get_listings)
    query = db.query(Listing).filter(Listing.is_active == True)
    
    # Apply all filters (same as above)
    if source:
        query = query.filter(Listing.source == source)
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if location:
        query = query.filter(Listing.location.ilike(f"%{location}%"))
    if property_type:
        query = query.filter(Listing.property_type == property_type)
    if min_rooms is not None:
        query = query.filter(Listing.rooms >= min_rooms)
    if max_rooms is not None:
        query = query.filter(Listing.rooms <= max_rooms)
    if min_area is not None:
        query = query.filter(Listing.area_sqm >= min_area)
    if max_area is not None:
        query = query.filter(Listing.area_sqm <= max_area)
    if created_after:
        query = query.filter(Listing.created_at >= created_after)
    if created_before:
        query = query.filter(Listing.created_at <= created_before)
    
    listings = query.all()
    
    if format == "csv":
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Source', 'Title', 'Price', 'Location', 'Property Type',
            'Rooms', 'Area (sqm)', 'URL', 'Created At'
        ])
        
        # Write data
        for listing in listings:
            writer.writerow([
                listing.id,
                listing.source,
                listing.title,
                listing.price,
                listing.location,
                listing.property_type,
                listing.rooms,
                listing.area_sqm,
                listing.url,
                listing.created_at.isoformat() if listing.created_at else ''
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=listings.csv"}
        )
    
    else:  # JSON format
        listings_data = [listing.to_dict() for listing in listings]
        return {"listings": listings_data, "count": len(listings_data)}

@router.get("/listings/{listing_id}")
async def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific listing by ID"""
    
    listing = db.query(Listing).filter(
        and_(Listing.id == listing_id, Listing.is_active == True)
    ).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return listing.to_dict()
