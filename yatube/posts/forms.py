from django import forms

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
            'group': 'Выберите группу, к которой'
                     'принадлежит это сообщение',
            'image': 'Выберите своё изображение которым'
                     'хотите поделиться'
        }


class CommentForm(forms.ModelForm):
    """Форма создание комментария."""

    class Meta:
        model = Comment
        labels = {"text": "Текст"}
        fields = ('text',)
        help_texts = {
            'text': 'Текст нового комментария'
        }
