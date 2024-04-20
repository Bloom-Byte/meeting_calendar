from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.views import generic
from users.decorators import redirect_authenticated


class IndexView(generic.TemplateView):
    template_name = "core/index.html"
    http_method_names = ["get"]

    @redirect_authenticated("dashboard:dashboard")
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)


index_view = IndexView.as_view()
