from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from home.models import Division, District, Upazila, Union, Ward, House, PasswordUtility

User = get_user_model()

class BaseUserForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

class UserCreationForm(UserCreationForm, BaseUserForm):
    name = forms.CharField(max_length=100, required=True)
    
    

    class Meta:
        model = User
        fields = ("name", "email", "password1", "password2")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.name = self.cleaned_data["name"]
        user.user_type = 'Public'
        if commit:
            user.save()
        return user
    
    
    
   
class LoginForm(forms.Form):
    # dont touch again

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class UpdatePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}),
        label="Current Password",
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        label="New Password",
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}),
        label="Confirm New Password",
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")

        return cleaned_data

class AddDivisionalCommissionerForm(BaseUserForm):
    name = forms.CharField(max_length=100, required=True)
    division = forms.ModelChoiceField(
        queryset=Division.objects.exclude(
            id__in=User.objects.filter(user_type='DivisionalCommissioner', division_id__isnull=False)
                                .values_list('division_id', flat=True)
        ),
        empty_label="Select Division",
        required=True
    )

    def save(self, commit=True):
        user = User(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
            user_type='DivisionalCommissioner',
            division=self.cleaned_data["division"]
        )

        raw_password = PasswordUtility.generate_password()
        user.set_password(raw_password)
        if commit:
            user.save()
            PasswordUtility.send_password_email(user.name, user.email, raw_password)

        return user

class AddDeputyCommissionerForm(BaseUserForm):
    name = forms.CharField(max_length=100, required=True)
    district = forms.ModelChoiceField(
        queryset=District.objects.none(), 
        empty_label="Select District",
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if self.user and self.user.user_type == 'DivisionalCommissioner':
            self.fields['district'].queryset = District.objects.filter(
                division=self.user.division
            ).exclude(
                id__in=User.objects.filter(user_type='DeputyCommissioner')
                                   .values_list('district_id', flat=True)
            )

    def save(self, commit=True):
        user = User(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
            user_type='DeputyCommissioner',
            district=self.cleaned_data["district"]
        )
        raw_password = PasswordUtility.generate_password()
        user.set_password(raw_password)
        if commit:
            user.save()
            PasswordUtility.send_password_email(user.name, user.email, raw_password)

        return user

class AddUNOForm(BaseUserForm):
    name = forms.CharField(max_length=100, required=True)
    upazila = forms.ModelChoiceField(
        queryset=Upazila.objects.none(), 
        empty_label="Select Upazila",
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if self.user and self.user.user_type == 'DeputyCommissioner':
            self.fields['upazila'].queryset = Upazila.objects.filter(
                district=self.user.district
            ).exclude(
                id__in=User.objects.filter(user_type='UNO')
                                   .values_list('upazila_id', flat=True)
            )

    def save(self, commit=True):
        user = User(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
            user_type='UNO',
            upazila=self.cleaned_data["upazila"]
        )
        raw_password = PasswordUtility.generate_password()
        user.set_password(raw_password)
        if commit:
            user.save()
            PasswordUtility.send_password_email(user.name, user.email, raw_password)

        return user

class AddUnionChairmanForm(BaseUserForm):
    name = forms.CharField(max_length=100, required=True)
    union = forms.ModelChoiceField(
        queryset=Union.objects.none(), 
        empty_label="Select Union",
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if self.user and self.user.user_type == 'UNO':
            self.fields['union'].queryset = Union.objects.filter(
                upazila=self.user.upazila
            ).exclude(
                id__in=User.objects.filter(user_type='UnionChairman')
                                   .values_list('union_id', flat=True)
            )

    def save(self, commit=True):
        user = User(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
            user_type='UnionChairman',
            union=self.cleaned_data["union"]
        )
        raw_password = PasswordUtility.generate_password()
        user.set_password(raw_password)
        if commit:
            user.save()
            PasswordUtility.send_password_email(user.name, user.email, raw_password)

        return user

class AddWardMemberForm(BaseUserForm):
    name = forms.CharField(max_length=100, required=True)
    ward = forms.ModelChoiceField(
        queryset=Ward.objects.none(), 
        empty_label="Select Ward",
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if self.user and self.user.user_type == 'UnionChairman':
            self.fields['ward'].queryset = Ward.objects.filter(
                union=self.user.union
            ).exclude(
                id__in=User.objects.filter(user_type='WardMember')
                                   .values_list('ward_id', flat=True)
            )

    def save(self, commit=True):
        user = User(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
            user_type='WardMember',
            ward=self.cleaned_data["ward"]
        )
        raw_password = PasswordUtility.generate_password()
        user.set_password(raw_password)
        if commit:
            user.save()
            PasswordUtility.send_password_email(user.name, user.email, raw_password)

        return user

class AddHouseForm(forms.ModelForm):
    family_member = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'min': '1'})
    )
    
    class Meta:
        model = House
        fields = ['family_member']

