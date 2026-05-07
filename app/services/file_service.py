import uuid
import os
import shutil
import traceback

from app.services.encryption import encrypt, decrypt
from app.services.chunking import split_file, merge_chunks
from app.services.hdfs_client import upload, download, ensure_hdfs_dir
from app.db.models import File, Chunk


BASE = "storage"
CHUNKS = os.path.join(BASE, "chunks")
MERGED = os.path.join(BASE, "merged")

os.makedirs(CHUNKS, exist_ok=True)
os.makedirs(MERGED, exist_ok=True)


# ================= UPLOAD =================
def handle_upload(file_path, filename, user, db):

    file_id = str(uuid.uuid4())
    db_file = None   # prevent crash in except

    try:
        print(f"\n[UPLOAD] Starting upload for {filename}")

        visibility = "teacher" if user.role == "teacher" else "student"
        base_path = f"/cloud/{visibility}/{user.id}/{file_id}"

        # STEP 1: Ensure HDFS directory exists
        print(f"[UPLOAD] Creating HDFS dir → {base_path}")
        ensure_hdfs_dir(base_path)
        print("[UPLOAD] HDFS dir created successfully")

        # STEP 2: Create DB entry
        db_file = File(
            file_id=file_id,
            user_id=user.id,
            filename=filename,
            visibility=visibility,
            status="UPLOADING",
            hdfs_base_path=base_path
        )

        db.add(db_file)
        db.commit()

        # STEP 3: Encrypt
        print("[UPLOAD] Encrypting file...")
        enc_file = encrypt(file_path, user.encryption_key)

        # STEP 4: Split
        print("[UPLOAD] Splitting into chunks...")
        chunks = split_file(enc_file, 200 * 1024, CHUNKS)

        print(f"[UPLOAD] Total chunks → {len(chunks)}")

        # STEP 5: Upload chunks
        for i, chunk_path in enumerate(chunks):
            hdfs_path = f"{base_path}/{os.path.basename(chunk_path)}"

            print(f"[UPLOAD] Uploading chunk {i} → {hdfs_path}")

            upload(chunk_path, hdfs_path)

            db.add(Chunk(
                chunk_id=str(uuid.uuid4()),
                file_id=file_id,
                chunk_index=i,
                hdfs_path=hdfs_path
            ))

            os.remove(chunk_path)

        # cleanup encrypted file
        os.remove(enc_file)

        db_file.status = "READY"
        db.commit()

        print("[UPLOAD] SUCCESS\n")

    except Exception as e:
        print("\n===== UPLOAD ERROR =====")
        print(traceback.format_exc())
        print("========================\n")

        # only update if DB entry exists
        if db_file:
            db_file.status = "FAILED"
            db.commit()

        raise e


# ================= DOWNLOAD =================
def handle_download(file_id, user, db):

    file = db.query(File).filter_by(file_id=file_id).first()
    if not file:
        return None

    # access control
    if user.role != "teacher":
        if file.visibility == "student" and file.user_id != user.id:
            return None

    chunks = (
        db.query(Chunk)
        .filter_by(file_id=file_id)
        .order_by(Chunk.chunk_index)
        .all()
    )

    shutil.rmtree(CHUNKS, ignore_errors=True)
    os.makedirs(CHUNKS, exist_ok=True)

    local_paths = []

    for c in chunks:
        local = os.path.join(CHUNKS, os.path.basename(c.hdfs_path))

        print(f"[DOWNLOAD] Fetching → {c.hdfs_path}")

        download(c.hdfs_path, local)
        local_paths.append(local)

    merged = merge_chunks(local_paths, os.path.join(MERGED, f"{file_id}.enc"))

    final = decrypt(merged, file.user.encryption_key)

    return final, file.filename, local_paths + [merged]