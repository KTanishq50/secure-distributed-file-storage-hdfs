from sqlalchemy import create_engine, text

engine = create_engine("postgresql://cloud:cloud@localhost:5432/cloudexam")

with engine.connect() as conn:
    print("\n--- USERS ---")
    print(conn.execute(text("SELECT * FROM users")).fetchall())

    print("\n--- FILES ---")
    print(conn.execute(text("SELECT * FROM files")).fetchall())

    print("\n--- CHUNKS ---")
    print(conn.execute(text("SELECT * FROM chunks")).fetchall())