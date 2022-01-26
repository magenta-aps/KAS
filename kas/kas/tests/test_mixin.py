from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


def create_admin_user():
    try:
        get_user_model().objects.create(username='admin')
    except IntegrityError:
        pass
