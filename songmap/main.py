from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, models, schemas, auth
from .database import SessionLocal, engine
import logging

models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
logger = logging.getLogger("app")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_if_authorized(owner_id, current_id):
    if owner_id != current_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Trying to access unauthorized content",
            headers={"WWW-Authenticate": "Bearer"},
        )


# TODO: MUST HAVE
#  create new user by REGISTRATION ... withou disabled key
#  passwords and everything into secret file, not pushed to git
#  REFACTOR
#  authentication and authorisation
#  do not use id, but name for user
#  instead of auth.get_current_user(token, db) ... implement some faster function that only checks token in db

# TODO: SHOULD DO LATER
#  increment user's approval_ratio when someone likes his song point - AS A BACKGROUND TASK


@app.post("/token/", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth.login_w_username_and_password(form_data.username, form_data.password, db)


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    return auth.get_current_user(token, db)


# USER

@app.post("/users/new/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@app.get("/users/{user_id}/", response_model=schemas.User)
def read_user(user_id: int, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    auth.get_current_user(token, db) # sometimes only checking if logged in
    return crud.get_user(db=db, user_id=user_id)


# SONG

@app.post("/songs/", response_model=schemas.Song)
def create_song(
        song: schemas.SongCreate,
        token: str = Depends(auth.oauth2_scheme),
        db: Session = Depends(get_db)
):
    auth.get_current_user(token, db)
    return crud.create_song(db=db, song=song)


@app.post("/songs/", response_model=List[schemas.Song])
def create_songs(
        songs: List[schemas.SongCreate],
        token: str = Depends(auth.oauth2_scheme),
        db: Session = Depends(get_db)
):
    auth.get_current_user(token, db)
    return crud.create_songs(db=db, songs=songs)


# SONG POINT

@app.post("/users/{owner_id}/songpoints/", response_model=schemas.SongPointResp)
def create_song_point_for_user(
        owner_id: int,
        song_point: schemas.SongPointCreate,
        token: str = Depends(auth.oauth2_scheme),
        db: Session = Depends(get_db)
):
    check_if_authorized(owner_id, auth.get_current_user(token, db).id)
    return crud.create_song_point_for_user(db=db, song_point=song_point, owner_id=owner_id)


@app.post("/users/{owner_id}/songpoints/", response_model=List[schemas.SongPointCreate])
def create_song_points_for_user(
        owner_id: int,
        song_points: List[schemas.SongPointCreate],
        token: str = Depends(auth.oauth2_scheme),
        db: Session = Depends(get_db)
):
    check_if_authorized(owner_id, auth.get_current_user(token, db).id)
    return crud.create_song_points_for_user(db=db, song_points=song_points, owner_id=owner_id)


# TRACK

@app.post("/users/{owner_id}/tracks/", response_model=schemas.TrackResp)
def create_track_w_song_points_for_user(
    owner_id: int,
    track: schemas.TrackCreate,
    song_points: List[schemas.SongPointCreate],
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db)
):
    check_if_authorized(owner_id, auth.get_current_user(token, db).id)
    return crud.create_track_w_song_points_for_user(
        db=db,
        track=track,
        song_points=song_points,
        owner_id=owner_id
    )


@app.get("/users/{owner_id}/tracks/", response_model=List[schemas.TrackResp])
def read_tracks_w_song_points_by_user(
        owner_id: int,
        token: str = Depends(auth.oauth2_scheme),
        db: Session = Depends(get_db)
):
    auth.get_current_user(token, db)
    return crud.get_tracks_w_song_points_by_user(owner_id=owner_id, db=db)


@app.get("/songpoints/", response_model=List[schemas.SongPointResp])
def read_near_song_points(
        longitude: float,
        latitude: float,
        radius: int = 50,
        skip: int = 0,
        limit: int = 100,
        token: str = Depends(auth.oauth2_scheme),
        db: Session = Depends(get_db)
):
    auth.get_current_user(token, db)
    return crud.get_song_points_within_radius(
        db=db,
        longitude=longitude,
        latitude=latitude,
        radius=radius,
        skip=skip,
        limit=limit
    )


# SONGPOINT + TRACK

@app.get("/users/{owner_id}/sat/", response_model=schemas.SongPointsAndTracksResp)
def read_song_points_and_tracks_by_user(
        owner_id: int,
        token: str = Depends(auth.oauth2_scheme),
        db: Session = Depends(get_db)
):
    auth.get_current_user(token, db)
    return crud.get_song_points_and_tracks_by_user(db=db, owner_id=owner_id)


@app.get("/sat/", response_model=schemas.SongPointsAndTracksResp)
def read_song_points_and_tracks_within_radius(
    longitude: float,
    latitude: float,
    radius: int = 50,
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db)
):
    auth.get_current_user(token, db)
    return crud.get_song_points_and_tracks_within_radius(
        db=db,
        longitude=longitude,
        latitude=latitude,
        radius=radius,
        skip=skip,
        limit=limit
    )