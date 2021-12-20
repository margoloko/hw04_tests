from django.db import models
from django.contrib.auth import get_user_model
from pytils.translit import slugify

User = get_user_model()


class Group(models.Model):
    ''' Класс Group для сообществ'''

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True,
                            max_length=190,)
    description = models.TextField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    ''' Класс Post описывает свойства постов'''

    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts')

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
