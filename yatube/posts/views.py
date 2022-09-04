from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .models import Follow, Group, Post, User, Comment
from .forms import PostForm, CommentForm
from .utils import paginator_posts


# Главная страница -------------------------------------------------
def index(request):
    """Описывает работу главной страницы."""
    post_list = Post.objects.select_related('author', 'group').all()
    context = {'page_obj': paginator_posts(request, post_list)}
    return render(request, 'posts/index.html', context)


# Страница групп ---------------------------------------------------
def group_posts(request, slug):
    """Описывает работу страницы сообщества."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    context = {
        'group': group,
        'page_obj': paginator_posts(request, post_list)
    }
    return render(
        request,
        'posts/group_list.html',
        context
    )


# Страница пользователя---------------------------------------------
def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').all()
    following = request.user.is_authenticated and (
        author.following.select_related('username').exists()
    )
    context = {
        'author': author,
        'page_obj': paginator_posts(request, post_list),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


# Страница поста ---------------------------------------------------
def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.prefetch_related('comments__author'),
        pk=post_id
    )

    context = {
        'author': post.author,
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all(),
    }
    return render(request, 'posts/post_detail.html', context)


# Страница создание поста ------------------------------------------
@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect(
            'posts:profile',
            username=request.user.username
        )

    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': False}
    )


# Удаляем нунежный пост --------------------------------------------
@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        post.delete()
    return redirect(
        'posts:profile',
        username=request.user.username
    )


# Страница редактирование поста ------------------------------------
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post_id=post.id)

    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'post': post, 'is_edit': True}
    )


# Добавляем комментарий к посту ------------------------------------
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(
        Post,
        pk=post_id,
    )
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(
            commit=False
        )
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


# Удаляем комментарий ----------------------------------------------
@login_required
def comment_delete(request, id):
    comment = get_object_or_404(Comment, id=id)
    user = request.user
    if ((user == comment.author) or (user == comment.post.author)):
        comment.delete()
    return redirect('posts:post_detail', post_id=comment.post.id)


# страница follow --------------------------------------------------
@login_required
def follow_index(request):
    post_list = Post.objects.select_related('author').filter(
        author__following__user=request.user
    )
    context = {
        'page_obj': paginator_posts(request, post_list),
    }
    return render(request, 'posts/follow.html', context)


# Подписаться на автора---------------------------------------------
@login_required
def profile_follow(request, username):
    following = get_object_or_404(User, username=username)
    follower = request.user
    if follower != following:
        Follow.objects.get_or_create(
            user=follower,
            author=following
        )
    return redirect('posts:profile', username=username)


# Отписаться на автора----------------------------------------------
@login_required
def profile_unfollow(request, username):
    get_object_or_404(Follow, author__username=username).delete()
    return redirect('posts:profile', username=username)
