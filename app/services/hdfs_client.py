import requests
import os

NAMENODE = "http://namenode:9870/webhdfs/v1"


# ================= ENSURE DIR =================
def ensure_hdfs_dir(hdfs_path):
    url = f"{NAMENODE}{hdfs_path}?op=MKDIRS&user.name=hadoop"

    r = requests.put(url)

    print("[HDFS MKDIR] status:", r.status_code, r.text)  # debug

    if r.status_code not in (200, 201):
        raise Exception(f"MKDIRS failed: {r.status_code} {r.text}")

# ================= UPLOAD =================
def upload(local_path, hdfs_path):
    # Step 1: init create (namenode returns redirect)
    init_url = f"{NAMENODE}{hdfs_path}?op=CREATE&overwrite=true&user.name=hadoop"

    r = requests.put(init_url, allow_redirects=False)
    if r.status_code != 307:
        raise Exception(f"CREATE init failed: {r.status_code} {r.text}")

    upload_url = r.headers.get("Location")
    if not upload_url:
        raise Exception("Missing redirect Location from namenode")

    # FIX: Docker hostname issue
    upload_url = upload_url.replace("localhost", "datanode")

    # Step 2: stream upload to datanode
    with open(local_path, "rb") as f:
        r2 = requests.put(upload_url, data=f)

    if r2.status_code not in (200, 201):
        raise Exception(f"Upload failed: {r2.status_code} {r2.text}")


# ================= DOWNLOAD =================
def download(hdfs_path, local_path):
    url = f"{NAMENODE}{hdfs_path}?op=OPEN&user.name=hadoop"

    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise Exception(f"Download failed: {r.status_code} {r.text}")

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    with open(local_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


# ================= DELETE =================
def delete_hdfs(hdfs_path):
    url = f"{NAMENODE}{hdfs_path}?op=DELETE&recursive=true&user.name=hadoop"

    r = requests.delete(url)
    if r.status_code != 200:
        raise Exception(f"Delete failed: {r.status_code} {r.text}")