from django.views import generic



class IndexView(generic.TemplateView):
    template_name = "core/index.html"
    http_method_names = ["get"]



index_view = IndexView.as_view()
