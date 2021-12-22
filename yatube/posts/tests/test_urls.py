from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth import get_user_model

from .test_models import Post, Group

User = get_user_model()
PROFILE = '/profile/auth/'
POST_DETAIL = '/posts/1/'
INDEX = '/'
GROUP_LIST = '/group/test-slug/'
POST_EDIT = '/posts/1/edit/'
POST_CREATE = '/create/'
LOGIN_ADRESS = '/auth/login/?next=/posts/1/edit/'
UNEXISTING_PAGE = '/unexisting_page/'


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.any_template_urls = [
            PROFILE,
            POST_DETAIL,
            INDEX,
            GROUP_LIST]
        cls.auth_templates_url = [POST_CREATE, ]
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
        for adress in self.any_template_urls:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Страница unexisting_page/ вернёт ошибку 404."""
        response = self.guest_client.get(UNEXISTING_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_exists_at_desired_location_authorized(self):
        """Страницы доступные авторизованному пользователю."""
        for adress in self.auth_templates_url:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_for_auth(self):
        """Проверка редиректа авторизированного пользователя
        для стариницы post/edit."""
        response = self.authorized_client.get(POST_EDIT, follow=True)
        self.assertRedirects(response, POST_DETAIL)

    def test_post_edit_url_redirect_for_auth(self):
        """Проверка редиректа неавторизированного пользователя
        для стариницы post/edit."""
        response = self.guest_client.get(POST_EDIT, follow=True)
        self.assertRedirects(response, LOGIN_ADRESS)

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница posts/edit/ доступна автору."""
        response = self.author_client.get(POST_EDIT)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_url_name = {
            PROFILE: 'posts/profile.html',
            POST_DETAIL: 'posts/post_detail.html',
            POST_CREATE: 'posts/post_create.html',
            POST_EDIT: 'posts/post_create.html',
            INDEX: 'posts/index.html',
            GROUP_LIST: 'posts/group_list.html'}
        for adress, template in template_url_name.items():
            with self.subTest(adress=adress):
                response = StaticURLTests.author_client.get(adress)
                self.assertTemplateUsed(response, template)
