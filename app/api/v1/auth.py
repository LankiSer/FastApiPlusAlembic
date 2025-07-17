from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.shemas.user import UserCreate
from app.shemas.token import Token
from app.core.security import get_password_hash, create_access_token, verify_password
from app.db.session import get_db
from app.db.models.user import User
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",  # Все роуты будут начинаться с /api/v1/auth
    tags=["auth"]
)

# Регистрация пользователя
@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": token, "token_type": "bearer"}

# Логин пользователя
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# Healthcheck роут
@router.get("/health", tags=["health"])
async def healthcheck():
    """Проверка работоспособности сервиса."""
    return {"status": "ok"}