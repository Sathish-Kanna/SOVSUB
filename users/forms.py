from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator


class LoginForm(forms.Form):
    voter_id = forms.CharField(label='Voter ID', max_length=10, required=True)
    otp = forms.CharField(label='OTP', min_length=6, max_length=6, required=True)
    # image = forms.ImageField(label='Image')


class UserRegisterForm(UserCreationForm):
    username = forms.EmailField(max_length=100, required=True, label='E-mail')
    voter_id = forms.CharField(max_length=10)
    name = forms.CharField(max_length=100)
    booth_id = forms.CharField(max_length=10)
    phone_regex = RegexValidator(regex=r'^\+?\d{10,12}$',
                                 message='Phone number must be entered in the format: "+919876543210"')
    phone_number = forms.CharField(validators=[phone_regex], max_length=17)

    class Meta:
        model = User
        fields = ['username', 'voter_id', 'name', 'booth_id', 'phone_number']

    def __int__(self):
        self.fields['password1'].required = False
        self.fields['password2'].required = False
