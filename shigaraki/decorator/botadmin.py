from functools import wraps
from pyrogram.types import Message, CallbackQuery
from shigaraki.admin.roleassign import load_roles

# Define the role hierarchy
ROLE_HIERARCHY = {
    "Botadmin" : ["Hokage", "Jonin" , "Chunin" , "Genin"],
    "Hokage": [],
    "Jonin": ["Hokage"],
    "Chunin": ["Jonin" , "Hokage"],
    "Genin": ["Jonin", "Chunin", "Hokage"]
}

# Helper function to check user roles
def user_has_role(user_id, role):
    roles = load_roles()

    # Check if the user has the required role or any lower role
    allowed_roles = [role] + ROLE_HIERARCHY.get(role, [])
    for allowed_role in allowed_roles:
        allowed_role_key = allowed_role + "s"
        if user_id in roles.get(allowed_role_key, []):
            return True

    return False

# Decorator factory to create role-based decorators
def role_required(role):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message_or_callback, *args, **kwargs):
            user_id = None

            if isinstance(message_or_callback, Message):
                user_id = message_or_callback.from_user.id
            elif isinstance(message_or_callback, CallbackQuery):
                user_id = message_or_callback.from_user.id

            if user_id and user_has_role(user_id, role):
                return await func(client, message_or_callback, *args, **kwargs)
            else:
                return
        return wrapper
    return decorator

# Role-based decorators
hokage = role_required("Hokage")
jonin = role_required("Jonin")
chunin = role_required("Chunin")
genin = role_required("Genin")
botadmin = role_required("Botadmin")
