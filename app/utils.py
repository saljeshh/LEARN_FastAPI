from passlib.context import CryptContext


# for hasing ...

# telling passlib what is the default algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hased_password):
    return pwd_context.verify(plain_password, hased_password)
