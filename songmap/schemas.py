from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    influence: int
    approval_ratio: int
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True


class UserInDB(User):
    disabled: Optional[bool] = None
    hashed_password: str


class SongBase(BaseModel):
    artist: str
    title: str
    spotify_id: str


class SongCreate(SongBase):
    pass


class Song(SongBase):
    id: int

    class Config:
        orm_mode = True


class SongPointBase(BaseModel):
    song_id: int
    longitude: float
    latitude: float
    time_added: datetime


class SongPointCreate(SongPointBase):
    pass


class SongPointResp(SongPointBase):
    owner_id: int
    likes: int
    song: Song

    class Config:
        orm_mode = True


class SongPoint(SongPointBase):
    geo: str
    owner_id: int
    track_id: Optional[int] = None
    likes: int

    class Config:
        orm_mode = True


class TrackBase(BaseModel):
    name: Optional[str] = None


class TrackCreate(TrackBase):
    pass


class TrackResp(TrackBase):
    id: int
    owner_id: int
    song_points: List[SongPointResp] = []

    class Config:
        orm_mode = True


class Track(TrackBase):
    id: int
    owner_id: int
    song_points: List[SongPoint] = []

    class Config:
        orm_mode = True


class SongPointsAndTracksResp(BaseModel):
    song_points: List[SongPointResp]
    tracks: List[TrackResp]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None