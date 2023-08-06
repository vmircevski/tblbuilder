from django.db import models


class DynTbl(models.Model):
    tblname = models.CharField(help_text="Dynamic table name", unique=True)
    columns = models.JSONField(help_text="Columns")
    testname = models.CharField()
