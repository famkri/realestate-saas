cat > init_db.py <<'EOF'
#!/usr/bin/env python3
"""
Database initialization script
Creates tables and optionally creates a default user
"""

import sys
import os
from sqlalchemy.orm import Session

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.deps import SessionLocal, get_password_hash, init_db
from app.models import User

def create_default_user():
    """Create a default admin user"""
    db: Session = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            print("✅ Default admin user created (username: admin, password: admin123)")
        else:
            print("ℹ️  Admin user already exists")
    
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    
    finally:
        db.close()

def main():
    """Initialize database and create default user"""
    print("🚀 Initializing database...")
    
    try:
        # Initialize database tables
        init_db()
        print("✅ Database tables created successfully")
        
        # Create default user
        create_default_user()
        
        print("🎉 Database initialization completed!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF
