from pathlib import Path


from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.database.db import get_async_session
from src.repository import users as rep_users
from src.schemas.user import UserSchema, TokenSchema, UserResponseSchema, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request,
                 db: AsyncSession = Depends(get_async_session)):
    """
   The signup function creates a new user in the database.
       It takes an email, username and password as input.
       The function returns the newly created user object.

   :param body: UserSchema: Validate the request body
   :param bg_task: BackgroundTasks: Add a task to the background queue
   :param request: Request: Get the host name
   :param db: AsyncSession: Get a database session
   :return: A new user, but the client does not need it
   :doc-author: Trelent
   """

    existing_user = await rep_users.get_user_by_email(body.email, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = auth_service.get_password_hash(body.password)
    new_user = await rep_users.create_user(body, db)
    # TODO send email notification
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_session)):
    """
   The login function is used to authenticate a user.
   It takes the username and password from the request body,
   and returns an access token if successful.

   :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
   :param db: AsyncSession: Get a database session
   :return: A dict with the access_token and refresh_token
   :doc-author: Trelent
   """

    user = await rep_users.get_user_by_email(body.username, db)
    if user is None or not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong credentials")

    access_token = await auth_service.create_access_token(data={"sub": user.email, "DB-class": "PSQL"})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await rep_users.update_token(user, refresh_token, db)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_async_session)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token,
        a new refresh_token, and the type of token (bearer).

    :param credentials: HTTPAuthorizationCredentials: Get the refresh token from the request header
    :param db: AsyncSession: Connect to the database
    :return: A dict with the access_token, refresh_token and token type
    :doc-author: Trelent
    """

    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await rep_users.get_user_by_email(email, db)

    if user.refresh_token != token:
        await rep_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email, "DB-class": "PSQL"})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await rep_users.update_token(user, refresh_token, db)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


templates_path = Path(__file__).parent.parent / 'services' / 'templates'
templates = Jinja2Templates(directory=str(templates_path))


@router.get('/confirmed_email/{token}', response_class=HTMLResponse)
async def confirmed_email(token: str, request: Request, db: AsyncSession = Depends(get_async_session)):
    """
   The confirmed_email function is called when a user clicks on the link in their email.
       It verifies that the token is valid and then sets the confirmed flag to True for that user.

   :param token: str: Get the token from the url
   :param request: Request: Get the current request object
   :param db: AsyncSession: Get a database session, which is used by the repository functions
   :return: The following:
   :doc-author: Trelent
   """

    email = await auth_service.get_email_from_token(token)
    user = await rep_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return templates.TemplateResponse("email_already_confirmed.html", {"request": request, "user": user})
    await rep_users.confirmed_email(email, db)
    print(user.username)
    # return {"message": "Email confirmed"}
    try:
        # Так й не змiг перебороти, щоб в шаблонi [confirmed_email.html] коректно вiдображався {{ user.username }}
        # хоча вивiд цього параметру перед передачею його до шаблону говорить, що все гаразд...
        return templates.TemplateResponse("confirmed_email.html", {"request": request, "user": user})
    except Exception as err:
        print(f"Error rendering template: {err}")
        raise


@router.post('/request_email', response_class=HTMLResponse)
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_async_session)):
    """
    The request_email function is used to send an email to the user with a link that they can click on
    to confirm their account. The function takes in a RequestEmail object, which contains the email of
    the user who wants to confirm their account. If the user's account has already been confirmed, then
    they are redirected back to the login page and told that they have already confirmed their account.
    If not, then an email is sent out containing a link for them to click on.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the request, which is used to generate a link for
    :param db: AsyncSession: Get the database session from the dependency injection container
    :return: A templateresponse object
    :doc-author: Trelent
    """

    user = await rep_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return templates.TemplateResponse("email_already_confirmed.html", {"request": request, "user": user})
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return templates.TemplateResponse("check_for_confirmation.html", {"request": request, "user": user})
