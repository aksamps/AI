"""Package init for routes"""
from routes.health import health_bp
from routes.auth import auth_bp
from routes.books import books_bp
from routes.checkouts import checkouts_bp
from routes.memberships import memberships_bp

__all__ = ['health_bp', 'auth_bp', 'books_bp', 'checkouts_bp', 'memberships_bp']
