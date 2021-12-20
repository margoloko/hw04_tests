from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect

from .forms import PostForm
from .models import Post, Group, User


def paginator(request: HttpRequest, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return(page_obj)


def index(request: HttpRequest) -> HttpResponse:
    ''' Функция выводит на главную страницу десять последних постов.'''
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_obj = paginator(request, post_list)
    context = {'page_obj': page_obj, }
    return render(request, template, context)


def group_posts(request: HttpRequest, slug) -> HttpResponse:
    ''' Функция group_posts передаёт в шаблон posts/group_list.html десять
    последних объектов модели Post, принадлежащих соответствующей группе.'''
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(request, posts)
    context = {'group': group,
               'posts': posts,
               'page_obj': page_obj, }
    return render(request, template, context)


def profile(request: HttpRequest, username):
    ''' Функция для отображения профиля пользователя.'''
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    author_post = author.posts.filter(author=author)
    posts = Post.objects.filter(author=author)
    post_count = posts.count()
    page_obj = paginator(request, author_post)
    context = {'author': author,
               'posts': posts,
               'post_count': post_count,
               'page_obj': page_obj, }
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id):
    ''' Функция выводит детальную информацию о посте.'''
    template = 'posts/post_detail.html'
    post_page = Post.objects.get(pk=post_id)
    post_count = Post.objects.filter(author=post_page.author).count()
    context = {'post_page': post_page,
               'post_count': post_count, }
    return render(request, template, context)


@login_required
def post_create(request: HttpRequest):
    ''' Функция для создания поста.'''
    template = 'posts/post_create.html'
    form = PostForm()
    context = {'form': form}
    if request.method == "POST":
        post_author = Post(author=request.user)
        form = PostForm(request.POST or None, instance=post_author)
        if form.is_valid():
            form.cleaned_data['text']
            form.cleaned_data['group']
            form.save()
            return redirect('posts:profile', request.user)
        return render(request, template, {'form': form})
    return render(request, template, context)


@login_required
def post_edit(request: HttpRequest, post_id):
    ''' Функция для редактирования поста.'''
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        form = PostForm(request.POST or None, instance=post)
        is_edit = True
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        context = {'form': form,
                   'is_edit': is_edit,
                   'post_id': post_id, }
        return render(request, 'posts/post_create.html', context)
    return redirect('posts:post_detail', post_id)
