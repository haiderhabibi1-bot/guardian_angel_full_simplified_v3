
from django.contrib import admin
from .models import PublicQuestion, LawyerProfile, CustomerProfile, VerificationToken

@admin.register(PublicQuestion)
class PublicQuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "is_answered", "created_at", "answered_by")
    search_fields = ("title", "body")

@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialty", "years_experience", "bar_number", "approved")
    list_filter = ("approved", "specialty")
    search_fields = ("user__username", "bar_number", "specialty")

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username", "user__email")

@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at")
    search_fields = ("user__username", "token")
