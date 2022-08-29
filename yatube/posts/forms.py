from django import forms
from django.db import models

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма создание поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {
            "text": "Текст",
            "group": "Группа",
            'image': 'Изображение'
        }
        help_texts = {
            'text': 'Введите текст сообщения',
            'group': 'Выберите группу, к которой принадлежит это сообщение',
            'image': 'Выберите своё изображение которым хотите поделиться'
        }

class СommentForm(forms.ModelForm):
    """Форма создание комментария."""
    text = models.TextField('Текст', help_text='Текст нового комментария') 
    class Meta:
        model = Comment
        fields = ('text',)

