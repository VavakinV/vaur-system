from rest_framework import serializers


class FullNameSerializerMixin:
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        parts = [
            getattr(obj, 'last_name', None),
            getattr(obj, 'first_name', None),
            getattr(obj, 'middle_name', None),
        ]
        return ' '.join(filter(None, parts))
