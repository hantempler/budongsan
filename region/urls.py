from django.urls import path
from region import views 


urlpatterns = [
    path("map", views.region_map, name = "map"),
    path('locations/', views.location_selector, name='location_selector'),
    path('graph/', views.region_graph, name='region_graph')
]
