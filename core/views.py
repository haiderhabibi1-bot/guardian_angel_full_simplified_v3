from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import views as auth_views

from .models import PublicQuestion, LawyerProfile, CustomerProfile, VerificationToken
from .forms import (
    PublicQuestionForm,
    CustomerRegistrationForm,
    LawyerRegistrationForm,
    CustomerSettingsForm,
    LawyerSettingsForm,
)

import secrets


# ----------------------
# Helper email functions
# ----------------------
def _send_verification_email(request, user):
    """
    Creates a one-time verification token and emails a link to the user.
    Account remains inactive until they click the link.
    """
    token = secrets.token_hex(32)
    VerificationToken.objects.create(user=user, token=token)
    verify_url = request.build_absolute_uri(reverse('verify_email', args=[token]))

    subject = 'Verify your Guardian Angel account'
    context = {'user': user, 'verify_url': verify_url}
    text_body = render_to_string('registration/verify_email.txt', context)
    html_body = render_to_string('registration/verify_email.html', context)

    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_body, "text/html")
    msg.send()


def _notify_admin_lawyer_registration(user, specialty, years_experience, bar_number, request=None):
    """
    Sends you an email when a lawyer signs up (for manual approval of bar cert etc.)
    Set ADMIN_REVIEW_EMAIL in env vars to receive this.
    """
    admin_email = getattr(settings, "ADMIN_REVIEW_EMAIL", "")
    if not admin_email:
        return

    lines = [
        "A new lawyer signed up:",
        "",
        f"Username: {user.username}",
        f"Email: {user.email}",
        f"Specialty: {specialty}",
        f"Years: {years_experience}",
        f"Bar #: {bar_number}",
    ]
    # Optional: include certificate URL if serving media publicly
    # if request is not None:
    #     lines.append(f"Certificate: {request.build_absolute_uri(user.lawyerprofile.bar_certificate.url)}")

    body = "\n".join(lines)
    send_mail(
        subject="New lawyer registration pending approval",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_email],
        fail_silently=True,
    )


# ------------
# Public pages
# ------------
def home(request):
    latest_questions = PublicQuestion.objects.filter(is_answered=True)[:5]
    lawyers = LawyerProfile.objects.filter(approved=True)[:6]
    return render(request, 'core/home.html', {'latest_questions': latest_questions, 'lawyers': lawyers})


def public_questions(request):
    if request.user.is_authenticated and hasattr(request.user, 'lawyerprofile'):
        questions = PublicQuestion.objects.all()
    else:
        questions = PublicQuestion.objects.filter(is_answered=True)
    return render(request, 'core/public_questions.html', {'questions': questions})


@login_required
def ask_public_question(request):
    if not hasattr(request.user, 'customerprofile'):
        messages.error(request, "Only customers can ask public questions.")
        return redirect('public_questions')

    if request.method == "POST":
        form = PublicQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.name = request.user.username
            q.email = request.user.email
            q.save()
            messages.success(request, "Your question has been submitted. Lawyers will review and answer.")
            return redirect('public_questions')
    else:
        form = PublicQuestionForm()

    return render(request, 'core/ask_public_question.html', {'form': form})


def lawyers_list(request):
    lawyers = LawyerProfile.objects.filter(approved=True)
    return render(request, 'core/lawyers_list.html', {'lawyers': lawyers})


def about(request):
    return render(request, 'core/about.html')


def switch_language(request):
    # The language is stored by middleware from ?lang=en|fr; we just bounce back.
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


# ------------------
# Authentication/Reg
# ------------------
def register_customer(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.create(user=user)
            _send_verification_email(request, user)
            messages.success(request, "Account created. Please verify your email to activate your account.")
            return redirect('login')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'core/register.html', {'form': form})


def register_lawyer(request):
    if request.method == "POST":
        form = LawyerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            lp = LawyerProfile.objects.create(
                user=user,
                specialty=form.cleaned_data['specialty'],
                years_experience=form.cleaned_data['years_experience'],
                bar_number=form.cleaned_data['bar_number'],
                bar_certificate=form.cleaned_data['bar_certificate'],
                approved=False,
            )
            _send_verification_email(request, user)
            _notify_admin_lawyer_registration(user, lp.specialty, lp.years_experience, lp.bar_number, request=request)
            messages.success(
                request,
                "Lawyer account submitted. Check your email to verify your account. "
                "Admin approval is required to appear publicly."
            )
            return redirect('login')
    else:
        form = LawyerRegistrationForm()
    return render(request, 'core/register_lawyer.html', {'form': form})


def verify_email(request, token):
    try:
        vt = VerificationToken.objects.get(token=token)
    except VerificationToken.DoesNotExist:
        messages.error(request, "Invalid or expired verification link.")
        return redirect('login')

    user = vt.user
    user.is_active = True
    user.save()
    vt.delete()

    messages.success(request, "Email verified. You can now log in.")
    return redirect('login')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Please verify your email before logging in.")
                return redirect('login')
            login(request, user)
            return redirect('home')
        messages.error(request, "Invalid username or password.")
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# --------------
# Settings pages
# --------------
@login_required
def settings_customer(request):
    if not hasattr(request.user, 'customerprofile'):
        messages.error(request, "Only customers can access customer settings.")
        return redirect('home')

    if request.method == "POST":
        form = CustomerSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            new_password = request.POST.get("new_password")
            if new_password:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Settings saved. Please log in again with your new password.")
                return redirect('login')
            messages.success(request, "Settings updated.")
            return redirect('settings_customer')
    else:
        form = CustomerSettingsForm(instance=request.user)

    return render(request, 'core/settings_customer.html', {'form': form})


@login_required
def settings_lawyer(request):
    if not hasattr(request.user, 'lawyerprofile'):
        messages.error(request, "Only lawyers can access lawyer settings.")
        return redirect('home')

    lp = request.user.lawyerprofile

    if request.method == "POST":
        form = LawyerSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

            lp.specialty = request.POST.get("specialty", lp.specialty)
            try:
                lp.years_experience = int(request.POST.get("years_experience", lp.years_experience))
            except Exception:
                pass

            if request.FILES.get("bar_certificate"):
                lp.bar_certificate = request.FILES["bar_certificate"]

            lp.save()

            new_password = request.POST.get("new_password")
            if new_password:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Settings saved. Please log in again with your new password.")
                return redirect('login')

            messages.success(request, "Settings updated.")
            return redirect('settings_lawyer')
    else:
        form = LawyerSettingsForm(
            instance=request.user,
            initial={'specialty': lp.specialty, 'years_experience': lp.years_experience},
        )

    return render(request, 'core/settings_lawyer.html', {'form': form, 'lp': lp})


# -------------------------
# Lawyer answering workflow
# -------------------------
@login_required
def answer_question(request, pk):
    if not hasattr(request.user, 'lawyerprofile'):
        messages.error(request, "Only lawyers can answer questions.")
        return redirect('public_questions')

    q = get_object_or_404(PublicQuestion, pk=pk)

    if request.method == "POST":
        answer_text = request.POST.get("answer_text", "").strip()
        if not answer_text:
            messages.error(request, "Answer cannot be empty.")
        else:
            q.answer_text = answer_text
            q.is_answered = True
            q.answered_by = request.user.lawyerprofile
            q.save()
            messages.success(request, "Answer posted.")
            return redirect('public_questions')

    return render(request, 'core/answer_question.html', {'q': q})


# --------------------------
# Password reset (built-ins)
# --------------------------
def password_reset_request(request):
    """
    Sends the password reset email using Django's built-in view,
    with our custom templates.
    """
    return auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/password-reset/done/',
    )(request)


def password_reset_done_view(request):
    return auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    )(request)


def password_reset_confirm_view(request, uidb64=None, token=None):
    return auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset/done/'
    )(request, uidb64=uidb64, token=token)


def password_reset_complete_view(request):
    return auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    )(request)
