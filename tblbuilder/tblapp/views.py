from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tblbuilder.tblapp.serializers import TableSerializer, ColumnChangeSerializer
from tblbuilder.tblapp.dynamic_table import DynamicTable


@api_view(["POST"])
def DynamicTableApi(request):
    """create table"""
    data = JSONParser().parse(request)
    table_serializer = TableSerializer(data=data)
    if table_serializer.is_valid():
        DynamicTable(table_serializer.data, create_table=True)
        return JsonResponse(table_serializer.data)


@api_view(["PUT"])
def DynamicColumnApi(request, tblname):
    """add/remove/alter columns"""
    coldef = JSONParser().parse(request)
    column_change_serializer = ColumnChangeSerializer(data=coldef)
    if column_change_serializer.is_valid():
        dt = DynamicTable.load_from_db(tblname)
        dt.process_column(column_change_serializer.data)
        return JsonResponse(column_change_serializer.data)
    return JsonResponse(
        column_change_serializer.errors, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def DynamicAddRowApi(request, tblname):
    """insert row"""
    row_data = JSONParser().parse(request)
    dt = DynamicTable.load_from_db(tblname)
    dt_serializer = dt.get_serializer()(data=row_data)
    if dt_serializer.is_valid():
        dt_serializer.save()
        return JsonResponse(dt_serializer.data)
    return JsonResponse(dt_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def DynamicListRowsApi(request, tblname):
    """listing rows"""
    dt = DynamicTable.load_from_db(tblname)
    DynamicTableSerializer = dt.get_serializer()
    rows = dt.model_cls.objects.all()
    dt_serializer = DynamicTableSerializer(rows, many=True)
    return Response({"rows": dt_serializer.data})
