# Реализованные эндпоинты
1) Аутентификация
Сначала нам нужно зарегистрировать пользователя, вызовем данный эндпоинт
http://localhost:8000/register

![html страница](images/register.png)
Далее можно войти в созданный аккаунт введя пароль и логин
http://localhost:8000/login

![html страница](images/login.png)
Для проверки корректности аутентификации перейдём по данному пути
http://localhost:8000/users/me

![html страница](images/users_me.png)
Также была реализована возможность изменения пароля для текущего аккаунта
http://localhost:8000/users/change-password

![html страница](../images/change_password.PNG)
Для пользователей была добавлена возможность вывода всех users из базы данных и получения пользователя по IP
http://localhost:8000/users

![html страница](../images/get_users.PNG)
http://localhost:8000/users/{users_id}

![html страница](../images/user_id.PNG)
Соответствущий код для аутентификации
```python

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session=Depends(get_session)):
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.username == token_data["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm= os.getenv('ALGORITHM'))

def verify_token(token: str):
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@app.get("/users", response_model=List[UserDefault])
def get_users(session=Depends(get_session)):
    return session.exec(select(User)).all()

@app.get("/users/me", response_model=UserDefault)
def get_current_user_info(user: User = Depends(get_current_user)):
    return user

@app.put("/users/change-password")
def change_password(old_password: str, new_password: str, user: User = Depends(get_current_user), session=Depends(get_session)):
    if not user.verify_password(old_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    user.set_password(new_password)
    session.add(user)
    session.commit()
    return {"message": "Password changed"}

@app.get("/user/{user_id}", response_model=User)
def get_user(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/register")
def register_user(user: UserDefault, password: str, session=Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == user.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(**user.dict(), created_at=datetime.utcnow().isoformat())
    new_user.set_password(password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User registered"}

@app.post("/login")
def login(username: str, password: str, session=Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
```