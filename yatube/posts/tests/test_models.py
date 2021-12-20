from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Ооочень длинный тестовый текст',
            author=cls.user,
        )

    def test_models_have_correct_object_names_post(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_text = post.text[:15]
        self.assertEqual(expected_text, str(post))

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_name = group.title
        self.assertEqual(expected_name, str(group))

    def test_title_group_max_length(self):
        """Проверяем, что у модели Group title меньше или равен 200символов."""
        group = PostModelTest.group
        max_length_group = group._meta.get_field('title').max_length
        length_title_group = len(group.title)
        self.assertLessEqual(length_title_group, max_length_group)
