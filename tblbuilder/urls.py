from django.urls import include, path

# from rest_framework import routers
from tblbuilder.tblapp import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/table/<str:tblname>", views.DynamicColumnApi),
    path("api/table/<str:tblname>/row", views.DynamicAddRowApi),
    path("api/table/<str:tblname>/rows", views.DynamicListRowsApi),
    path("api/table", views.DynamicTableApi),
]
