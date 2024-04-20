from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string
from django.conf import settings


def get_admin_only_models_content_types() -> list[ContentType]:
    """
    Return a list of content types for admin only models as defined
    in the `ADMIN_ONLY_MODELS` setting.
    """
    admin_only_models = getattr(settings, "ADMIN_ONLY_MODELS", [])
    content_types = []
    for model in admin_only_models:
        content_type = ContentType.objects.get_for_model(import_string(model))
        content_types.append(content_type)
    return content_types


def get_permissions_for_admin_only_models() -> list[Permission]:
    """
    Return a list of all permissions for admin only models
    as defined in the `ADMIN_ONLY_MODELS` setting.
    """
    content_types = get_admin_only_models_content_types()
    permissions = Permission.objects.filter(content_type__in=content_types)
    return permissions


def remove_permissions_for_admin_only_models(user) -> None:
    """
    Remove permissions for admin only models defined in the
    `ADMIN_ONLY_MODELS` setting, from the given user.
    """
    permissions = get_permissions_for_admin_only_models()
    user.user_permissions.remove(*permissions)


def add_permissions_for_admin_only_models(user) -> None:
    """
    Add permissions for admin only models defined in the
    `ADMIN_ONLY_MODELS` setting, to the given user.
    """
    permissions = get_permissions_for_admin_only_models()
    user.user_permissions.add(*permissions)


def update_admin_only_perms_on_user(user) -> None:
    """
    Update the permissions for admin only models on the given user.

    Removes permissions for admin only models if the user is not an admin,
    otherwise adds them.

    :param user: The user to update permissions for.
    """
    if user.is_admin:
        add_permissions_for_admin_only_models(user)
    else:
        remove_permissions_for_admin_only_models(user)
    return None
