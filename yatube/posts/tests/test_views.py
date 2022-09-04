from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.cache import cache

from ..models import Comment, Follow, Group, Post
from ..forms import CommentForm, PostForm

User = get_user_model()

POSTS_COUNT = 13


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Описание тестовой группы',
        )
        cls.user = User.objects.create_user(username='Test_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            pub_date='2022-08-23 9-00-00'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def context_post_and_page(self, response, flag=False):
        """Проверка поста на странице."""
        if flag is True:
            post = response.context['post']
        else:
            post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.image, self.post.image)

    def test_context_post_in_page_index(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.context_post_and_page(response)

    def test_context_post_in_page_group(self):
        """Шаблон group_list сформирован с правильным контекстом
        отфильтрованных по группе.
        """
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.context_post_and_page(response)
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(response.context['group'], self.group)

    def test_post_not_used_in_other_group(self):
        """Пост не используется в чужой группе."""
        Post.objects.all().delete()
        Post.objects.create(
            author=self.user,
            text='Тестовый текст_2',
            group=self.group
        )
        group_new = Group.objects.create(
            title='Тестовая группа_2',
            slug='test_slug_2',
            description='Описание тестовой группы_2'
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(group_new.slug,)))
        self.assertEqual(len(response.context['page_obj']), 0)
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_context_post_in_page_profile(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=(self.user.username,)))
        self.context_post_and_page(response)
        self.assertEqual(
            response.context['author'], self.post.author
        )

    def test_context_post_in_page_post_detail(self):
        """Шаблон post_detail сформирован
        с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post.id,)))
        self.context_post_and_page(response, True)

    def test_context_post_in_page_edit_and_create_post(self):
        """Шаблон create_post сформирован с
        правильным контекстом.
        """
        url_page = (
            ('posts:post_edit', (self.post.id,)),
            ('posts:post_create', None,)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for name, args in url_page:
            with self.subTest(name=name):
                response = self.authorized_client.get(
                    reverse(name, args=args)
                )
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'], PostForm
                )
                for value, expect in form_fields.items():
                    with self.subTest(value=value):
                        field_type = (
                            response
                            .context
                            .get('form')
                            .fields
                            .get(value)
                        )
                        self.assertIsInstance(field_type, expect)


class PaginatorViewsTest(TestCase):
    """Тестируем работу паджинатора."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.author = User.objects.create_user(
            username="test_author",
        )
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.posts = [
            Post(
                text=f'Тестовый пост {post}',
                author=cls.author,
                group=cls.group,
            )
            for post in range(POSTS_COUNT)
        ]
        cls.follower = User.objects.create_user(
            username="test_follower",
        )
        cls.following = Follow.objects.create(
            user=cls.follower,
            author=cls.author,
        )

        Post.objects.bulk_create(cls.posts)
        cls.all_pages_with_paginator = (
            ('posts:index', None),
            ('posts:group_list', (cls.group.slug,)),
            ('posts:profile', (cls.author.username,)),
            ('posts:follow_index', None)
        )
        cls.lot_post = (
            ('?page=1', settings.CONST_TEN),
            ('?page=2', POSTS_COUNT - settings.CONST_TEN)
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

    def test_paginator_on_page(self):
        """Паджинатор показывает по 10 постов на страницах
        index, group_list, profile, follow_index
        """
        for name, args in self.all_pages_with_paginator:
            with self.subTest(args=args):
                for numder_page, count_posts in self.lot_post:
                    with self.subTest(numder_page=numder_page):
                        response = self.follower_client.get(
                            reverse(name, args=args) + numder_page
                        )
                        self.assertEqual(
                            len(response.context.get('page_obj')
                                .object_list), count_posts)


class TestComments(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test_user')
        cls.comment_user = User.objects.create_user(
            username='TestCommentUser'
        )
        cls.post = Post.objects.create(
            text='БЛА-БЛА-БЛА',
            author=cls.user,
        )
        cls.url_comment = reverse(
            'posts:add_comment',
            args=(cls.post.id,)
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_authorized(self):
        """Проверяем, что авторизованный пользователь может
        комментировать.
        """
        Comment.objects.all().delete()
        response = self.authorized_client.post(
            self.url_comment,
            {'text': 'test comment'},
            follow=True)
        comment_one = Comment.objects.first()
        self.assertContains(response, 'test comment')
        self.assertEqual(Comment.objects.count(), 1)
        self.assertIsInstance(
            response.context['form'], CommentForm
        )
        self.assertEqual(comment_one.post.author, self.post.author)
        self.assertEqual(comment_one.post.text, self.post.text)
        self.assertEqual(comment_one.post, self.post)

    def test_comment_noauthorized(self):
        """Проверяем, что неавторизованный пользователь не может
        комментировать.
        """
        self.client.post(
            self.url_comment,
            {'text': 'test comment'},
            follow=True)
        Comment.objects.first()
        self.assertEqual(Comment.objects.count(), 0)


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='text'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Главная страница работает с 20 секундным кешем."""
        self.authorized_client.get(
            reverse('posts:index')
        )
        Post.objects.create(
            author=self.user,
            text='текст 1',
            group=self.group)
        response1 = self.authorized_client.get(
            reverse('posts:index')
        )
        Post.objects.all().delete()
        response2 = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(response1.content, response3.content)


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test_author')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test_slug',
            description='Test description'
        )
        cls.follower = User.objects.create_user(
            username='Test_user')
        cls.following = Follow.objects.create(
            user=cls.follower,
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)

    def test_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей.
        """
        Follow.objects.all().delete()
        follow_count1 = Follow.objects.count()
        follow = Follow.objects.filter(
            author=self.user,
            user=self.follower
        )
        self.assertEqual(follow.first(), None)
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                args=(self.user.username,)
            )
        )
        follow_count2 = Follow.objects.count()
        self.assertEqual(follow_count2, follow_count1 + 1)
        follow = Follow.objects.first()
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(follow.author, self.user)
        self.assertEqual(follow.user, self.follower)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unfollow(self):
        """Авторизованный пользователь может
        отписаться от других пользователей.
        """
        self.assertEqual(self.user.following.count(), 1)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                args=(self.user.username,)
            )
        )
        self.assertEqual(self.user.following.count(), 0)

    def test_follow_index(self):
        """Новая запись пользователя появляется в ленте фаловера."""
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        new_post = Post.objects.create(
            author=self.user,
            text='Новый пост'
        )
        response = self.authorized_client.get(reverse(
            'posts:follow_index')
        )
        self.assertEqual(new_post, response.context['page_obj'][0])
        self.assertEqual(len(
            response.context.get('page_obj').object_list), 1
        )
        post = response.context['post']
        self.assertEqual(post.text, new_post.text)
        self.assertEqual(post.author, new_post.author)

    def test_not_follow_index(self):
        """Новая запись пользователя не появляется в ленте
        не фаловера.
        """
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        new_user = User.objects.create_user(
            username='New_user'
        )
        Post.objects.create(
            author=new_user,
            text='Новый пост'
        )
        response = self.authorized_client.get(reverse(
            'posts:follow_index')
        )
        self.assertEqual(len(
            response.context['page_obj']), 0
        )

    def test_following_self(self):
        """Проверка, что нельзя подписаться на самого себя."""
        Follow.objects.all().delete()
        self.assertEqual(Follow.objects.all().count(), 0)

        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                args=(self.follower.username,)
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)
        self.authorized_client.get(reverse(
            'posts:profile_follow', args=(self.user.username,))
        )
        self.assertEqual(Follow.objects.all().count(), 1)
