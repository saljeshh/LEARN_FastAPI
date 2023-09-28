from jose import JWTError, jwt
from datetime import datetime, timedelta
import schemas
from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from sqlalchemy.orm import Session
import models
from config import settings

# passing /login url
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET KEY
# Algorithm
# Expiration time

# SECRET_KEY = "9f8ds9fj43kjsdf9gvfjke4fmd098354983490843nfkdsf9834"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 10


def create_access_token(data: dict):
    # make copy of original data its dictinoary
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    # adding new field exp to dictionary
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


# the main goal of verify access token and get current user function is to protect url
# if loggedin user can see some page like profile , home page


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        # type of str id
        id = str(payload.get("user_id"))
        print(type(id))

        if id is None:
            raise credentials_exception

        # pydantic validation so that users dont send any other than token
        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()
    print(user)
    return user
