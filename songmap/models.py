from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    hashed_password = Column(String, nullable=False, index=True)
    disabled = Column(Boolean, nullable=False, default=False, index=True)

    approval_ratio = Column(Integer, nullable=False, default=0, index=True)
    influence = Column(Integer, nullable=False, default=0, index=True)

    song_points = relationship("SongPoint", back_populates="owner")
    tracks = relationship("Track", back_populates="owner")


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    artist = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False, index=True)
    spotify_id = Column(String, nullable=True, index=True)

    song_points = relationship("SongPoint", back_populates="song")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=True, index=True)

    owner = relationship("User", back_populates="tracks")
    song_points = relationship("SongPoint", back_populates="track")


class SongPoint(Base):
    __tablename__ = "songpoints"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    likes = Column(Integer, nullable=False, default=0, index=True)
    time_added = Column(DateTime, nullable=False, index=True)
    longitude = Column(Float)
    latitude = Column(Float)
    geo = Column(Geometry(geometry_type="POINT"))

    track = relationship("Track", back_populates="song_points")
    song = relationship("Song", back_populates="song_points")
    owner = relationship("User", back_populates="song_points")
