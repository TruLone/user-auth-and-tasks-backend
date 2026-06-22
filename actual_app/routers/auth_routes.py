from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import actual_app.database_models as database_models, actual_app.schemas as schemas, actual_app.auth as auth
from actual_app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_input: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(database_models.User).filter_by(username=user_input.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if db.query(database_models.User).filter_by(email=user_input.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if user_input.password != user_input.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    hashed_pwd = auth.hash_password(user_input.password)
    new_user = database_models.User(email = user_input.email, password = hashed_pwd, username = user_input.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(user_input: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(database_models.User).filter_by(username=user_input.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    if not auth.verify_password(user_input.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
