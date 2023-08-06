from typing import Dict, Optional, List

from django.db import ProgrammingError
from django.db.utils import DataError
from django.db import connections, models
from rest_framework import serializers

from tblbuilder.tblapp.models import DynTbl
from tblbuilder.tblapp.utils import TblappException


class DynamicTable:
    """It has all operations for managing dynamic tables:
    * creating dynamic table
    * adding/removing/altering columns
    * keeping table metadata in 'dyntbl' table for later re-creating of Django model
    * geting the model serializer from model class
    """

    coltype_map = {
        "string": models.CharField,
        "number": models.IntegerField,
        "boolean": models.BooleanField,
    }

    def __init__(self, data: Dict, create_table: bool = True):
        self.db_conn = connections["default"]
        self.data = data
        self.model_cls = self.get_model_cls(data)
        if create_table:
            self.create_table()

    @classmethod
    def load_from_db(cls, tblname: str) -> "DynamicTable":
        """loads table metadata from 'dyntbl' table and creates model class"""
        d = DynTbl.objects.filter(tblname=tblname).first()
        if d:
            data = {"tblname": d.tblname, "columns": d.columns}
            obj = cls(data, create_table=False)
            return obj
        tblexc = TblappException(
            code="table_load_error",
            detail=f"Table '{tblname}' does not exists.",
        )
        tblexc.status_code = 400
        raise tblexc

    def get_model_cls(self, data: Dict) -> models.Model:
        """dynamically creates Django model class"""

        class Meta:
            app_label = "tblapp"

        model_attrs = {
            "__module__": models.Model.__module__,
            "app_label": "tblbuilder.tblapp",
            "Meta": Meta,
        }

        for col_dict in data["columns"]:
            model_attrs[col_dict["colname"]] = self.coltype_map[col_dict["coltype"]]()

        model_cls = type(data["tblname"], (models.Model,), model_attrs)
        return model_cls

    def create_table(self) -> None:
        """creates the table from Django model and persists in the DB"""
        try:
            with self.db_conn.schema_editor() as schema_editor:
                schema_editor.create_model(self.model_cls)
        except ProgrammingError:
            tblexc = TblappException(
                code="table_create_error",
                detail=f"Error while creating table: '{self.data['tblname']}.'",
            )
            tblexc.status_code = 400
            raise tblexc
        else:
            self.save_to_db()

    def save_to_db(self) -> None:
        """saves table's name and columns in 'dyntbl' table"""
        d = DynTbl(tblname=self.data["tblname"], columns=self.data["columns"])
        d.save()

    def process_column(self, coldef: Dict):
        """uses clients json to decide next steps"""
        if coldef["change"] == "add":
            self.add_column(coldef)
        elif coldef["change"] == "alter":
            self.alter_column(coldef)
        elif coldef["change"] == "remove":
            self.remove_column(coldef)

    def add_column(self, coldef: Dict) -> None:
        """adds column to dynamic table and saves metadata to 'dyntbl' table"""
        field = self.coltype_map[coldef["coltype"]](null=True)
        field.column = coldef["colname"]

        try:
            with self.db_conn.schema_editor() as schema_editor:
                schema_editor.add_field(self.model_cls, field)
        except ProgrammingError:
            tblexc = TblappException(
                code="field_add_error",
                detail=f"Error while creating field: '{coldef['colname']}'. Field already exists.",
            )
            tblexc.status_code = 400
            raise tblexc
        else:
            self.column_to_db(coldef, "add")

    def alter_column(self, coldef: Dict) -> None:
        """alters column to dynamic table and saves metadata to 'dyntbl' table"""
        try:
            local_coldef = list(
                filter(
                    lambda col: col["colname"] == coldef["oldcolname"],
                    self.data["columns"],
                )
            )[0]
        except IndexError:
            tblexc = TblappException(
                code="not_found",
                detail=f"Column '{coldef['oldcolname']}' was not found",
            )
            tblexc.status_code = 404
            raise tblexc

        old_field = self.coltype_map[local_coldef["coltype"]]()
        old_field.column = local_coldef["colname"]

        new_field = self.coltype_map[coldef["coltype"]]()
        new_field.column = coldef["colname"]

        try:
            with self.db_conn.schema_editor() as schema_editor:
                schema_editor.alter_field(self.model_cls, old_field, new_field)
        except ProgrammingError:
            tblexc = TblappException(
                code="column_error",
                detail=f"Column '{coldef['colname']}' already exists.",
            )
            tblexc.status_code = 404
            raise tblexc
        except DataError:
            tblexc = TblappException(
                code="data_convert_error",
                detail=f"Column '{coldef['oldcolname']}' cannot be converted to '{coldef['coltype']}'",
            )
            tblexc.status_code = 404
            raise tblexc
        else:
            self.column_to_db(coldef, "alter")

    def remove_column(self, coldef: Dict) -> None:
        """removes column to dynamic table and saves metadata to 'dyntbl' table"""
        try:
            local_coldef = list(
                filter(
                    lambda col: col["colname"] == coldef["colname"],
                    self.data["columns"],
                )
            )[0]
        except IndexError:
            tblexc = TblappException(
                code="not_found", detail=f"Column '{coldef['colname']}' was not found"
            )
            tblexc.status_code = 404
            raise tblexc

        field = self.coltype_map[local_coldef["coltype"]]()
        field.column = coldef["colname"]

        try:
            with self.db_conn.schema_editor() as schema_editor:
                schema_editor.remove_field(self.model_cls, field)
        except ProgrammingError:
            tblexc = TblappException(
                code="remove_column_error",
                detail=f"Error while removing column '{coldef['colname']}'",
            )
            tblexc.status_code = 400
            raise tblexc
        else:
            self.column_to_db(coldef, "remove")

    def column_to_db(self, coldef: Dict, change: str = "add") -> None:
        """saves added/removed/altered column to 'dyntbl' table"""
        d = DynTbl.objects.filter(tblname=self.data["tblname"]).first()
        if change == "add":
            del coldef["change"]
            d.columns.append(coldef)
            d.save()
        elif change == "remove":
            d.columns = list(
                filter(lambda col: col["colname"] != coldef["colname"], d.columns)
            )
            d.save()
        elif change == "alter":
            for i in range(len(d.columns)):
                col = d.columns[i]
                if col["colname"] == coldef["oldcolname"]:
                    d.columns[i] = {
                        "colname": coldef["colname"],
                        "coltype": coldef["coltype"],
                    }
            d.save()

    def get_fields(self) -> List:
        return [x["colname"] for x in self.data["columns"]]

    def get_serializer(self) -> serializers.ModelSerializer:
        """creates Dynamic Table Serializer class from model class"""
        meta_cls = type(
            "Meta",
            (object,),
            {
                "model": self.model_cls,
                "fields": self.get_fields(),
            },
        )
        ser = type(
            "DynamicTableSerializer", (serializers.ModelSerializer,), {"Meta": meta_cls}
        )
        return ser
