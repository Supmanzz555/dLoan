from django.core.management.base import BaseCommand
from data.applicants import ALL_APPLICANTS
from django_api.screening.models import Applicant


class Command(BaseCommand):
    help = "Seed 20 sample applicants into the database"

    def handle(self, *args, **options):
        created = 0
        for data in ALL_APPLICANTS:
            _, was_created = Applicant.objects.update_or_create(
                applicant_id=data["applicant_id"],
                defaults={
                    "name": data["name"],
                    "age": data["age"],
                    "employment_type": data["employment_type"],
                    "monthly_income": data["monthly_income"],
                    "monthly_debt": data["monthly_debt"],
                    "requested_loan_amount": data["requested_loan_amount"],
                    "credit_history": data["credit_history"],
                    "uploaded_documents": data.get("uploaded_documents", []),
                    "notes": data.get("notes", ""),
                    "response_lang": "en",
                },
            )
            if was_created:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(f"Seeded {created} applicants (total: {Applicant.objects.count()})")
        )
