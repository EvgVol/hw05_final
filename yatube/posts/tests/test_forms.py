from http import HTTPStatus
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Проверяем форму создание и редактирование поста-------------------
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateForm(TestCase):
    """Проверка формы со странице создания поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.user = User.objects.create_user(username='test_name')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user
        )
        cls.form = PostForm()
        cls.form_data = {
            'text': cls.post.text,
            'group': cls.group.id,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    # Анонимный пользователь----------------------------------------
    def test_guest_cant_create_post(self):
        """Гостевой пользователь
        не может создавать посты.
        """
        Post.objects.all().delete()
        response = self.client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=False
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), 0)

    # Авторизованный пользователь-----------------------------------
    def test_check_send_form_post(self):
        """Проверка создание поста авторизованным пользователем."""
        Post.objects.all().delete()
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', args=(self.user.username,)))
        self.assertEqual(post.text, self.form_data['text'])
        self.assertEqual(post.group.id, self.form_data['group'])
        self.assertEqual(post.author, self.user)

    def test_edit_post(self):
        """Проверка формы изменения поста."""
        self.assertEqual(Post.objects.count(), 1)
        group_2 = Group.objects.create(
            title='Заголовок новой группы',
            slug='test_slug2',
            description='Тестовое описание новой группы'
        )
        new_form_data = {
            'text': 'Новый текст',
            'group': group_2.id,
        }
        self.auth_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=new_form_data,
            follow=True,
        )
        post = Post.objects.first()
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, new_form_data['text'])
        self.assertEqual(post.group.id, new_form_data['group'])
        response = self.auth_client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context['page_obj']), 0)
        self.assertEqual(Post.objects.count(), 1)

    def test_image_post_in_context(self):
        """Пост с изображением правильно передается в словарь."""
        # Post.objects.all().delete
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        other_form_data = {
            'group': 'Тестовая группа',
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        url_page = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.post.author,)),
            ('posts:post_detail', (self.post.id,)),
        )
        for name, args in url_page:
            with self.subTest(args=args):
                response = self.client.post(
                    reverse(name, args=args),
                    data=other_form_data,
                    follow=True
                )
        post = Post.objects.first()
        self.assertFormError(
            response,
            'post',
            'image',
            None,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)
