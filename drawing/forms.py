from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username doesn't exist!")
        return username

    def clean_password(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("Username hasn't passed the validation!")
        password = self.cleaned_data['password']
        found_user = User.objects.get(username=username)
        if not found_user.check_password(password):
            raise forms.ValidationError("Wrong password!")
        return password


class SignUpForm(UserCreationForm):
    pass
