from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.config import settings
from src.auth.models import User
from src.auth.dtos import UserCreate, UserResponse, Token
from src.auth.controllers import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user
)
from src.customers.models import Customer

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password,
        role="customer"
    )
    
    customer = await Customer.find_one(Customer.email == user_in.email)
    if not customer:
        customer = Customer(name=user_in.name, email=user_in.email)
        await customer.insert()
    new_user.customer = customer
        
    await new_user.insert()
    return new_user

@router.post("/create-staff", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(user_in: UserCreate, current_admin: User = Depends(get_current_user)):
    if current_admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create staff accounts")
        
    if user_in.role == "admin":
        raise HTTPException(status_code=422, detail="Cannot create admin accounts through API")
        
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role
    )
    
    await new_user.insert()
    return new_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
