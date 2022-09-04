from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StatusURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_username'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый тест',
            group=cls.group
        )
        cls.not_an_author = User.objects.create_user(
            username='No_author'
        )
        cls.all_pages = (
            (
                'posts:index',
                None,
                '/',
            ),
            (
                'posts:group_list',
                (cls.group.slug,),
                f'/group/{cls.group.slug}/',
            ),
            (
                'posts:profile',
                (cls.user.username,),
                f'/profile/{cls.user.username}/',
            ),
            (
                'posts:post_detail',
                (cls.post.id,),
                f'/posts/{cls.post.id}/',
            ),
            (
                'posts:post_create',
                None,
                '/create/',
            ),
            (
                'posts:post_edit',
                (cls.post.id,),
                f'/posts/{cls.post.id}/edit/',
            ),
            (
                'posts:add_comment',
                (cls.post.id,),
                f'/posts/{cls.post.id}/comment/',
            ),
            (
                'posts:follow_index',
                None,
                '/follow/',
            ),
            (
                'posts:profile_follow',
                (cls.user.username,),
                f'/profile/{cls.user.username}/follow/',
            ),
            (
                'posts:profile_unfollow',
                (cls.user.username,),
                f'/profile/{cls.user.username}/unfollow/',
            ),

        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author = Client()
        self.not_author.force_login(self.not_an_author)

    def test_unexisting_page(self):
        """Провека несуществующей страницы."""
        response = self.client.get('/unexisting/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_public_pages_for_guest_client(self):
        """Url-адрес доступен анонимному пользователю
        с проверкой перенаправлению.
        """
        for name, args, url in self.all_pages:
            with self.subTest(args=args):
                reverse_name = reverse(name, args=args)
                redirect_to_login = reverse('users:login')
                if name in ('posts:post_create',
                            'posts:post_edit',
                            'posts:add_comment',
                            'posts:follow_index',
                            'posts:profile_follow',
                            'posts:profile_unfollow'):
                    response = self.client.get(reverse_name)
                    self.assertEqual(
                        response.status_code, HTTPStatus.FOUND
                    )
                    self.assertRedirects(
                        response,
                        f'{redirect_to_login}?next={reverse_name}'
                    )
                else:
                    response = self.client.get(reverse_name)
                    self.assertEqual(
                        response.status_code, HTTPStatus.OK
                    )

    def test_public_pages_for_author_post(self):
        """Все url-адресы доступны автору поста."""
        for name, args, url in self.all_pages:
            with self.subTest(args=args):
                reverse_name = reverse(name, args=args)
                if name == 'posts:add_comment':
                    response = self.authorized_client.get(
                        reverse_name
                    )
                    self.assertEqual(
                        response.status_code, HTTPStatus.FOUND
                    )
                    self.assertRedirects(
                        response,
                        reverse(
                            'posts:post_detail',
                            args=(self.post.id,)
                        )
                    )
                elif name == 'posts:profile_unfollow':
                    response = self.authorized_client.get(
                        reverse_name
                    )
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND
                    )
                elif name == 'posts:profile_follow':
                    response = self.authorized_client.get(
                        reverse_name
                    )
                    self.assertEqual(
                        response.status_code, HTTPStatus.FOUND
                    )
                    self.assertRedirects(
                        response,
                        reverse(
                            'posts:profile',
                            args=(self.user.username,)
                        )
                    )
                else:
                    response = self.authorized_client.get(
                        reverse_name
                    )
                    self.assertEqual(
                        response.status_code, HTTPStatus.OK
                    )

    def test_pages_for_guest_client(self):
        """Все url-адрес|posts_edit доступен не автору поста
        c post_edit редирект на post_detail.
        """
        for name, args, url in self.all_pages:
            with self.subTest(args=args):
                reverse_name = reverse(name, args=args)
                if name in ('posts:post_edit', 'posts:add_comment'):
                    response = self.not_author.get(reverse_name)
                    self.assertEqual(
                        response.status_code, HTTPStatus.FOUND
                    )
                    redirect_to_post_detail = reverse(
                        'posts:post_detail', args=(self.post.id,)
                    )
                    self.assertRedirects(
                        response, redirect_to_post_detail
                    )
                elif name in ('posts:profile_follow',
                              'posts:profile_unfollow'):
                    response = self.not_author.get(reverse_name)
                    self.assertEqual(
                        response.status_code, HTTPStatus.FOUND
                    )
                else:
                    response = self.not_author.get(reverse_name)
                    self.assertEqual(
                        response.status_code, HTTPStatus.OK
                    )

    def test_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_all_pages = (
            (
                ('posts:index'),
                (None),
                ('posts/index.html')
            ),
            (
                ('posts:group_list'),
                (self.group.slug,),
                ('posts/group_list.html')
            ),
            (
                ('posts:profile'),
                (self.user.username,),
                ('posts/profile.html')
            ),
            (
                ('posts:post_detail'),
                (self.post.id,),
                ('posts/post_detail.html')
            ),
            (
                ('posts:post_create'),
                None,
                ('posts/create_post.html')
            ),
            (
                ('posts:post_edit'),
                (self.post.id,),
                ('posts/create_post.html')
            ),
            (
                ('posts:follow_index'),
                None,
                ('posts/follow.html')
            ),
        )
        for name, args, template in template_all_pages:
            with self.subTest(args=args):
                response = self.authorized_client.get(
                    reverse(name, args=args)
                )
                self.assertTemplateUsed(response, template)
