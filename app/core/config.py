import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ALGORITHM = "HS256"
    HDFS_BASE_PATH = "/cloud"

settings = Settings()
