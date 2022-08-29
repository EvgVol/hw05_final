from django.views.generic.base import TemplateView


class AboutOfMe(TemplateView):
    template_name = 'about/author.html'


class AboutOfTech(TemplateView):
    template_name = 'about/tech.html'
