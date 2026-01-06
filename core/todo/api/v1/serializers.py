from rest_framework import serializers
from todo.models import Task
from accounts.models import Profile


class TaskSerializer(serializers.ModelSerializer):
    snippet = serializers.ReadOnlyField(source="get_snippet")
    relative_url = serializers.URLField(source="get_absolute_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField(method_name="get_abs_url")

    class Meta:
        model = Task
        fields = [
            "id",
            "user",
            "description",
            "snippet",
            "title",
            "complete",
            "relative_url",
            "absolute_url",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["user", "id"]

    def get_abs_url(self, obj):

        request = self.context.get("request")
        if not request:
            return None
        return request.build_absolute_uri(obj.pk)

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("snippet", None)
            rep.pop("relative_url", None)
            rep.pop("absolute_url", None)
        else:
            rep.pop("description", None)
        return rep

    def create(self, validated_data):
        validated_data["user"] = Profile.objects.get(
            user__id=self.context.get("request").user.id
        )
        return super().create(validated_data)
