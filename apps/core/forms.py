from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class SignupForm(UserCreationForm):
    honeypot = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'hidden'}))
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override default verbose/HTML help texts with concise plain text
        self.fields["password1"].help_text = "Use at least 8 characters and avoid personal info."
        self.fields["password2"].help_text = "Re-enter the password for confirmation."
        self.fields["honeypot"].label = ""

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get('honeypot') or '').strip():
            raise forms.ValidationError('Invalid submission.')
        return cleaned
