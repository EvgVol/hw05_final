from http import HTTPStatus

from django.shortcuts import render


# Ошибка 404 -------------------------------------------------------
def page_not_found(request, exception):
    """Выводим страницу 404 когда страница не найдена."""
    return render(
        request, 'core/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND)


# Ошибка 500 -------------------------------------------------------
def server_error(request):
    """Выводим страницу 500 когда что-то пошло не так на сервере."""
    return render(
        request,
        'core/500.html',
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )


# Ошибка 403 -------------------------------------------------------
def csrf_failure(request, exception):
    """Выводим страницу 403 когда у пользователя нет
    доступа к этой странице.
    """
    return render(
        request,
        'core/403.html',
        status=HTTPStatus.FORBIDDEN
    )
