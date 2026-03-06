from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def _truncate(password: str) -> str:
    """bcrypt solo soporta hasta 72 bytes; truncamos si es necesario"""
    return password[:72]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_truncate(plain_password), hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(_truncate(password))
