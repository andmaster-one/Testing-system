from django.db import models
from .cache import GROUPS_SET_PK
from django.contrib.auth.models import User

# Группы тестов
class Group(models.Model):
    name = models.CharField(max_length=255, verbose_name='Тест')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"
    
    def save(self):
        super().save()
        pk_group = self.pk
        GROUPS_SET_PK.add(pk_group)
        
    
    def delete(self):
        pk_group = self.pk
        GROUPS_SET_PK.discard(pk_group)
        super().delete()

# Вопросы
class Question(models.Model):
    name = models.CharField(max_length=255, verbose_name='Вопрос')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='questions',verbose_name='группа')

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.name

# Ответы
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='вопрос')
    name = models.CharField(max_length=255, verbose_name='Ответ')
    is_true = models.BooleanField(verbose_name='верный ответ')

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return self.name


class SaveSessionAuthUsers(models.Model):
    """ Класс для сохранения сессии авторизованных пользователей """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session_data = models.TextField(blank=True)

    class Meta:
        verbose_name = "Результат"
        verbose_name_plural = "Результаты"

