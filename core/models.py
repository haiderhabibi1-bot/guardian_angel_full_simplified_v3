
from django.db import models
from django.contrib.auth.models import User

class PublicQuestion(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)
    answer_text = models.TextField(blank=True)
    answered_by = models.ForeignKey('LawyerProfile', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class LawyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=200)
    years_experience = models.PositiveIntegerField()
    bar_number = models.CharField(max_length=100)
    bar_certificate = models.FileField(upload_to='bar_certificates/')
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.specialty})"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username

class VerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.token}"
