from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=150, label="Full name",
        widget=forms.TextInput(attrs={'autocomplete': 'name'}))
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords do not match.")
        elif p1:
            try:
                validate_password(p1)      # Django's built-in rules (min 8 chars, etc.)
            except forms.ValidationError as e:
                self.add_error('password1', e)
        return cleaned

    def save(self):
        data = self.cleaned_data
        first, _, last = data['full_name'].strip().partition(' ')
        return User.objects.create_user(
            username=data['email'],        # the email is used as the username
            email=data['email'],
            password=data['password1'],
            first_name=first,
            last_name=last,
        )


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email address",
        widget=forms.EmailInput(attrs={'autofocus': True, 'autocomplete': 'email'}))
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))

    def clean_username(self):
        return self.cleaned_data['username'].lower()