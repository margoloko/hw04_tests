from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth import get_user_model

from .test_models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
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
        cls.post = Post.objects.create(
            text='Тестовая группа',
            author=cls.author,
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
# Создаем второй клиент
        self.authorized_client = Client()
# Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_url_exists_for_any_user(self):
        """Страницы с доступом для любого пользователя."""
        template_urls = [
            '/profile/auth/',
            '/posts/1/',
            '/',
            '/group/test-slug/']
        for adress in template_urls:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Страница unexisting_page/ вернёт ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_exists_at_desired_location_authorized(self):
        """Страница create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница posts/edit/ доступна автору."""
        response = StaticURLTests.author_client.get('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_url_name = {
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
            '/posts/1/edit/': 'posts/post_create.html',
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html'}
        for adress, template in template_url_name.items():
            with self.subTest(adress=adress):
                response = StaticURLTests.author_client.get(adress)
                self.assertTemplateUsed(response, template)
