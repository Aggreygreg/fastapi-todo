from fastapi import FastAPI
from database import init_db

app = FastAPI()

# Initialize the database on startup
@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Hello, Todo App! Database connected."}