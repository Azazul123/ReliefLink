from django.test import TestCase
from .models import PasswordUtility, Division, District, Upazila, Union, Ward, Housh

class PasswordUtilityTest(TestCase):
    def test_generate_password(self):
        password = PasswordUtility.generate_password(10)
        self.assertEqual(len(password), 10)

    def test_send_password_email(self):
        # Mock send_mail to test without sending real emails
        with self.assertLogs('home.models', level='ERROR') as log:
            PasswordUtility.send_password_email('Test User', 'invalid_email', 'password')
            self.assertIn('Failed to send email', log.output[0])

class HoushModelTest(TestCase):
    def test_holding_number_generation(self):
        division = Division.objects.create(name="TestDivision")
        district = District.objects.create(name="TestDistrict", division=division)
        upazila = Upazila.objects.create(name="TestUpazila", district=district)
        union = Union.objects.create(name="TestUnion", upazila=upazila)
        ward = Ward.objects.create(name="TestWard", union=union)
        house = Housh.objects.create(ward=ward, family_member=5)
        self.assertIsNotNone(house.holding_number)
