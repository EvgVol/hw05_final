from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import (PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)

from .forms import CreationForm


class SignUp(CreateView):
    """Регистрация нового пользователя."""

    form_class = CreationForm
    success_url = reverse_lazy('group:index')
    template_name = 'users/signup.html'


class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'


class PasswordChange(PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_confirm.html'


class PasswordResetDone(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class PasswordReset(PasswordResetView):
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'
