from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import time

DATABASE_URL = "postgresql://cloud:cloud@db:5432/cloudexam"

# ---------------- DB CONNECTION (RETRY) ----------------
engine = None

for i in range(10):
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True
        )

        # test connection
        conn = engine.connect()
        conn.close()

        print("Connected to PostgreSQL")
        break

    except Exception as e:
        print(f"Waiting for DB... ({i+1}/10)")
        time.sleep(2)

if engine is None:
    raise Exception("Could not connect to PostgreSQL")


# ---------------- SESSION ----------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


# ---------------- DEPENDENCY ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()