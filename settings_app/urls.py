from django.urls import path
from . import views

app_name = "settings_app"

urlpatterns = [
    path("", views.CompanySettingUpdateView.as_view(), name="edit"),
]
