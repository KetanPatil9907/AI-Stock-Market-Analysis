from django.contrib.auth import get_user_model


class EmailBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username or kwargs.get("email")

        if not email or not password:
            return None

        user_model = get_user_model()

        try:
            user = user_model.objects.get(email__iexact=email)
        except user_model.DoesNotExist:
            return None

        if user.check_password(password) and user.is_active:
            return user

        return None

    def get_user(self, user_id):
        user_model = get_user_model()

        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None