# from fastapi import Request, Depends, HTTPException, status, FastAPI
#
# from src.entity.models import Role, User
# from src.services.auth import auth_service
#
# app = FastAPI()
#
#
# class RoleAccess:
#     """
#     Перевіряє, чи користувач має одну з дозволених ролей.
#     """
#
#     def __init__(self, allowed_roles: list[Role] = None):
#         """
#         :param allowed_roles: Список дозволених ролей. Якщо не вказано, всі ролі дозволені.
#         """
#         self.allowed_roles = allowed_roles or list(Role)
#
#     async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
#         """
#         Перевіряє, чи користувач має одну з дозволених ролей.
#
#         :param request: Запит FastAPI.
#         :param user: Залежність для поточного користувача.
#         :raises HTTPException: Викидає HTTPException зі статусом 403, якщо роль відсутня.
#         """
#         if user.role not in self.allowed_roles:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
#
#
# # Створення екземпляра класу RoleAccess з дозволеними ролями
# access_elevated = RoleAccess(allowed_roles=[Role.admin, Role.moderator])
#
#
# # Використання як декоратора залежності в маршруті
# @app.get("/some_protected_route", dependencies=[Depends(access_elevated)])
# async def some_protected_route():
#     # Ваш код для захищеного маршруту
#     return {"message": "You have access to this route!"}
from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        """
        The __init__ function is called when the class is instantiated.
        It allows us to set up or initialize the attributes of our objects.
        In this case, we are initializing a list of allowed roles.

        :param self: Represent the instance of the class
        :param allowed_roles: list[Role]: Define the allowed roles for a user
        :return: Nothing
        :doc-author: Trelent
        """

        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
       The __call__ function is a decorator that allows us to use the class as a function.
           It takes in the request and user, then checks if the user's role is allowed by this route.
           If not, it raises an HTTPException with status code 403 (Forbidden) and detail message &quot;In your eyes (In your eyes), Forbidden love...

       :param self: Access the class attributes
       :param request: Request: Get the request object, which contains information about the http request
       :param user: User: Get the current user
       :return: The decorated function
       :doc-author: Trelent
       """

        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN")
