import csv
import json

from django.db import IntegrityError
from django.db.models import Count, Exists, OuterRef, Q
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django_api.accounts.log import log_activity
from django_api.accounts.permissions import IsReviewer
from data.applicants import APPLICANT_MAP

from .models import Applicant, Screening, Feedback
from .serializers import (
    ApplicantSerializer,
    ApplicantListSerializer,
    ScreeningSerializer,
    ScreeningDetailSerializer,
    FeedbackSerializer,
    FeedbackListSerializer,
    ScreenInputSerializer,
)
from .screening_service import start_screening, get_job_status


class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ApplicantListSerializer
        return ApplicantSerializer

    def get_queryset(self):
        qs = Applicant.objects.all()
        search = self.request.query_params.get("search", "")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(applicant_id__icontains=search)
                | Q(employment_type__icontains=search)
            )
        return qs


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def screen_applicant_view(request):
    ser = ScreenInputSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    applicant_id = ser.validated_data["applicant_id"]
    response_lang = ser.validated_data.get("response_lang", "en")

    if applicant_id in APPLICANT_MAP:
        applicant_dict = dict(APPLICANT_MAP[applicant_id])
    else:
        applicant_obj = Applicant.objects.filter(
            applicant_id=applicant_id
        ).first()
        if not applicant_obj:
            return Response(
                {"detail": f"Applicant {applicant_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        applicant_dict = {
            "applicant_id": applicant_obj.applicant_id,
            "name": applicant_obj.name,
            "age": applicant_obj.age,
            "employment_type": applicant_obj.employment_type,
            "monthly_income": applicant_obj.monthly_income,
            "monthly_debt": applicant_obj.monthly_debt,
            "requested_loan_amount": applicant_obj.requested_loan_amount,
            "credit_history": applicant_obj.credit_history,
            "uploaded_documents": applicant_obj.uploaded_documents,
            "notes": applicant_obj.notes,
        }

    if response_lang:
        applicant_dict["response_lang"] = response_lang

    job_id = start_screening(applicant_dict, user=request.user)
    log_activity(
        request.user, "screen_applicant",
        {"applicant_id": applicant_id, "job_id": job_id},
        request,
    )
    return Response({"job_id": job_id})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def screen_status_view(request, job_id):
    job = get_job_status(job_id)
    if job.get("status") == "not_found":
        return Response(
            {"detail": "Job not found"}, status=status.HTTP_404_NOT_FOUND
        )
    return Response(job)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def feedback_view(request):
    if request.method == "GET":
        feedbacks = Feedback.objects.select_related(
            "screening__applicant", "submitted_by", "reviewed_by"
        ).all().order_by("-created_at")[:200]
        ser = FeedbackListSerializer(feedbacks, many=True)
        return Response(ser.data)

    screening_id = request.data.get("screening_id")
    correct = request.data.get("correct")
    override = request.data.get("override_recommendation")
    comment = request.data.get("comment")

    if screening_id is None or correct is None:
        return Response(
            {"detail": "screening_id and correct are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(correct, bool):
        return Response(
            {"detail": "correct must be a boolean"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if correct is False and not (comment and comment.strip()):
        return Response(
            {"detail": "Comment is required when overriding AI recommendation"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    screening = Screening.objects.filter(id=screening_id).first()
    if screening is None:
        return Response(
            {"detail": "Screening not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        Feedback.objects.create(
            screening=screening,
            submitted_by=request.user,
            correct=correct,
            override_recommendation=override,
            comment=comment,
        )
    except IntegrityError:
        return Response(
            {"detail": "Feedback already submitted for this screening"},
            status=status.HTTP_409_CONFLICT,
        )
    screening.status = "pending_review"
    screening.save(update_fields=["status"])
    log_activity(
        request.user, "submit_feedback",
        {"screening_id": screening_id, "correct": correct, "override": override},
        request,
    )
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsReviewer])
def review_screening(request, screening_id):
    from datetime import datetime, timezone

    screening = Screening.objects.filter(id=screening_id).first()
    if screening is None:
        return Response({"detail": "Screening not found"}, status=status.HTTP_404_NOT_FOUND)

    if screening.status != "pending_review":
        return Response(
            {"detail": f"Cannot review screening with status '{screening.status}'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    action = request.data.get("action")
    comment = request.data.get("comment", "")

    if action not in ("concur", "send_back"):
        return Response(
            {"detail": "action must be 'concur' or 'send_back'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    feedback = screening.feedbacks.first()
    if feedback:
        feedback.reviewed_by = request.user
        feedback.review_status = action
        feedback.review_comment = comment
        feedback.reviewed_at = datetime.now(timezone.utc)
        feedback.save(update_fields=["reviewed_by", "review_status", "review_comment", "reviewed_at"])

    new_status = "approved" if action == "concur" else "sent_back"
    screening.status = new_status
    screening.save(update_fields=["status"])

    log_activity(
        request.user, f"review_{action}",
        {"screening_id": screening_id, "comment": comment},
        request,
    )
    return Response({"status": new_status})


class ScreeningViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScreeningSerializer

    def get_queryset(self):
        qs = Screening.objects.select_related("applicant", "initiated_by").annotate(
            has_feedback=Exists(
                Feedback.objects.filter(screening_id=OuterRef("id"))
            )
        )
        status_filter = self.request.query_params.get("status", "")
        if status_filter:
            qs = qs.filter(status=status_filter)
        search = self.request.query_params.get("search", "")
        if search:
            qs = qs.filter(
                Q(job_id__icontains=search)
                | Q(applicant__name__icontains=search)
                | Q(applicant__applicant_id__icontains=search)
            )
        return qs

    @action(detail=True, methods=["get"])
    def detail(self, request, pk=None):
        screening = self.get_object()
        ser = ScreeningDetailSerializer(screening)
        return Response(ser.data)

    @action(detail=False, methods=["get"])
    def export(self, request):
        qs = self.get_queryset().filter(status__in=["done", "pending_review", "approved", "rejected", "sent_back"])
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=screenings.csv"
        writer = csv.writer(response)
        writer.writerow(
            [
                "Job ID",
                "Applicant ID",
                "Name",
                "Initiated By",
                "Recommendation",
                "Confidence",
                "Status",
                "Eligibility",
                "DTI Ratio",
                "Risk Flags",
                "Created",
            ]
        )
        for s in qs:
            rd = s.result_data or {}
            writer.writerow(
                [
                    s.job_id,
                    rd.get("applicant_id", ""),
                    s.applicant.name if s.applicant else "",
                    s.initiated_by.username if s.initiated_by else "",
                    rd.get("recommendation", ""),
                    rd.get("confidence", ""),
                    s.status,
                    rd.get("eligibility_status", ""),
                    rd.get("debt_to_income_ratio", ""),
                    "; ".join(rd.get("risk_flags", [])),
                    s.created_at.isoformat() if s.created_at else "",
                ]
            )
        return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    total = Screening.objects.count()
    completed_statuses = ["done", "pending_review", "approved", "rejected", "sent_back"]
    done = Screening.objects.filter(status__in=completed_statuses)
    by_outcome = {}
    flag_counts: dict[str, int] = {}
    for s in done:
        rd = s.result_data or {}
        rec = rd.get("recommendation", "Unknown")
        by_outcome[rec] = by_outcome.get(rec, 0) + 1
        for flag in rd.get("risk_flags", []):
            flag_counts[flag] = flag_counts.get(flag, 0) + 1

    by_status = dict(
        Screening.objects.values("status")
        .annotate(count=Count("id"))
        .values_list("status", "count")
    )

    fb_total = Feedback.objects.count()
    agreed = Feedback.objects.filter(correct=True).count()
    agreement_pct = round(agreed / fb_total * 100) if fb_total > 0 else 0
    overrides_count = Feedback.objects.filter(correct=False).count()

    recent_filter = request.query_params.get("recent", "all")

    recent_qs = (
        Screening.objects.select_related("applicant", "initiated_by")
        .filter(status__in=completed_statuses)
        .order_by("-created_at")
    )

    if recent_filter == "overrides":
        recent_qs = recent_qs.filter(
            id__in=Feedback.objects.filter(correct=False).values("screening_id")
        )
    elif recent_filter == "agreed":
        recent_qs = recent_qs.filter(
            id__in=Feedback.objects.filter(correct=True).values("screening_id")
        )
    elif recent_filter == "feedback":
        recent_qs = recent_qs.filter(
            id__in=Feedback.objects.values("screening_id")
        )

    recent_qs = recent_qs[:20]

    recent = list(
        recent_qs.values(
            "id", "job_id", "status", "created_at",
            "result_data", "initiated_by__username",
        )
    )

    recent_ids = [r["id"] for r in recent]
    fb_map = {}
    for fb in Feedback.objects.filter(screening_id__in=recent_ids).values(
        "screening_id", "correct"
    ):
        sid = fb["screening_id"]
        if sid not in fb_map:
            fb_map[sid] = fb["correct"]

    for r in recent:
        r["has_feedback"] = r["id"] in fb_map
        r["feedback_correct"] = fb_map.get(r["id"])

    return Response(
        {
            "total": total,
            "by_outcome": by_outcome,
            "by_status": by_status,
            "agreement_pct": agreement_pct,
            "overrides_count": overrides_count,
            "top_risk_flags": sorted(
                flag_counts.items(), key=lambda x: -x[1]
            )[:5],
            "recent": recent,
            "total_feedback": fb_total,
        }
    )
