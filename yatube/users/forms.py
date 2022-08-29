from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    """Форма для регистрации нового пользователя."""

    class Meta:
        """Информация о созданном новом пользователе."""

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "username": "Ник",
            "email": "E-Mail"
        }
