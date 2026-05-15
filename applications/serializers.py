from rest_framework import serializers

from .models import Application, CandidateNote


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source="applicant.username", read_only=True)
    applicant_email = serializers.EmailField(source="applicant.email", read_only=True)
    applicant_first_name = serializers.CharField(source="applicant.first_name", read_only=True)
    applicant_last_name = serializers.CharField(source="applicant.last_name", read_only=True)

    job_display_title = serializers.SerializerMethodField()
    company_display_name = serializers.SerializerMethodField()
    recruiter_id = serializers.SerializerMethodField()
    recruiter_name = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "applicant",
            "applicant_name",
            "applicant_email",
            "applicant_first_name",
            "applicant_last_name",
            "job_title",
            "company",
            "job_display_title",
            "company_display_name",
            "recruiter_id",
            "recruiter_name",
            "status",
            "applied_date",
            "notes",
            "contact_name",
            "contact_email",
            "created_at",
            "updated_at",
            "reviewed_at",
        ]

        read_only_fields = [
            "id",
            "applicant",
            "applicant_name",
            "applicant_email",
            "applicant_first_name",
            "applicant_last_name",
            "job_display_title",
            "company_display_name",
            "recruiter_id",
            "recruiter_name",
            "created_at",
            "updated_at",
            "reviewed_at",
        ]

    def get_job_display_title(self, obj):
        if obj.job:
            return obj.job.title
        return obj.job_title

    def get_company_display_name(self, obj):
        if obj.job:
            return obj.job.company
        return obj.company

    def get_recruiter_id(self, obj):
        if obj.job and obj.job.posted_by:
            return obj.job.posted_by.id
        return None

    def get_recruiter_name(self, obj):
        if obj.job and obj.job.posted_by:
            return obj.job.posted_by.username
        return None

    def validate_status(self, value):
        allowed_statuses = [choice[0] for choice in Application.STATUS_CHOICES]

        if value not in allowed_statuses:
            raise serializers.ValidationError("Invalid application status.")

        return value


class CandidateNoteSerializer(serializers.ModelSerializer):
    recruiter_name = serializers.CharField(source="recruiter.username", read_only=True)
    candidate_name = serializers.CharField(source="candidate.username", read_only=True)

    class Meta:
        model = CandidateNote
        fields = [
            "id",
            "candidate",
            "candidate_name",
            "recruiter",
            "recruiter_name",
            "content",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "candidate",
            "candidate_name",
            "recruiter",
            "recruiter_name",
            "created_at",
            "updated_at",
        ]


class CandidateProfileSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)

    total_applications = serializers.IntegerField()
    pending = serializers.IntegerField()
    applied = serializers.IntegerField()
    screening = serializers.IntegerField()
    interview = serializers.IntegerField()
    offer = serializers.IntegerField()
    accepted = serializers.IntegerField()
    rejected = serializers.IntegerField()
    withdrawn = serializers.IntegerField()

    first_applied = serializers.DateTimeField(allow_null=True)
    last_applied = serializers.DateTimeField(allow_null=True)
    applications = ApplicationSerializer(many=True)
    notes_count = serializers.IntegerField()