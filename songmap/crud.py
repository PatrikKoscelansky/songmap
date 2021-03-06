from typing import Optional, List

from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, schemas, auth


# USER
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).all()

# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    password_hash = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# SONG

def create_song(db: Session, song: schemas.SongCreate):
    db_song = models.Song(artist=song.artist, title=song.title, spotify_id=song.spotify_id)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def create_songs(db: Session, songs: List[schemas.SongCreate]):
    db_songs = []
    for song in songs:
        db_song = create_song(db, song)
        db_songs.append(db_song)
    return db_songs


# TODO: consider creating also song here
def create_song_point_for_user(
        db: Session, song_point: schemas.SongPointCreate, owner_id: int, track_id: Optional[int] = None
):
    geo = 'POINT({} {})'.format(song_point.longitude, song_point.latitude)
    db_song_point = models.SongPoint(
        longitude=song_point.longitude,
        latitude=song_point.latitude,
        geo=geo,
        time_added=song_point.time_added,
        song_id=song_point.song_id,
        owner_id=owner_id,
        track_id=track_id
    )

    db.add(db_song_point)
    db.commit()
    db.refresh(db_song_point)
    return db_song_point


def create_song_points_for_user(
    db: Session, song_points: List[schemas.SongPointCreate], owner_id: int
):
    db_song_points = []
    for song_point in song_points:
        db_song_point = create_song_point_for_user(db, song_point, owner_id)
        db_song_points.append(db_song_point)
    return db_song_points


def get_song_points_within_radius(db: Session, longitude: float, latitude: float, radius: int = 50, skip: int = 0, limit: int = 100):
    geo = 'POINT({} {})'.format(longitude, latitude)
    return db.query(models.SongPoint).filter(func.ST_DistanceSphere(models.SongPoint.geo, geo) < radius).offset(skip).limit(limit).all()


def create_track(db: Session, track: schemas.TrackCreate, owner_id: int):
    db_track = models.Track(name=track.name, owner_id=owner_id)
    db.add(db_track)
    db.commit()
    db.refresh(db_track)
    return db_track


def get_tracks_w_song_points_by_user(db: Session, owner_id: int):
    return db.query(models.Track).filter(models.Track.owner_id == owner_id).all()


def create_track_w_song_points_for_user(
        db: Session,
        track: schemas.TrackCreate,
        song_points: List[schemas.SongPointCreate],
        owner_id: int
):
    db_track = models.Track(name=track.name, owner_id=owner_id)
    db.add(db_track)
    db.commit()
    db.refresh(db_track)

    for song_point in song_points:
        geo = 'POINT({} {})'.format(song_point.longitude, song_point.latitude)
        db_song_point = models.SongPoint(
            longitude=song_point.longitude,
            latitude=song_point.latitude,
            geo=geo,
            time_added=song_point.time_added,
            song_id=song_point.song_id,
            owner_id=owner_id,
            track_id=db_track.id
        )
        db.add(db_song_point)

    db.commit()
    db.refresh(db_track)

    return db_track


def get_song_points_and_tracks_by_user(db: Session, owner_id: int):
    db_tracks = get_tracks_w_song_points_by_user(db=db, owner_id=owner_id)
    db_song_points = db.query(models.SongPoint).filter(models.SongPoint.owner_id == owner_id, models.SongPoint.track_id == None).all()

    return {
        "song_points": db_song_points,
        "tracks": db_tracks
    }


def get_song_points_and_tracks_within_radius(
        db: Session,
        longitude: float,
        latitude: float,
        radius: int = 50,
        skip: int = 0,
        limit: int = 100
):
    geo = 'POINT({} {})'.format(longitude, latitude)

    # models.SongPoint.track_id == None,
    db_song_points_all = db.query(models.SongPoint).filter(
        func.ST_DistanceSphere(models.SongPoint.geo, geo) < radius
    ).offset(skip).limit(limit).all()

    db_song_points = [sp for sp in db_song_points_all if sp.track_id == None]

    db_song_points_from_tracks = [sp for sp in db_song_points_all if sp.track_id != None]
    relevant_track_ids = set([sp.track_id for sp in db_song_points_from_tracks])

    db_tracks = []
    for track_id in relevant_track_ids:
        db_track = db.query(models.Track).filter(models.Track.id == track_id).first()
        db_tracks.append(db_track)

    return {
        "song_points": db_song_points,
        "tracks": db_tracks
    }
