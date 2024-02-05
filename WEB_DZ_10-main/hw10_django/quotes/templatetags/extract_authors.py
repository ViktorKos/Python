from django import template
from ..models import Author

register = template.Library()


@register.filter(name='author')
def get_author(author):
    # Використовуємо try-except для безпечного доступу до id об'єкта
    try:
        author_id = author.id
    except AttributeError:
        author_id = None

    # Використовуємо метод first() замість filter, щоб отримати перший об'єкт або None
    author_instance = Author.objects.filter(id=author_id).first()

    # Перевіряємо, чи існує автор, перед тим як отримати fullname
    if author_instance:
        return author_instance.fullname

    # Повертаємо порожній рядок, якщо автор не знайдений
    return ''
