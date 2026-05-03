from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    """Full serializer — used for CRUD operations."""

    display_title   = serializers.SerializerMethodField()
    display_company = serializers.SerializerMethodField()

    class Meta:
        model  = Application
        fields = [
            'id',
            'user',
            'job',
            'company_name',
            'job_title',
            'display_title',
            'display_company',
            'status',
            'notes',
            'applied_date',
            'order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at',
                            'display_title', 'display_company']

    def get_display_title(self, obj):
        return obj.get_display_title()

    def get_display_company(self, obj):
        return obj.get_display_company()

    def validate(self, data):
        """
        Must have either a job FK  OR  both company_name + job_title.
        """
        job          = data.get('job')
        company_name = data.get('company_name', '').strip()
        job_title    = data.get('job_title', '').strip()

        if not job and not (company_name and job_title):
            raise serializers.ValidationError(
                "Provide either a job ID or both company_name and job_title."
            )
        return data


class MoveCardSerializer(serializers.Serializer):
    """Lightweight serializer just for moving a card to a new column."""

    STATUS_CHOICES = [s[0] for s in Application.KANBAN_STATUS_CHOICES]

    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    order  = serializers.IntegerField(required=False, min_value=0)


class KanbanColumnSerializer(serializers.Serializer):
    """One column in the board response."""

    status = serializers.CharField()
    label  = serializers.CharField()
    cards  = ApplicationSerializer(many=True)