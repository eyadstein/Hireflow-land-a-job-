from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source="posted_by.username", read_only=True)
    applicant_count = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = [
            "posted_by",
            "created_at",
            "source",
            "is_filled",
            "filled_at",
        ]

    def get_applicant_count(self, obj):
        return obj.application_set.count()

    def get_application_count(self, obj):
        return obj.application_set.count()

    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")

        if self.instance is not None:
            if salary_min is None:
                salary_min = self.instance.salary_min
            if salary_max is None:
                salary_max = self.instance.salary_max

        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError({
                "salary_max": "Maximum salary must be greater than or equal to minimum salary."
            })

        title = attrs.get("title", getattr(self.instance, "title", ""))
        company = attrs.get("company", getattr(self.instance, "company", ""))
        description = attrs.get("description", getattr(self.instance, "description", ""))

        if title is not None and not str(title).strip():
            raise serializers.ValidationError({"title": "Job title is required."})

        if company is not None and not str(company).strip():
            raise serializers.ValidationError({"company": "Company name is required."})

        if description is not None and not str(description).strip():
            raise serializers.ValidationError({"description": "Job description is required."})

        return attrs