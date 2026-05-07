from fastapi import APIRouter, UploadFile, File as FastAPIFile, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import shutil, os

from app.services.file_service import handle_upload, handle_download
from app.services.hdfs_client import delete_hdfs
from app.core.auth import get_current_user
from app.db.session import get_db
from app.db.models import File as DBFile, User

router = APIRouter()

TEMP = "storage/tmp"
os.makedirs(TEMP, exist_ok=True)


def cleanup(paths):
    for p in paths:
        if os.path.exists(p):
            os.remove(p)


# ================= UPLOAD =================
@router.post("/upload")
def upload(
    file: UploadFile = FastAPIFile(...),
    user_data=Depends(get_current_user),
    db=Depends(get_db)
):

    user = db.query(User).filter(User.id == user_data["user_id"]).first()

    if not user:
        raise HTTPException(401, "User not found")

    if not user.encryption_key:
        raise HTTPException(500, "Missing encryption key (re-register user)")

    path = os.path.join(TEMP, file.filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        handle_upload(path, file.filename, user, db)
    except Exception as e:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(500, f"upload failed: {str(e)}")

    if os.path.exists(path):
        os.remove(path)

    return {"msg": "uploaded"}


# ================= DOWNLOAD (ID) =================
@router.get("/download")
def download(
    file_id: str,
    bg: BackgroundTasks,
    user_data=Depends(get_current_user),
    db=Depends(get_db)
):

    user = db.query(User).filter(User.id == user_data["user_id"]).first()

    result = handle_download(file_id, user, db)
    if not result:
        raise HTTPException(404, "File not found")

    final, filename, temps = result
    bg.add_task(cleanup, temps + [final])

    return FileResponse(final, filename=filename)


# ================= DOWNLOAD BY NAME =================
@router.get("/download-by-name")
def download_by_name(
    filename: str,
    bg: BackgroundTasks,
    user_data=Depends(get_current_user),
    db=Depends(get_db)
):

    user = db.query(User).filter(User.id == user_data["user_id"]).first()

    # FIX: use visibility instead of file_type
    file = db.query(DBFile).filter_by(
        filename=filename,
        visibility="teacher"
    ).first()

    if not file:
        raise HTTPException(404, "Teacher file not found")

    result = handle_download(file.file_id, user, db)

    if not result:
        raise HTTPException(403, "Access denied")

    final, filename, temps = result
    bg.add_task(cleanup, temps + [final])

    return FileResponse(final, filename=filename)


# ================= DELETE =================
@router.delete("/delete")
def delete(
    file_id: str,
    user_data=Depends(get_current_user),
    db=Depends(get_db)
):

    user = db.query(User).filter(User.id == user_data["user_id"]).first()

    file = db.query(DBFile).filter_by(file_id=file_id).first()
    if not file:
        raise HTTPException(404, "File not found")

    if user.role != "teacher" and file.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    delete_hdfs(file.hdfs_base_path)

    db.delete(file)
    db.commit()

    return {"msg": "deleted"}


# ================= STUDENT FILES =================
@router.get("/my-files")
def my_files(
    user_data=Depends(get_current_user),
    db=Depends(get_db)
):

    user_id = user_data["user_id"]

    # FIX: removed file_type (does NOT exist in model)
    files = db.query(DBFile).filter_by(
        user_id=user_id
    ).all()

    return [
        {"file_id": f.file_id, "filename": f.filename}
        for f in files
    ]


# ================= TEACHER FILES =================
@router.get("/all-files")
def all_files(
    user_data=Depends(get_current_user),
    db=Depends(get_db)
):

    if user_data["role"] != "teacher":
        raise HTTPException(403, "Only teacher allowed")

    return [
        {
            "file_id": f.file_id,
            "filename": f.filename,
            "visibility": f.visibility
        }
        for f in db.query(DBFile).all()
    ]