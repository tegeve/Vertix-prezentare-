def is_staff_user(user):
    # adaptează la modelul tău (role == ADMIN/MANAGER etc.)
    return getattr(user, "role", None) in {"ADMIN", "MANAGER"}


def message_queryset_for_user(qs, user):
    if is_staff_user(user):
        return qs  # vede PUBLIC + INTERNAL
    return qs.filter(visibility="PUBLIC")  # client vede doar public
