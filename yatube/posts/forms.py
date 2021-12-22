from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Форма для создания поста."""
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {'text': 'Текст',
                  'group': 'Группа',
                  }
        help_texts = {'text': 'Введите текст',
                      'group': 'выберете из существующих',
                      }


# class CommentForm(forms.ModelForm):
#    """Форма для создания комментария."""
#    class Meta:
#        model = Comment
#        fields = "__all__"
