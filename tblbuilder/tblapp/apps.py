from django.apps import AppConfig


class TblappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tblbuilder.tblapp"
    verbose_name = "Dynamic Table Creation App"
