from datetime import datetime, timedelta
from typing import Any, Union, Optional

import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from .models import UserCreate, UserResponse, User
from config import settings

ALGORITHM = "HS256"
# Create a single instance of CryptContext for better performance and thread safety.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_token = OAuth2PasswordBearer(tokenUrl="/login/access-token/")


def authenticate(user: UserCreate, password: str) -> Optional[UserResponse]:
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_access_token(
        subject: Union[str, Any], expire_delta: Optional[timedelta] = None
) -> str:
    """Create an access token with an expiration date.

    :param subject: The subject for the token (e.g., user ID)
    :param expire_delta: The timedelta after which the token will expire. If not provided, default value from settings is used.
    :return: The encoded JWT token as a string
    """
    # Calculate the expiration time
    expire = datetime.utcnow() + (
            expire_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    )

    # Create the JWT payload
    payload = {"exp": expire, "sub": subject}

    # Encode and return the JWT token
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def hash_password(password: str) -> str:
    """Hash the given password.

    :param password: The password to hash
    :return: The hashed password as a string
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify if the given password matches the hashed password.

    :param password: The password to verify
    :param hashed_password: The hashed password to compare with
    :return: True if the password matches, False otherwise
    """
    return pwd_context.verify(password, hashed_password)


async def ensure_admin_exists() -> User:
    admin = await User.get_or_none(username="admin")
    if not admin:
        admin = await User.create(
            username="admin",
            password_hash=hash_password(settings.ADMIN_PASSWORD)
        )
    return admin
