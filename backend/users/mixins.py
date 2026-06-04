from rest_framework import serializers


class FullNameSerializerMixin(serializers.Serializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        if isinstance(obj, dict):
            return obj.get('full_name') or ' '.join(filter(None, [
                obj.get('last_name'),
                obj.get('first_name'),
                obj.get('middle_name'),
            ]))

        user = getattr(obj, 'user', obj)
        return ' '.join(filter(None, [
            getattr(user, 'last_name', None),
            getattr(user, 'first_name', None),
            getattr(user, 'middle_name', None),
        ]))
