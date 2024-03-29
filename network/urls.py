from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from network import views

urlpatterns = [
    path("post/", views.network_recoverage_messaure),
    path("post/async/", views.network_recoverage_messaure_async),
]

urlpatterns = format_suffix_patterns(urlpatterns)
