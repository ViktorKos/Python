from django.db import models
from django.contrib.auth.models import User


# Модель для представлення інформації про автора
class Author(models.Model):
    fullname = models.CharField(max_length=64, null=False, unique=True)
    born_date = models.CharField(max_length=64)
    born_location = models.CharField(max_length=256)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# Модель для представлення тегів, які можуть бути призначені цитатам
class Tag(models.Model):
    name = models.CharField(max_length=16, null=False, unique=True)

    class Meta:
        verbose_name_plural = "Tags"
        verbose_name = "Tag"


# Модель для представлення цитат, які мають зв'язок із зазначеними авторами та тегами
class Quote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    quote = models.TextField()
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
