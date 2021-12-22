from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class StaticPageTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        """Smoke test страницы об авторе"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech(self):
        """Smoke test страницы Технологии"""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_author_url(self):
        """URL, генерируемый при помощи имени about:author, доступен."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_url(self):
        """URL, генерируемый при помощи имени about:tech, доступен."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_page_uses_correct_template(self):
        """При запросе к about:tech
        применяется шаблон staticpages/about.html."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech_page_uses_correct_template(self):
        """При запросе к about: tech
        применяется шаблон staticpages/about.html."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
