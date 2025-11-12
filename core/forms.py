
from django import forms
from django.contrib.auth.models import User
from .models import PublicQuestion

class PublicQuestionForm(forms.ModelForm):
    class Meta:
        model = PublicQuestion
        fields = ["title", "body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 4})}

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password")
    class Meta:
        model = User
        fields = ["username", "email"]
    def clean(self):
        cd = super().clean()
        if cd.get("password") != cd.get("password_confirm"):
            raise forms.ValidationError("Passwords do not match.")
        return cd
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False  # require email verification
        if commit:
            user.save()
        return user

class LawyerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password")
    specialty = forms.CharField()
    years_experience = forms.IntegerField(min_value=0)
    bar_number = forms.CharField()
    bar_certificate = forms.FileField()
    class Meta:
        model = User
        fields = ["username", "email"]
    def clean(self):
        cd = super().clean()
        if cd.get("password") != cd.get("password_confirm"):
            raise forms.ValidationError("Passwords do not match.")
        return cd
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False  # require email verification
        if commit:
            user.save()
        return user

class CustomerSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

class LawyerSettingsForm(forms.ModelForm):
    specialty = forms.CharField()
    years_experience = forms.IntegerField(min_value=0)
    class Meta:
        model = User
        fields = ["username", "email"]
