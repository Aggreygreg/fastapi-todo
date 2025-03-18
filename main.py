from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select, or_
from database import init_db, engine
from models import User, Todo, UserCreate, UserOut, Login, Token
from auth import hash_password, verify_password, create_access_token
from contextlib import asynccontextmanager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello, Todo App! Database connected."}

@app.post("/register", response_model=UserOut)
def register_user(user: UserCreate):
    """Register a new user."""
    try:
        with Session(engine) as session:
            logger.info(f"Registering user: {user.username}")
            existing_user = session.exec(
                select(User).where(
                    or_(User.username == user.username, User.email == user.email)
                )
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username or email already taken")

            hashed_password = hash_password(user.password)
            db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            logger.info(f"User registered: {db_user.id}")
            return UserOut(id=db_user.id, username=db_user.username, email=db_user.email)
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and return an access token."""
    try:
        with Session(engine) as session:
            logger.info(f"Login attempt for user: {form_data.username}")
            user = session.exec(
                select(User).where(User.username == form_data.username)
            ).first()
            if not user or not verify_password(form_data.password, user.hashed_password):
                raise HTTPException(status_code=401, detail="Incorrect username or password")

            access_token = create_access_token(data={"sub": user.username})
            logger.info(f"Token issued for user: {user.username}")
            return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")