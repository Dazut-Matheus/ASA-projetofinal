from rest_framework import serializers
from audits.models import AuditsRemoval


class AuditsRemovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditsRemoval
        fields = "__all__"
