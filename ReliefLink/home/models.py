# home/models.py
import json, math
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.db.models import Sum
import random
import string
import logging

logger = logging.getLogger(__name__)

# Define the custom user manager
class CustomUserManager(BaseUserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Division(models.Model):
    name = models.CharField(max_length=100)
    floody_districts = models.TextField(default='[]')
    
    dry_food_demand = models.IntegerField(default=0)
    primary_food_demand = models.IntegerField(default=0)

    dry_food_supply = models.IntegerField(default=0)
    primary_food_supply = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def add_floody_district(self, district_id):
        floody_districts = self.get_floody_districts()
        if district_id not in floody_districts:
            floody_districts.append(district_id)
            self.set_floody_districts(floody_districts)
            self.update_relief_demand()
        else:
            self.update_relief_demand()


    def remove_floody_district(self, district_id):
        floody_districts = self.get_floody_districts()
        if district_id in floody_districts:
            floody_districts.remove(district_id)
            self.set_floody_districts(floody_districts)
            self.update_relief_demand()
        

    def update_relief_demand(self):
        """Recalculates relief demand based on current floody wards."""
        floody_districts = self.get_floody_districts()
        self.dry_food_demand = District.objects.filter(id__in=floody_districts).aggregate(Sum('dry_food_demand'))['dry_food_demand__sum'] or 0

        self.primary_food_demand = District.objects.filter(id__in=floody_districts).aggregate(Sum('primary_food_demand'))['primary_food_demand__sum'] or 0

        self.dry_food_supply = District.objects.filter(id__in=floody_districts).aggregate(Sum('dry_food_supply'))['dry_food_supply__sum'] or 0

        self.primary_food_supply = District.objects.filter(id__in=floody_districts).aggregate(Sum('primary_food_supply'))['primary_food_supply__sum'] or 0

        self.save()

    def get_floody_districts(self):
        try:
            return json.loads(self.floody_districts)
        except json.JSONDecodeError:
            return []

    def set_floody_districts(self, district_ids):
        self.floody_districts = json.dumps(district_ids)
        self.save()

class District(models.Model):
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    floody_upazilas = models.TextField(default='[]')

    dry_food_demand = models.IntegerField(default=0)
    primary_food_demand = models.IntegerField(default=0)

    dry_food_supply = models.IntegerField(default=0)
    primary_food_supply = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def add_floody_upazila(self, upazila_id):
        floody_upazilas = self.get_floody_upazilas()
        if upazila_id not in floody_upazilas:
            floody_upazilas.append(upazila_id)
            self.set_floody_upazilas(floody_upazilas)
            self.update_relief_demand()
            self.division.add_floody_district(self.id)
        else:
            self.update_relief_demand()
            self.division.add_floody_district(self.id)


    def remove_floody_upazila(self, upazila_id):
        floody_upazilas = self.get_floody_upazilas()
        if upazila_id in floody_upazilas:
            floody_upazilas.remove(upazila_id)
            self.set_floody_upazilas(floody_upazilas)
            self.update_relief_demand()
            self.division.remove_floody_district(self.id)

    
    def update_relief_demand(self):
        """Recalculates relief demand based on current floody wards."""
        floody_upazilas = self.get_floody_upazilas()
        self.dry_food_demand = Upazila.objects.filter(id__in=floody_upazilas).aggregate(Sum('dry_food_demand'))['dry_food_demand__sum'] or 0

        self.primary_food_demand = Upazila.objects.filter(id__in=floody_upazilas).aggregate(Sum('primary_food_demand'))['primary_food_demand__sum'] or 0

        self.dry_food_supply = Upazila.objects.filter(id__in=floody_upazilas).aggregate(Sum('dry_food_supply'))['dry_food_supply__sum'] or 0

        self.primary_food_supply = Upazila.objects.filter(id__in=floody_upazilas).aggregate(Sum('primary_food_supply'))['primary_food_supply__sum'] or 0
        self.save()

    def get_floody_upazilas(self):
        try:
            return json.loads(self.floody_upazilas)
        except json.JSONDecodeError:
            return []

    def set_floody_upazilas(self, upazila_ids):
        self.floody_upazilas = json.dumps(upazila_ids)
        self.save()

class Upazila(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    floody_unions = models.TextField(default='[]')

    dry_food_demand = models.IntegerField(default=0)
    primary_food_demand = models.IntegerField(default=0)

    dry_food_supply = models.IntegerField(default=0)
    primary_food_supply = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def add_floody_union(self, union_id):
        floody_unions = self.get_floody_unions()
        
        if union_id not in floody_unions:
            floody_unions.append(union_id)
            self.set_floody_unions(floody_unions)
            self.update_relief_demand()
            self.district.add_floody_upazila(self.id)
        else:
            self.update_relief_demand()
            self.district.add_floody_upazila(self.id)

        
    def remove_floody_union(self, union_id):
        floody_unions = self.get_floody_unions()
        if union_id in floody_unions:
            floody_unions.remove(union_id)
            self.set_floody_unions(floody_unions)
            self.update_relief_demand()
            self.district.remove_floody_upazila(self.id)
        

    def update_relief_demand(self):
        floody_unions = self.get_floody_unions()

        self.dry_food_demand = Union.objects.filter(id__in=floody_unions).aggregate(Sum('dry_food_demand'))['dry_food_demand__sum'] or 0

        self.primary_food_demand = Union.objects.filter(id__in=floody_unions).aggregate(Sum('primary_food_demand'))['primary_food_demand__sum'] or 0

        self.dry_food_supply = Union.objects.filter(id__in=floody_unions).aggregate(Sum('dry_food_supply'))['dry_food_supply__sum'] or 0

        self.primary_food_supply = Union.objects.filter(id__in=floody_unions).aggregate(Sum('primary_food_supply'))['primary_food_supply__sum'] or 0
        
        self.save()
        

    def get_floody_unions(self):
        try:
            return json.loads(self.floody_unions)
        except json.JSONDecodeError:
            return []

    def set_floody_unions(self, union_ids):
        self.floody_unions = json.dumps(union_ids)
        self.save()

class Union(models.Model):
    name = models.CharField(max_length=100)
    upazila = models.ForeignKey(Upazila, on_delete=models.CASCADE)
    floody_wards = models.TextField(default='[]')
    dry_food_demand = models.IntegerField(default=0)
    primary_food_demand = models.IntegerField(default=0)
    dry_food_supply = models.IntegerField(default=0)
    primary_food_supply = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def add_floody_ward(self, ward_id):
        floody_wards = self.get_floody_wards()
        if ward_id not in floody_wards:
            floody_wards.append(ward_id)
            self.set_floody_wards(floody_wards)
            self.update_relief_demand()
            self.upazila.add_floody_union(self.id)
        else:
            # print("cole")
            self.update_relief_demand()
            self.upazila.add_floody_union(self.id)
        


    def remove_floody_ward(self, ward_id):
        floody_wards = self.get_floody_wards()
        if ward_id in floody_wards:
            floody_wards.remove(ward_id)
            self.set_floody_wards(floody_wards)
            self.update_relief_demand()
            self.upazila.remove_floody_union(self.id)
        

    def update_relief_demand(self):
        
        floody_wards = self.get_floody_wards()

        self.dry_food_demand = Ward.objects.filter(id__in=floody_wards).aggregate(Sum('dry_food_demand'))['dry_food_demand__sum'] or 0

        self.primary_food_demand = Ward.objects.filter(id__in=floody_wards).aggregate(Sum('primary_food_demand'))['primary_food_demand__sum'] or 0

        self.dry_food_supply = Ward.objects.filter(id__in=floody_wards).aggregate(Sum('dry_food_supply'))['dry_food_supply__sum'] or 0

        self.primary_food_supply = Ward.objects.filter(id__in=floody_wards).aggregate(Sum('primary_food_supply'))['primary_food_supply__sum'] or 0

        self.save()

    def get_floody_wards(self):
        try:
            return json.loads(self.floody_wards)
        except json.JSONDecodeError:
            return []

    def set_floody_wards(self, ward_ids):
        self.floody_wards = json.dumps(ward_ids)
        self.save()

class Ward(models.Model):
    name = models.CharField(max_length=100)
    union = models.ForeignKey(Union, on_delete=models.CASCADE)

    is_flood = models.BooleanField(default=False)

    relief_demand = models.IntegerField(default=0)
    dry_food_demand = models.IntegerField(default=0)
    primary_food_demand = models.IntegerField(default=0)
    dry_food_demand_in_percentage = models.IntegerField(default=0)

    dry_food_supply = models.IntegerField(default=0)
    primary_food_supply = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def relief_supply(self, relief, relief_type):
        self.relief_demand -= relief
        if relief_type == 'dry':
            self.dry_food_supply += relief
            self.dry_food_demand -= relief
        else:
            self.primary_food_supply += relief
            self.primary_food_demand -= relief
        
        self.save()
        self.union.add_floody_ward(self.id)



    def propagate_flood_status(self):
        if self.is_flood:
            self.relief_demand = Housh.objects.filter(ward=self).aggregate(Sum('relief_demand'))['relief_demand__sum'] or 0
            # print(self.dry_food_demand_in_percentage)
            self.dry_food_demand = math.ceil((self.relief_demand * self.dry_food_demand_in_percentage) / 100)
            self.primary_food_demand = self.relief_demand - self.dry_food_demand
            self.save()
            self.union.add_floody_ward(self.id)


    def propagate_flood_remove_status(self):
        """Propagate the flood remove status to all related parent entities."""
        if not self.is_flood:
            self.union.remove_floody_ward(self.id)

class Housh(models.Model):
    holding_number = models.CharField(max_length=20, blank=True, null=True)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    family_member = models.IntegerField()
    relief_demand = models.IntegerField()
    dry_food_supply = models.IntegerField(default=0)
    primary_food_supply = models.IntegerField(default= 0)

    def save(self, *args, **kwargs):
        # Ensure relief_demand is initialized properly
        if self.relief_demand is None:
            self.relief_demand = self.family_member
        self.relief_demand = self.family_member

        # Deduct relief_supply if not None
        if self.dry_food_supply is not None or self.primary_food_supply is not None:
            self.relief_demand -= (self.dry_food_supply + self.primary_food_supply)

        # Generate holding_number if it doesn't exist
        if not self.holding_number:
            try:
                division_code = self.ward.union.upazila.district.division.name[:2].lower()
                district_code = self.ward.union.upazila.district.name[:2].lower()
                upazila_code = self.ward.union.upazila.name[:2].lower()
                union_code = self.ward.union.name[:2].lower()
                ward_code = self.ward.name[:2].lower()

                # Ensure correct counting
                house_count = Housh.objects.filter(ward=self.ward).exclude(pk=self.pk).count() + 1
                self.holding_number = f"{division_code}{district_code}{upazila_code}{union_code}{ward_code}{house_count}"
            except AttributeError as e:
                logger.error(f"Holding number generation failed: {e}")
                raise ValueError("Invalid data for holding number generation.")

        super().save(*args, **kwargs)

    def ReliefSupply(self, relief, relief_type):
        if relief_type == 'dry':
            self.dry_food_supply += relief
        else:
            self.primary_food_supply += relief
        Housh.save(self)

        self.ward.relief_supply(relief, relief_type)




class PasswordUtility:
    @staticmethod
    def generate_password(length=None):
        """Generate a random password."""
        length = length or getattr(settings, 'PASSWORD_LENGTH', 8)  # Default length is 8
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def send_password_email(name, email, raw_password):
        """Send the generated password to the user's email."""
        subject = "Your Account Password"
        message = (
            f"Hello {name},\n\n"
            f"Your account has been created. Here is your temporary password:\n\n"
            f"{raw_password}\n\n"
            f"Please log in and change your password immediately."
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('Admin', 'Admin'),
        ('DivisionalCommissioner', 'Divisional Commissioner'),
        ('DeputyCommissioner', 'Deputy Commissioner'),
        ('UNO', 'UNO'),
        ('UnionChairman', 'Union Chairman'),
        ('WardMember', 'Ward Member'),
        ('Public', 'Public'),
    )
    username = None  # Remove the default username field
    email = models.EmailField(unique=True)  # Use email as the username
    name = models.CharField(max_length=100, blank=False, null=False)
    user_type = models.CharField(max_length=30, choices=USER_TYPES)
    
    # Place relationships
    division = models.OneToOneField(
        'Division', null=True, blank=True, on_delete=models.SET_NULL
    )
    district = models.OneToOneField(
        'District', null=True, blank=True, on_delete=models.SET_NULL
    )
    upazila = models.OneToOneField(
        'Upazila', null=True, blank=True, on_delete=models.SET_NULL
    )
    union = models.OneToOneField(
        'Union', null=True, blank=True, on_delete=models.SET_NULL
    )
    ward = models.OneToOneField(
        'Ward', null=True, blank=True, on_delete=models.SET_NULL
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type']

    class Meta:
        permissions = [
            ("can_add_user", "Can add a user"),
            ("can_remove_user", "Can remove a user"),
        ]

    objects = CustomUserManager()

    def clean(self):
        """
        Enforce the rules based on user_type.
        """
        super().clean()
        
        if self.user_type == 'DivisionalCommissioner' and not self.division:
            raise ValidationError("A Divisional Commissioner must be linked to a Division.")
        if self.user_type == 'DeputyCommissioner' and not self.district:
            raise ValidationError("A Deputy Commissioner must be linked to a District.")
        if self.user_type == 'UNO' and not self.upazila:
            raise ValidationError("A UNO must be linked to an Upazila.")
        if self.user_type == 'UnionChairman' and not self.union:
            raise ValidationError("A Union Chairman must be linked to a Union.")
        if self.user_type == 'WardMember' and not self.ward:
            raise ValidationError("A Ward Member must be linked to a Ward.")
        
        # Ensure admin and other types do not have place fields set
        if self.user_type in ['Admin', 'Public']:
            if any([self.division, self.district, self.upazila, self.union, self.ward]):
                raise ValidationError(f"A user of type {self.user_type} should not be linked to any place field.")

    def __str__(self):
        return f"{self.name} ({self.user_type})"


@receiver(post_save, sender=CustomUser)
def handle_new_user(sender, instance, created, **kwargs):
    if created:
        raw_password = PasswordUtility.generate_password()
        instance.set_password(raw_password)
        instance.save(update_fields=['password'])
        PasswordUtility.send_password_email(instance.name, instance.email, raw_password)

        if instance.user_type not in ['Public'] and instance.user_type in [
            'Admin', 'DivisionalCommissioner', 'DeputyCommissioner',
            'UNO', 'UnionChairman', 'WardMember',
        ]:
            instance.user_permissions.add(
                Permission.objects.get(codename='can_add_user'),
                Permission.objects.get(codename='can_remove_user'),
            )
