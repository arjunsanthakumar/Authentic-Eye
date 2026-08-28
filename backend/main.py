from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt

from database import engine, get_db
from models import Base, User
from schemas import UserCreate, UserLogin

# Create the tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint for user signup. Expects a JSON body with
    {
      "username": "someusername",
      "email": "someone@example.com",
      "password": "SomePassword123!"
    }
    """
    # Check if user with this username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this username or email already exists.")

    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    # Create a new User model instance
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password.decode("utf-8")  # store as string
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"detail": "Signup successful! You can now log in."}

@app.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint for user login. Expects a JSON body with
    {
      "username_or_email": "someone",
      "password": "SomePassword123!"
    }
    """
    user = db.query(User).filter(
        (User.username == login_data.username_or_email) | (User.email == login_data.username_or_email)
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    # Compare the hashed password in the database with the provided password
    if not bcrypt.checkpw(login_data.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    # If you want, you could generate a JWT token or set up a session here
    return {"detail": "Login successful!"}
