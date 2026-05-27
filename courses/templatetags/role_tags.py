from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_role')
def has_role(user, group_name):
    """
    Перевіряє належність користувача до визначеної групи авторизації.

    Цей фільтр використовується на рівні шаблонів для розмежування прав
    доступу (ACL - Access Control List) між різними типами користувачів
    (наприклад, Студентами та Викладачами).

    Аргументи:
        user: Об'єкт поточного користувача (request.user).
        group_name (str): Назва цільової групи для перевірки.

    Повертає:
        bool: True, якщо користувач належить до вказаної групи
              або є системним адміністратором, інакше False.
    """
    if not user.is_authenticated:
        return False

    # Адміністратор системи автоматично отримує доступ до всіх компонентів
    if user.is_superuser:
        return True

    return user.groups.filter(name=group_name).exists()