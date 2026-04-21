from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app import db
from models import Membership, User

memberships_bp = Blueprint('memberships', __name__, url_prefix='/api/memberships')

@memberships_bp.route('', methods=['POST'])
@jwt_required()
def create_membership():
    """Create membership (admin only)"""
    data = request.get_json()
    
    if not data or not data.get('user_id'):
        return jsonify({'error': 'Missing user_id'}), 400
    
    user = User.query.get(data.get('user_id'))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    existing = Membership.query.filter(
        Membership.user_id == data.get('user_id'),
        Membership.organization_id == user.organization_id
    ).first()
    
    if existing:
        return jsonify({'error': 'User already a member'}), 400
    
    membership = Membership(
        user_id=data.get('user_id'),
        organization_id=user.organization_id,
        role=data.get('role', 'member'),
        status='active'
    )
    
    db.session.add(membership)
    db.session.commit()
    
    return jsonify(membership.to_dict()), 201

@memberships_bp.route('', methods=['GET'])
@jwt_required()
def list_memberships():
    """List all memberships (admin only)"""
    memberships = Membership.query.all()
    
    return jsonify({
        'data': [m.to_dict() for m in memberships]
    }), 200

@memberships_bp.route('/<membership_id>', methods=['PATCH'])
@jwt_required()
def update_membership(membership_id):
    """Update membership (admin only)"""
    membership = Membership.query.get(membership_id)
    if not membership:
        return jsonify({'error': 'Membership not found'}), 404
    
    data = request.get_json()
    
    if 'role' in data:
        membership.role = data['role']
    if 'status' in data:
        membership.status = data['status']
    
    db.session.commit()
    
    return jsonify(membership.to_dict()), 200

@memberships_bp.route('/<membership_id>', methods=['DELETE'])
@jwt_required()
def delete_membership(membership_id):
    """Delete membership (revoke) (admin only)"""
    membership = Membership.query.get(membership_id)
    if not membership:
        return jsonify({'error': 'Membership not found'}), 404
    
    membership.status = 'revoked'
    db.session.commit()
    
    return jsonify({'message': 'Membership revoked'}), 200
