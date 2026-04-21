from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from models import Checkout, Book, User

checkouts_bp = Blueprint('checkouts', __name__, url_prefix='/api/checkouts')

@checkouts_bp.route('', methods=['POST'])
@jwt_required()
def checkout_book():
    """Checkout a book"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('book_id'):
        return jsonify({'error': 'Missing book_id'}), 400
    
    book = Book.query.get(data.get('book_id'))
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    if book.available_quantity <= 0:
        return jsonify({'error': 'Book not available'}), 400
    
    # Check for overdue items (user cannot checkout if they have unreturned overdue books)
    user = User.query.get(user_id)
    overdue_checkouts = Checkout.query.filter(
        Checkout.user_id == user_id,
        Checkout.status == 'active',
        Checkout.due_date < datetime.utcnow()
    ).all()
    
    if overdue_checkouts:
        return jsonify({
            'error': 'Cannot checkout - you have overdue items',
            'overdue_count': len(overdue_checkouts)
        }), 400
    
    # Create checkout
    due_date = datetime.utcnow() + timedelta(days=14)
    checkout = Checkout(
        user_id=user_id,
        book_id=data.get('book_id'),
        organization_id=user.organization_id,
        due_date=due_date,
        status='active'
    )
    
    book.available_quantity -= 1
    
    db.session.add(checkout)
    db.session.commit()
    
    return jsonify(checkout.to_dict()), 201

@checkouts_bp.route('', methods=['GET'])
@jwt_required()
def list_user_checkouts():
    """List user's checkouts"""
    user_id = get_jwt_identity()
    
    checkouts = Checkout.query.filter(Checkout.user_id == user_id).all()
    
    return jsonify({
        'data': [checkout.to_dict() for checkout in checkouts]
    }), 200

@checkouts_bp.route('/<checkout_id>/return', methods=['POST'])
@jwt_required()
def return_book(checkout_id):
    """Return a book"""
    user_id = get_jwt_identity()
    
    checkout = Checkout.query.get(checkout_id)
    if not checkout:
        return jsonify({'error': 'Checkout not found'}), 404
    
    if checkout.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if checkout.status == 'returned':
        return jsonify({'error': 'Book already returned'}), 400
    
    checkout.returned_at = datetime.utcnow()
    checkout.status = 'returned'
    
    book = checkout.book
    book.available_quantity += 1
    
    db.session.commit()
    
    return jsonify(checkout.to_dict()), 200

@checkouts_bp.route('/<checkout_id>', methods=['GET'])
@jwt_required()
def get_checkout(checkout_id):
    """Get checkout details"""
    user_id = get_jwt_identity()
    
    checkout = Checkout.query.get(checkout_id)
    if not checkout:
        return jsonify({'error': 'Checkout not found'}), 404
    
    if checkout.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(checkout.to_dict()), 200
