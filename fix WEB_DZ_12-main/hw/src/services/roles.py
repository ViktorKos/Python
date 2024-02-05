from fastapi import Request, Depends, HTTPException, status, FastAPI

from src.entity.models import Role, User
from src.services.auth import auth_service

app = FastAPI()


class RoleAccess:
    """
    Перевіряє, чи користувач має одну з дозволених ролей.
    """

    def __init__(self, allowed_roles: list[Role] = None):
        """
        :param allowed_roles: Список дозволених ролей. Якщо не вказано, всі ролі дозволені.
        """
        self.allowed_roles = allowed_roles or list(Role)

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        Перевіряє, чи користувач має одну з дозволених ролей.

        :param request: Запит FastAPI.
        :param user: Залежність для поточного користувача.
        :raises HTTPException: Викидає HTTPException зі статусом 403, якщо роль відсутня.
        """
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


# Створення екземпляра класу RoleAccess з дозволеними ролями
access_elevated = RoleAccess(allowed_roles=[Role.admin, Role.moderator])


# Використання як декоратора залежності в маршруті
@app.get("/some_protected_route", dependencies=[Depends(access_elevated)])
async def some_protected_route():
    # Ваш код для захищеного маршруту
    return {"message": "You have access to this route!"}
