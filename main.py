from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, or_
from database import init_db, engine
from models import User, Todo, UserCreate, UserOut
from auth import hash_password
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