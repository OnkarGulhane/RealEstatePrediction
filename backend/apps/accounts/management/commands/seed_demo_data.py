from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.predictions.models import Prediction


class Command(BaseCommand):
    help = "Seed standard demo credentials, admin accounts, and realistic valuation history for Phase 7 local release."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing predictions before seeding",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo data for Real Estate Prediction Platform..."))

        # 1. Admin Superuser
        admin_email = "admin@realestate.local"
        admin_password = "AdminPassword123!"
        admin_user, created_admin = User.objects.get_or_create(
            email=admin_email,
            defaults={
                "display_name": "System Administrator",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            }
        )
        if not created_admin:
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
        admin_user.set_password(admin_password)
        admin_user.save()

        status_text = "created" if created_admin else "updated"
        self.stdout.write(self.style.SUCCESS(f"  [+] Admin user {status_text}: {admin_email} (Pass: {admin_password})"))

        # 2. Standard Demo User
        demo_email = "demo@realestate.local"
        demo_password = "DemoPassword123!"
        demo_user, created_demo = User.objects.get_or_create(
            email=demo_email,
            defaults={
                "display_name": "Priya Sharma",
                "is_staff": False,
                "is_superuser": False,
                "is_active": True,
            }
        )
        demo_user.set_password(demo_password)
        demo_user.save()

        status_text = "created" if created_demo else "updated"
        self.stdout.write(self.style.SUCCESS(f"  [+] Demo user {status_text}: {demo_email} (Pass: {demo_password})"))

        # 3. Optional Clear
        if options.get("clear"):
            deleted_count, _ = Prediction.objects.filter(user__in=[admin_user, demo_user]).delete()
            self.stdout.write(self.style.WARNING(f"  [-] Cleared {deleted_count} existing predictions for demo accounts."))

        # 4. Realistic Valuation History for Demo User
        sample_records = [
            {
                "location": "Mumbai",
                "area_value": 1250.0,
                "area_basis": "CARPET",
                "bhk": 3,
                "bathrooms": 3.0,
                "balcony": 2,
                "floor_number": 15.0,
                "total_floors": 24.0,
                "parking_spaces": 2,
                "furnishing": "Furnished",
                "transaction_type": "Resale",
                "status": "Ready to Move",
                "facing": "East",
                "ownership": "Co-operative Society",
                "estimated_price_inr": Decimal("38500000.00"),
            },
            {
                "location": "Bangalore",
                "area_value": 1800.0,
                "area_basis": "SUPER",
                "bhk": 3,
                "bathrooms": 3.0,
                "balcony": 1,
                "floor_number": 4.0,
                "total_floors": 12.0,
                "parking_spaces": 1,
                "furnishing": "Semi-Furnished",
                "transaction_type": "New Property",
                "status": "Ready to Move",
                "facing": "North",
                "ownership": "Freehold",
                "estimated_price_inr": Decimal("14500000.00"),
            },
            {
                "location": "Pune",
                "area_value": 950.0,
                "area_basis": "CARPET",
                "bhk": 2,
                "bathrooms": 2.0,
                "balcony": 1,
                "floor_number": 7.0,
                "total_floors": 14.0,
                "parking_spaces": 1,
                "furnishing": "Unfurnished",
                "transaction_type": "Resale",
                "status": "Ready to Move",
                "facing": "East",
                "ownership": "Freehold",
                "estimated_price_inr": Decimal("7850000.00"),
            },
            {
                "location": "New Delhi",
                "area_value": 2200.0,
                "area_basis": "CARPET",
                "bhk": 4,
                "bathrooms": 4.0,
                "balcony": 3,
                "floor_number": 2.0,
                "total_floors": 4.0,
                "parking_spaces": 2,
                "furnishing": "Furnished",
                "transaction_type": "Resale",
                "status": "Ready to Move",
                "facing": "North - East",
                "ownership": "Freehold",
                "estimated_price_inr": Decimal("42000000.00"),
            },
            {
                "location": "Hyderabad",
                "area_value": 1550.0,
                "area_basis": "SUPER",
                "bhk": 3,
                "bathrooms": 2.0,
                "balcony": 2,
                "floor_number": 9.0,
                "total_floors": 18.0,
                "parking_spaces": 1,
                "furnishing": "Semi-Furnished",
                "transaction_type": "New Property",
                "status": "Ready to Move",
                "facing": "East",
                "ownership": "Freehold",
                "estimated_price_inr": Decimal("11200000.00"),
            },
        ]

        seeded_predictions = 0
        for item in sample_records:
            exists = Prediction.objects.filter(
                user=demo_user,
                location=item["location"],
                area_value=item["area_value"],
                bhk=item["bhk"],
            ).exists()
            if not exists:
                Prediction.objects.create(
                    user=demo_user,
                    model_version="1.0.0-lgbm",
                    schema_version="1.0",
                    created_at=timezone.now(),
                    **item
                )
                seeded_predictions += 1

        self.stdout.write(self.style.SUCCESS(f"  [+] Seeded {seeded_predictions} historical predictions for {demo_email}."))
        self.stdout.write(self.style.SUCCESS("\nDemo data seeding completed successfully!"))
