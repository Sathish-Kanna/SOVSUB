from django import forms


class LoginForm(forms.Form):
    voter_id = forms.CharField(label='Voter ID', max_length=10, required=True)
    otp = forms.CharField(label='OTP', min_length=6, max_length=6, required=True)
    image = forms.ImageField(label='Image', required=True)
