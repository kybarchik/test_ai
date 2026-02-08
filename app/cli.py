import argparse
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.core.logger import setup_logging
from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


async def create_user(session: AsyncSession, username: str, password: str) -> None:
    """Create a user with the provided credentials."""
    repository = UserRepository(session)
    hashed_password = get_password_hash(password)
    await repository.create_user(username=username, hashed_password=hashed_password)
    logger.info("User created", extra={"username": username})


async def run_create_user(username: str, password: str) -> None:
    """Run the create user workflow in an async session."""
    async with SessionLocal() as session:
        await create_user(session, username, password)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="MVP CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create_user_parser = subparsers.add_parser("create-user", help="Create a new user")
    create_user_parser.add_argument("--username", required=True)
    create_user_parser.add_argument("--password", required=True)
    return parser.parse_args()


def main() -> None:
    """Entry point for CLI commands."""
    setup_logging()
    args = parse_args()
    if args.command == "create-user":
        asyncio.run(run_create_user(args.username, args.password))


if __name__ == "__main__":
    main()
