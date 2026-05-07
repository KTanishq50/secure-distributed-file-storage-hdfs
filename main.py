from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.db.session import engine
from app.db.models import Base  # ensures models are registered

from app.routes import auth_routes, file_routes
from app.ui.pages import login_page, register_page, teacher_page, student_page

import socket


app = FastAPI()


# ---------------- DB INIT ----------------
@app.on_event("startup")
def startup():
    # create tables if they don't exist
    Base.metadata.create_all(bind=engine)


# ---------------- ROUTES ----------------
app.include_router(auth_routes.router)
app.include_router(file_routes.router)


# ---------------- UI ----------------
@app.get("/")
def root():
    return RedirectResponse(url="/login")


@app.get("/login")
def login_ui():
    return login_page()


@app.get("/register")
def register_ui():
    return register_page()


@app.get("/teacher")
def teacher_ui():
    return teacher_page()


@app.get("/student")
def student_ui():
    return student_page()


# ---------------- DEBUG ----------------
@app.get("/whoami")
def whoami():
    return {"container": socket.gethostname()}