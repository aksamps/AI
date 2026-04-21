"""
Database seeding script - populates initial test data

Run: python database/seed.py
"""

import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app, db
from backend.models import Organization, User, Membership, Book, Checkout
from datetime import datetime, timedelta
from uuid import uuid4

def seed_database():
    """Seed database with test data"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("Creating test organization...")
        org = Organization(
            name='Test Library',
            description='A test library for development'
        )
        db.session.add(org)
        db.session.flush()  # Get the ID
        
        print("Creating test users...")
        users = []
        for i in range(5):
            user = User(
                organization_id=org.id,
                email=f'user{i+1}@example.com',
                name=f'Test User {i+1}',
                oauth_provider='google',
                oauth_id=f'google-user-{i+1}',
                avatar_url='https://lh3.googleusercontent.com/a/default-user'
            )
            db.session.add(user)
            users.append(user)
        
        print("Creating memberships...")
        for i, user in enumerate(users):
            role = 'admin' if i == 0 else 'member'
            membership = Membership(
                user_id=user.id,
                organization_id=org.id,
                role=role,
                status='active'
            )
            db.session.add(membership)
        
        print("Creating test books...")
        books_data = [
            ('To Kill a Mockingbird', 'Harper Lee', '9780061120084'),
            ('1984', 'George Orwell', '9780451524935'),
            ('Pride and Prejudice', 'Jane Austen', '9780141439518'),
            ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565'),
            ('The Catcher in the Rye', 'J.D. Salinger', '9780316769174'),
            ('The Hobbit', 'J.R.R. Tolkien', '9780547928227'),
            ('Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', '9780439708180'),
            ('The Lord of the Rings', 'J.R.R. Tolkien', '9780544003415'),
            ('Brave New World', 'Aldous Huxley', '9780060850524'),
            ('The Alchemist', 'Paulo Coelho', '9780062315007'),
        ]
        
        books = []
        for title, author, isbn in books_data:
            book = Book(
                organization_id=org.id,
                title=title,
                author=author,
                isbn=isbn,
                edition='1st Edition',
                description=f'{title} by {author}',
                total_quantity=3,
                available_quantity=3
            )
            db.session.add(book)
            books.append(book)
        
        db.session.flush()
        
        print("Creating sample checkouts...")
        # User 1 checks out a couple of books
        if len(users) > 0 and len(books) > 1:
            checkout1 = Checkout(
                user_id=users[0].id,
                book_id=books[0].id,
                organization_id=org.id,
                due_date=datetime.utcnow() + timedelta(days=14),
                status='active'
            )
            checkout2 = Checkout(
                user_id=users[0].id,
                book_id=books[1].id,
                organization_id=org.id,
                due_date=datetime.utcnow() + timedelta(days=7),
                status='active'
            )
            db.session.add(checkout1)
            db.session.add(checkout2)
            books[0].available_quantity -= 1
            books[1].available_quantity -= 1
        
        db.session.commit()
        
        print("✓ Database seeded successfully!")
        print(f"  - Organization: {org.name}")
        print(f"  - Users: {len(users)}")
        print(f"  - Books: {len(books)}")
        print(f"  - Checkouts: 2 (from test user)")

if __name__ == '__main__':
    seed_database()
