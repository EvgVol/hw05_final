from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админка размещенных постов."""

    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Админка размещенных группы."""

    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    search_fields = ('description',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка размещенных комментариев."""

    list_display = (
        'pk',
        'text',
        'post',
        'author',
    )
    search_fields = ('text',)
    list_filter = ("post",)
    empty_value_display = "-пусто-"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка размещенных подписок."""

    list_display = (
        'user',
        'author',
    )
