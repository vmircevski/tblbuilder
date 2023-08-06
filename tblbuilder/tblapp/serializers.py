from rest_framework import serializers

COLUMN_CHANGE_CHOICES = (
    ("add", "add"),
    ("remove", "remove"),
    ("alter", "alter"),
)

COLUMN_TYPE_CHOICES = (
    ("string", "string"),
    ("number", "number"),
    ("boolean", "boolean"),
)


class ColumnSerializer(serializers.Serializer):
    colname = serializers.CharField()
    coltype = serializers.CharField()


class TableSerializer(serializers.Serializer):
    tblname = serializers.CharField()
    columns = serializers.ListField(child=ColumnSerializer())


class ColumnChangeSerializer(serializers.Serializer):
    change = serializers.ChoiceField(choices=COLUMN_CHANGE_CHOICES)
    oldcolname = serializers.CharField(required=False)
    colname = serializers.CharField()
    # for removing 'coltype' is not required
    coltype = serializers.ChoiceField(choices=COLUMN_TYPE_CHOICES, required=False)
