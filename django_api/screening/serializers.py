from rest_framework import serializers
from .models import Applicant, Screening, Feedback


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ApplicantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = (
            "id",
            "applicant_id",
            "name",
            "age",
            "employment_type",
            "monthly_income",
            "credit_history",
        )


class ScreeningSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(
        source="applicant.name", read_only=True, default=""
    )
    initiated_by_name = serializers.CharField(
        source="initiated_by.username", read_only=True, default=""
    )
    has_feedback = serializers.BooleanField(read_only=True)

    class Meta:
        model = Screening
        fields = (
            "id",
            "job_id",
            "applicant",
            "applicant_name",
            "initiated_by",
            "initiated_by_name",
            "has_feedback",
            "status",
            "progress",
            "error_message",
            "result_data",
            "agent_states",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "job_id", "created_at", "updated_at")


class ScreeningDetailSerializer(serializers.ModelSerializer):
    applicant_data = ApplicantSerializer(source="applicant", read_only=True)

    class Meta:
        model = Screening
        fields = "__all__"
        read_only_fields = ("id", "job_id", "created_at", "updated_at")


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"
        read_only_fields = ("id", "created_at", "reviewed_at")


class FeedbackListSerializer(serializers.ModelSerializer):
    job_id = serializers.CharField(source="screening.job_id", read_only=True)
    applicant_name = serializers.CharField(
        source="screening.applicant.name", read_only=True, default=""
    )
    submitted_by_name = serializers.CharField(
        source="submitted_by.username", read_only=True, default=""
    )
    reviewed_by_name = serializers.CharField(
        source="reviewed_by.username", read_only=True, default=""
    )

    class Meta:
        model = Feedback
        fields = (
            "id",
            "screening",
            "job_id",
            "applicant_name",
            "submitted_by",
            "submitted_by_name",
            "correct",
            "override_recommendation",
            "comment",
            "reviewed_by",
            "reviewed_by_name",
            "review_status",
            "review_comment",
            "reviewed_at",
            "created_at",
        )


class ScreenInputSerializer(serializers.Serializer):
    applicant_id = serializers.CharField()
    response_lang = serializers.CharField(default="en")


class DashboardSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_outcome = serializers.DictField()
    by_status = serializers.DictField()
    agreement_pct = serializers.IntegerField()
    overrides_count = serializers.IntegerField()
    top_risk_flags = serializers.ListField()
    recent = serializers.ListField()
