from django.test import TestCase
from .models import *


class TenantTestCase(TestCase):
    def setUp(self):
        for i in range(0, 5):
            user = User.objects.create_user(
                username=f"testuser{i}", password="testpassword"
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
