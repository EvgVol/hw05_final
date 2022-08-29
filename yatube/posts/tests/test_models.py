from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.text = 'Гиппопотомонстросескипедалофобия'
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.text,
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        field_str = {
            str(self.post): self.text[:15],
            str(self.group): self.group.title,
        }
        for field, expected_value in field_str.items():
            with self.subTest(expected_value=expected_value):
                self.assertEqual(field, expected_value)

    def test_help_text_group(self):
        """help_text группы поля title совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field)
                        .help_text, expected_value)

    def test_verbose_name_group_and_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group_verboses = {
            'title': 'Название',
            'slug': 'URL',
            'description': 'Описание',
        }
        post_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in post_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field)
                        .verbose_name, expected_value)

        for field, expected_value in group_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field)
                        .verbose_name, expected_value)
