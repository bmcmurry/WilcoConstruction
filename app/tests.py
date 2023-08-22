from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from .models import *
from django.contrib.auth.models import User


class PaymentPortalViewTest(TestCase):
    def setUp(self):
        # Create a user and a tenant with a linked lease
        self.user = User.objects.create_user(
            username="testuser23", password="testpassword"
        )
        self.lease = Lease.objects.create(
            pricePerMonth=1000,
            lateFee=50,
            startDate=datetime.now().date() - timedelta(days=60),
            dueDate=datetime.now().date() - timedelta(days=30),
            currentBalance=200,
        )
        self.tenant = Tenant.objects.create(
            linkToBuiltinUser=self.user,
            first_name="Test",
            last_name="User",
            linkToLease=self.lease,
        )

    def test_current_balance_updated(self):
        # Simulate accessing the PaymentPortalView
        response = self.client.get(reverse("payment_portal"))

        # Get the updated lease object from the database
        updated_lease = Lease.objects.get(pk=self.lease.pk)

        # Calculate expected balance
        today = datetime.now().date()
        difference = today - self.lease.dueDate
        months_overdue = difference.days // 30
        expected_balance = self.lease.currentBalance + months_overdue * (
            self.lease.pricePerMonth + self.lease.lateFee
        )

        # Check if the current balance is updated correctly
        self.assertEqual(updated_lease.currentBalance, expected_balance)


class TenantTestCase(TestCase):
    def setUp(self):
        for i in range(0, 5):
            user = User.objects.create_user(
                username=f"testuser{i+1}", password="testpassword"
            )
            Tenant.objects.create(
                linkToBuiltinUser=user,
                first_name="John",
                last_name="Doe",
                phone="1112223333",
                userEmail="johndoe@gmail.com",
            )

    def tearDown(self):
        # Clean up created data after each test
        User.objects.filter(username__startswith="testuser_").delete()
        Tenant.objects.all().delete()

    def test_unique_username(self):
        username = f"testuser_{self._testMethodName}"
        user = User.objects.create_user(username=username, password="testpass")

    def test_queryset_exists(self):
        qs = Tenant.objects.all()
        self.assertTrue(qs.exists())

    def test_queryset_count(self):
        qs = Tenant.objects.all()
        self.assertEqual(qs.count(), 5)
