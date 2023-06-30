from sqlalchemy import create_engine, Integer, Column, Unicode, Time, Enum, DateTime, select, and_, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declarative_base, Session, relationship
import pandas as pd
from config import DB_FILENAME, DB_TBLNAME

engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)
Base = declarative_base() # задание родительского класса, чтобы описывать каждую таблицу как класс

# создание таблиц
class VideoInfo(Base):
    __tablename__ = DB_TBLNAME

    id = Column(Integer, primary_key=True)
    hash = Column(Unicode)
    name = Column(Unicode)
    format = Column(Unicode)
    size = Column(Integer)
    length = Column(Integer)
    videoBitrate = Column(Integer)
    dateCreate = Column(DateTime)
    dateChange = Column(DateTime)
    owner = Column(Unicode)
    path = Column(Unicode)
    frameWidth = Column(Integer)
    frameHeight = Column(Integer)
    fps = Column(Integer)
    frames = Column(Integer)
    videoCodec = Column(Integer)
    colorDepth = Column(Integer)
    colorSpace = Column(Unicode) 
    audio = relationship('AudioInfo', uselist=False, backref=DB_TBLNAME)


    def __repr__(self) -> str:
        return f"""id: {self.id}
        hash: {self.hash}
    name: {self.name}
    format: {self.format}
    size: {self.size}
    length: {self.length}
    videoBitrate: {self.videoBitrate}
    dateCreate: {self.dateCreate}
    dateChange: {self.dateChange}
    owner: {self.owner}
    path: {self.path}
    frameWidth: {self.frameWidth}
    frameHeight: {self.frameHeight}
    fps: {self.fps}
    videoCodec: {self.videoCodec}
    colorDepth: {self.colorDepth}
    colorSpace: {self.colorSpace}
    """

class AudioInfo(Base):
    __tablename__ = f"{DB_TBLNAME}_audio"

    id = Column(Integer, primary_key=True)
    audioBitrate = Column(Integer)
    channels = Column(Integer)
    samplingRate = Column(Integer)
    audioCodec = Column(Integer)
    video_id = mapped_column(ForeignKey(f"{DB_TBLNAME}.id", ondelete='CASCADE'), nullable=False)
    video = relationship("VideoInfo", backref=f"{DB_TBLNAME}_audio")


