"""
Script to create the Newsletter table in the database.
Run this script to add newsletter functionality to the existing database.
"""

from app import app, db
from models import Newsletter

def create_newsletter_table():
    """Create the newsletter table if it doesn't exist"""
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            print("✓ Newsletter table created successfully!")
            
            # Verify the table was created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'newsletters' in tables:
                print("✓ Newsletter table verified in database")
                
                # Show table structure
                columns = inspector.get_columns('newsletters')
                print("\nTable structure:")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
            else:
                print("✗ Newsletter table not found in database")
                
        except Exception as e:
            print(f"✗ Error creating newsletter table: {str(e)}")
            raise

if __name__ == '__main__':
    create_newsletter_table()
