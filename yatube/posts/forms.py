from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма для создания поста."""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image') 
        labels = {'text': 'Текст',
                  'group': 'Группа', 
                  'image': 'Картинка'}
        help_texts = {'text': 'Введите текст',
                      'group': 'выберете из существующих',
                      'image': 'Загрузите картинку'}


class CommentForm(forms.ModelForm):
    """Форма для создания комментария."""
    class Meta:
        model = Comment
        fields = "__all__"