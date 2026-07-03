from django.db import models


class Applicant(models.Model):
    applicant_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    employment_type = models.CharField(max_length=30)
    monthly_income = models.FloatField()
    monthly_debt = models.FloatField()
    requested_loan_amount = models.FloatField()
    credit_history = models.CharField(max_length=30)
    uploaded_documents = models.JSONField(default=list)
    notes = models.TextField(blank=True, null=True)
    response_lang = models.CharField(max_length=5, default="en")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "applicant"
        ordering = ["applicant_id"]

    def __str__(self):
        return f"{self.applicant_id} — {self.name}"


class Screening(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("running", "Running"),
        ("done", "Done"),
        ("error", "Error"),
        ("pending_review", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("sent_back", "Sent Back"),
    ]
    applicant = models.ForeignKey(
        Applicant, on_delete=models.SET_NULL, null=True, blank=True
    )
    initiated_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    job_id = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=14, choices=STATUS_CHOICES, default="queued"
    )
    input_data = models.JSONField()
    result_data = models.JSONField(null=True, blank=True)
    agent_states = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    progress = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "screening"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.job_id} — {self.status}"


class Feedback(models.Model):
    screening = models.ForeignKey(
        Screening, on_delete=models.CASCADE, related_name="feedbacks"
    )
    submitted_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    correct = models.BooleanField()
    override_recommendation = models.CharField(max_length=30, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_feedbacks",
    )
    review_status = models.CharField(
        max_length=10, blank=True, null=True,
        choices=[("concur", "Concur"), ("send_back", "Send Back")],
    )
    review_comment = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "feedback"
        ordering = ["-created_at"]
        unique_together = ("screening", "submitted_by")

    def __str__(self):
        return f"Feedback for {self.screening.job_id}: {'correct' if self.correct else 'override'}"
