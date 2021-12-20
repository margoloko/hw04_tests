from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


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
        cls.group_test = Group.objects.create(
            title='Ошибочная группа',
            slug='test-slug-test',
            description='Неверная группа',)
        for post in range(11):
            cls.post = Post.objects.create(
                text='Тестовая запись',
                author=cls.author,
                group=cls.group,
                id=post)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}): 'posts/post_create.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:profile', kwargs={'username':
                    PageTests.author.username}): 'posts/profile.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html'}
# Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным полями."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным полями."""
        response = self.author_client.get(reverse('posts:post_edit',
                                                  kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context страницы index
    # в первом элементе списка содержит ожидаемые значения
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:index'))

        # Взяли первый элемент из списка и проверили,
        # что его содержание совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовая запись')
        self.assertEqual(first_object.author.username, 'auth')
        self.assertEqual(first_object.group.title, 'Тестовая группа')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': 'test-slug'})))
        self.assertEqual(response.context['group'].title, 'Тестовая группа')
        self.assertEqual(response.context['group'].description,
                         'Тестовое описание')
        self.assertEqual(response.context['group'].slug, 'test-slug')
        first_object = response.context['posts'][0]
        self.assertEqual(first_object.text, 'Тестовая запись')
        self.assertEqual(first_object.author.username, 'auth')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        posts = response.context['post_page']
        self.assertEqual(posts.pk, self.post.id)
        self.assertEqual(posts.text, 'Тестовая запись')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        posts = response.context['author']
        self.assertEqual(posts, self.post.author)
        self.assertEqual(response.context['post_count'], 11)
        first_object = response.context['posts'][0]
        self.assertEqual(first_object.text, 'Тестовая запись')
        self.assertEqual(first_object.group.title, 'Тестовая группа')

    def test_paginator(self):
        """Тестирование паджинатора"""
        templates = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})]
        for template in templates:
            response = self.authorized_client.get(template)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка паджинатора: на второй странице должeн быть 1 пост."""
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_group_page_show_incorrect_context(self):
        """Отображение на страницах с переданной группой."""
        url_pages = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': 'auth'}))
        for value in url_pages:
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                first_object = response.context['page_obj'][0]
                post_group_0 = first_object.group.title
                self.assertEqual(post_group_0, self.group.title)
