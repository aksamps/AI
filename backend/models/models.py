from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Organization(db.Model):
    """Organization model for multi-tenancy"""
    __tablename__ = 'organizations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='organization', lazy=True, cascade='all, delete-orphan')
    memberships = db.relationship('Membership', backref='organization', lazy=True, cascade='all, delete-orphan')
    books = db.relationship('Book', backref='organization', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    oauth_provider = db.Column(db.String(50), nullable=False)  # 'google' or 'github'
    oauth_id = db.Column(db.String(255), nullable=False)
    oauth_access_token = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='user', lazy=True, cascade='all, delete-orphan')
    checkouts = db.relationship('Checkout', backref='user', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('organization_id', 'oauth_provider', 'oauth_id'),)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'name': self.name,
            'oauth_provider': self.oauth_provider,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat()
        }

class Membership(db.Model):
    """User organization membership"""
    __tablename__ = 'memberships'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'), nullable=False)
    role = db.Column(db.String(50), default='member')  # 'admin' or 'member'
    status = db.Column(db.String(50), default='active')  # 'active' or 'revoked'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'organization_id'),)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Book(db.Model):
    """Book model"""
    __tablename__ = 'books'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20))
    edition = db.Column(db.String(100))
    description = db.Column(db.Text)
    total_quantity = db.Column(db.Integer, default=1)
    available_quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    checkouts = db.relationship('Checkout', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'edition': self.edition,
            'description': self.description,
            'total_quantity': self.total_quantity,
            'available_quantity': self.available_quantity,
            'created_at': self.created_at.isoformat()
        }

class Checkout(db.Model):
    """Book checkout record"""
    __tablename__ = 'checkouts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(UUID(as_uuid=True), db.ForeignKey('books.id'), nullable=False)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'), nullable=False)
    checkout_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')  # 'active' or 'returned'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'book': self.book.to_dict() if self.book else None,
            'checkout_at': self.checkout_at.isoformat(),
            'due_date': self.due_date.isoformat(),
            'returned_at': self.returned_at.isoformat() if self.returned_at else None,
            'status': self.status
        }

class AuditLog(db.Model):
    """Audit log for agent actions and approvals"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'), nullable=False)
    action_type = db.Column(db.String(100), nullable=False)  # 'pr_review', 'approval', 'deployment', etc.
    actor = db.Column(db.String(255), nullable=False)  # Agent name or user email
    resource_type = db.Column(db.String(100))  # 'pr', 'workflow', 'book', 'user'
    resource_id = db.Column(db.String(255))  # PR number, workflow run ID, book ID, etc.
    details = db.Column(db.JSON)  # Additional context
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'action_type': self.action_type,
            'actor': self.actor,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'created_at': self.created_at.isoformat()
        }
