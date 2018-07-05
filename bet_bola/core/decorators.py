import functools

from django.contrib.admin import helpers
from django.template.response import TemplateResponse


def confirm_action(title=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, queryset):

            if 'confirm' in request.POST and request.POST:
                func(self, request, queryset)
                return None

            context = dict(
                self.admin_site.each_context(request),
                title=title,
                action=func.__name__,
                opts=self.model._meta,
                queryset=queryset,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME)

            return TemplateResponse(request, 'admin/do_action_on_selected_confirmation.html', context)

        wrapper.short_description = title

        return wrapper

    return decorator