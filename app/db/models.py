from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    encryption_key = Column(String, nullable=False)

    files = relationship("File", back_populates="user", cascade="all, delete")


class File(Base):
    __tablename__ = "files"

    file_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    filename = Column(String, nullable=False)
    visibility = Column(String, nullable=False)
    status = Column(String, nullable=False)

    hdfs_base_path = Column(String, nullable=False)

    user = relationship("User", back_populates="files")
    chunks = relationship("Chunk", back_populates="file", cascade="all, delete")


class Chunk(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String, primary_key=True)
    file_id = Column(String, ForeignKey("files.file_id"), nullable=False)

    chunk_index = Column(Integer, nullable=False)
    hdfs_path = Column(String, nullable=False)

    file = relationship("File", back_populates="chunks")