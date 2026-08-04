from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Base

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def _ensure_user_table_compatibility() -> None:
    """Backfill any missing columns needed by the ORM model."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        if "users" not in inspector.get_table_names():
            return

        column_names = {
            row[0]
            for row in connection.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'users'"
                )
            )
        }

        if "hashed_password" in column_names:
            connection.execute(
                text("ALTER TABLE users DROP COLUMN IF EXISTS hashed_password")
            )

        if "password_hash" not in column_names:
            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) "
                    "NOT NULL DEFAULT ''"
                )
            )

        if "is_active" in column_names:
            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ALTER COLUMN is_active TYPE BOOLEAN "
                    "USING CASE "
                    "WHEN LOWER(CAST(is_active AS TEXT)) IN ('true', 't', '1', 'yes', 'y') THEN TRUE "
                    "WHEN LOWER(CAST(is_active AS TEXT)) IN ('false', 'f', '0', 'no', 'n') THEN FALSE "
                    "ELSE TRUE "
                    "END"
                )
            )


def init_db() -> None:
    """Create tables for local development and align legacy schemas."""
    _ensure_user_table_compatibility()
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
