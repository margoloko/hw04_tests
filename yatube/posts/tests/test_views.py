from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms


from ..models import Post, Group

User = get_user_model()
POSTS_PER_PAGE = 11
INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': 'test-slug'})
PROFILE_URL = reverse('posts:profile', kwargs={'username': 'auth'})
POST_CREATE_URL = reverse('posts:post_create')
POST_DETAIL_URL = reverse('posts:post_detail', kwargs={'post_id': '1'})
POST_EDIT_URL = reverse('posts:post_edit', kwargs={'post_id': '1'})


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)
        cls.posts_amount = POSTS_PER_PAGE + 1
        bulk_posts = [
            Post(
                text=f'Тестовая запись {num}',
                author=cls.author,
                group=cls.group
            )
            for num in range(cls.posts_amount)
        ]
        Post.objects.bulk_create(bulk_posts)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Тестирование пагинатора"""
        templates = [INDEX_URL, GROUP_LIST_URL, PROFILE_URL]
        for template in templates:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertEqual(len(response.context['page_obj']), 10)
                response_two = self.authorized_client.get(template + '?page=2')
                self.assertEqual(len(response_two.context['page_obj']), 2)


class PageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.author_test = User.objects.create_user(username='auth-test')
        cls.author_test_client = Client()
        cls.author_test_client.force_login(cls.author_test)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)
        cls.group_test = Group.objects.create(title='Ошибочная группа',
                                              slug='test-slug-test',
                                              description='Неверная группа',)
        cls.post = Post.objects.create(text='Тестовая запись',
                                       author=cls.author,
                                       group=cls.group)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            POST_DETAIL_URL: 'posts/post_detail.html',
            POST_EDIT_URL: 'posts/post_create.html',
            INDEX_URL: 'posts/index.html',
            POST_CREATE_URL: 'posts/post_create.html',
            PROFILE_URL: 'posts/profile.html',
            GROUP_LIST_URL: 'posts/group_list.html'}
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def correct_fields(self, adress):
        response = self.author_client.get(adress)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField, }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def correct_context(self, adress):
        response = self.author_client.get(adress)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовая запись')
        self.assertEqual(first_object.group.title, 'Тестовая группа')
        self.assertEqual(first_object.author.username, 'auth')

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным полями."""
        self.correct_fields(POST_CREATE_URL)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным полями."""
        response = self.author_client.get(POST_EDIT_URL)
        self.assertEqual(response.context['post'].text, 'Тестовая запись')
        self.assertEqual(response.context['post'].group.title,
                         'Тестовая группа')
        self.assertEqual(response.context['post'].author.username, 'auth')
        self.correct_fields(POST_EDIT_URL)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        self.correct_context(INDEX_URL)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_LIST_URL)
        self.assertEqual(response.context['group'].description,
                         'Тестовое описание')
        self.assertEqual(response.context['group'].slug, 'test-slug')
        self.correct_context(GROUP_LIST_URL)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(POST_DETAIL_URL)
        posts = response.context['post_page']
        self.assertEqual(posts.pk, self.post.id)
        self.assertEqual(posts.text, 'Тестовая запись')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.author_client.get(PROFILE_URL)
        self.assertEqual(response.context['post_count'], 1)
        self.correct_context(PROFILE_URL)

    def test_group_page_show_incorrect_context(self):
        """Проверка, что пост не попал в группу,
        для которой не был предназначен."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': 'test-slug-test'})))
        self.assertEqual(response.context['group'].title, 'Ошибочная группа')
        self.assertEqual(response.context['group'].slug, 'test-slug-test')
        self.assertEqual(len(response.context['page_obj']), 0)
