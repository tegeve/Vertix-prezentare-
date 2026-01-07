from accounts.models import User

def is_admin(user) -> bool:
    return user.is_authenticated and user.role == User.Role.ADMIN

def is_manager(user) -> bool:
    return user.is_authenticated and user.role == User.Role.MANAGER

def is_admin_or_manager(user) -> bool:
    return is_admin(user) or is_manager(user)

def is_technician(user) -> bool:
    return user.is_authenticated and user.role == User.Role.TEHNICIAN

def is_client(user) -> bool:
    return user.is_authenticated and user.role == User.Role.CLIENT

def can_view_document(user, doc) -> bool:
    if not user.is_authenticated:
        return False

    if is_admin_or_manager(user):
        return True

    if is_technician(user) and doc.technicians.filter(pk=user.pk).exists():
        return True

    # client: doar FINAL și doar dacă e documentul lui
    if is_client(user) and doc.status == doc.Status.FINAL and doc.client_user_id == user.id:
        return True

    return False

def can_edit_document(user, doc) -> bool:
    if not user.is_authenticated:
        return False

    if is_admin_or_manager(user):
        return True

    if is_technician(user) and doc.technicians.filter(pk=user.pk).exists():
        return doc.status in {doc.Status.DRAFT, doc.Status.IN_PROGRESS, doc.Status.READY}

    return False

def can_close_document(user, doc) -> bool:
    return is_admin_or_manager(user)
