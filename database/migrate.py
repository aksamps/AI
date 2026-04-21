# Database migration script
# Run: alembic upgrade head

import os
from alembic import command
from alembic.config import Config

def migrate():
    """Run database migrations"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

if __name__ == '__main__':
    migrate()
