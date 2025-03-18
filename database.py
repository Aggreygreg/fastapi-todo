from sqlmodel import create_engine, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")  # Debug
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    print("Initializing database...")  # Debug
    SQLModel.metadata.create_all(engine)
    print("Database initialized.")  # Debug