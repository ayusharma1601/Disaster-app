import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Handle read-only serverless environments (e.g., Vercel Lambda)
# In serverless environments, write permissions are only granted in /tmp
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/disaster_app.db"
else:
    SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./disaster_app.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
