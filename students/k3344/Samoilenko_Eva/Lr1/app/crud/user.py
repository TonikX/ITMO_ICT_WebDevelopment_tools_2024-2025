from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED

from ..models.profile import Profile
from ..models.profileLibrary import ProfileLibrary
from ..schemas.password import ChangePasswordRequest
from ..services.auth import AuthHandler
from ..db.connection import get_session
from ..schemas.user import UserInput, User, UserLogin
from ..services.user_repo import select_all_users, find_user

router = APIRouter()
auth_handler = AuthHandler()


@router.post('/registration')
def register(user: UserInput, session=Depends(get_session)):
    users = select_all_users()

    if any(x.username == user.username for x in users):
        raise HTTPException(status_code=400, detail='Username is taken')

    hashed_pwd = auth_handler.get_password_hash(user.password)

    u = User(username=user.username, password=hashed_pwd, email=user.email)

    session.add(u)
    session.commit()
    session.refresh(u)

    profile = Profile(user_id=u.id, username=u.username)  # создаём пустой профиль
    session.add(profile)
    session.commit()
    session.refresh(profile)

    # Создаём библиотеку, связанную с этим профилем
    library = ProfileLibrary(profile_id=profile.id)
    session.add(library)
    session.commit()
    session.refresh(library)

    return JSONResponse(status_code=HTTP_201_CREATED, content={"message": "User created "
                                                                          "successfully"})


@router.post('/login')
def login(user: UserLogin):
    user_found = find_user(user.username)
    if not user_found:
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    verified = auth_handler.verify_password(user.password, user_found.password)
    if not verified:
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user_found.username)
    return {'token': token}


@router.get('/users/me')
def get_current_user(user: User = Depends(auth_handler.get_current_user)):
    return user


def change_user_password(user_id: int, old_password: str, new_password: str,
                         session=Depends(get_session)):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверим, что старый пароль совпадает с тем, что в базе данных
    if not auth_handler.verify_password(old_password, user.password):
        raise HTTPException(status_code=401,
                            detail="Incorrect old password")

    hashed_new_password = auth_handler.get_password_hash(new_password)

    user.password = hashed_new_password
    session.commit()

    return {"msg": "Password updated successfully"}


@router.put("/users/change_password")
def change_password(
    change_password_request: ChangePasswordRequest,
    current_user: User = Depends(auth_handler.get_current_user),  # Пользователь из токена
    session=Depends(get_session)
):

    return change_user_password(current_user.id, change_password_request.old_password,
                                change_password_request.new_password, session)
