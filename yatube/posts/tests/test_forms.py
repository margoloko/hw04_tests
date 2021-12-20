from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.author,
            group=cls.group)

    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма добавляет новый пост."""
        form_data = {
            'group': PostFormTests.group.pk,
            'text': 'Тестовый текст'}
        # Подсчитаем количество постов в Post
        post_count = Post.objects.count()
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': 'NoName'}))
        self.assertEqual(response.status_code, 200)
# Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        """Валидная форма изменяет пост."""
# Подсчитаем количество постов в Post
        post_count = Post.objects.count()
        form_data = {'text': 'Измененный текст'}
        # Отправляем POST-запрос
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={
                    'post_id': PostFormTests.post.pk}),
            data=form_data,
            follow=True)
# Проверяем, что произошло изменение поста
        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст').exists())
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': PostFormTests.post.pk}))
# Проверяем, число постов осталось прежним
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, 200)
