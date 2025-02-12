from django.urls import path
from apt import views

urlpatterns = [
    path("", views.index, name = "main_page"),
    path("apt_list/", views.apt_list, name='apt_list'),
    path("apt_info/<str:complexNo>/", views.apt_info, name = "apt_info"),
    path("details/<str:complexno_py>/", views.apt_detail, name="apt_detail"),

]

