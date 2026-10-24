import pytest
from django.core.management import call_command
from apps.accounts.models import User
from apps.predictions.models import Prediction


@pytest.mark.django_db
def test_seed_demo_data_command():
    """
    Verify seed_demo_data management command creates admin, demo user, and predictions idempotently.
    """
    call_command("seed_demo_data")

    admin = User.objects.filter(email="admin@realestate.local").first()
    assert admin is not None
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.check_password("AdminPassword123!") is True

    demo = User.objects.filter(email="demo@realestate.local").first()
    assert demo is not None
    assert demo.is_staff is False
    assert demo.check_password("DemoPassword123!") is True

    predictions = Prediction.objects.filter(user=demo)
    assert predictions.count() == 5

    # Re-run for idempotency
    call_command("seed_demo_data")
    assert Prediction.objects.filter(user=demo).count() == 5
