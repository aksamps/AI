from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app import db
from models import Book

books_bp = Blueprint('books', __name__, url_prefix='/api/books')

@books_bp.route('', methods=['GET'])
def list_books():
    """List all books"""
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Book.query
    
    if search:
        query = query.filter(
            (Book.title.ilike(f'%{search}%')) |
            (Book.author.ilike(f'%{search}%'))
        )
    
    books = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'data': [book.to_dict() for book in books.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': books.total,
            'pages': books.pages
        }
    }), 200

@books_bp.route('/<book_id>', methods=['GET'])
def get_book(book_id):
    """Get book by ID"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify(book.to_dict()), 200

@books_bp.route('', methods=['POST'])
@jwt_required()
def create_book():
    """Create new book (admin only)"""
    # Auth check for admin role - to be implemented in Phase 2
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    book = Book(
        title=data.get('title'),
        author=data.get('author'),
        isbn=data.get('isbn'),
        edition=data.get('edition'),
        description=data.get('description'),
        total_quantity=data.get('total_quantity', 1),
        available_quantity=data.get('total_quantity', 1)
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201

@books_bp.route('/<book_id>', methods=['PATCH'])
@jwt_required()
def update_book(book_id):
    """Update book (admin only)"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'isbn' in data:
        book.isbn = data['isbn']
    if 'edition' in data:
        book.edition = data['edition']
    if 'description' in data:
        book.description = data['description']
    if 'total_quantity' in data:
        book.total_quantity = data['total_quantity']
    
    db.session.commit()
    
    return jsonify(book.to_dict()), 200

@books_bp.route('/<book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    """Delete book (admin only)"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': 'Book deleted'}), 200
