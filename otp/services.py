import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import OTP


def generate_otp_code():
    return ''.join(random.choices(string.digits, k=6))


def create_otp(user, otp_type, purpose='verify'):
    """Create a new OTP and invalidate old ones."""
    # Invalidate existing OTPs
    OTP.objects.filter(
        user=user,
        otp_type=otp_type,
        purpose=purpose,
        is_used=False
    ).update(is_used=True)

    # Create new OTP
    otp = OTP.objects.create(
        user=user,
        code=generate_otp_code(),
        otp_type=otp_type,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(
            minutes=settings.OTP_EXPIRY_MINUTES
        )
    )
    return otp


def send_email_otp(user, purpose='verify'):
    """Send OTP via email."""
    otp = create_otp(user, 'email', purpose)

    subject_map = {
        'verify': 'Verify your HireFlow email',
        'reset': 'Reset your HireFlow password',
        'login': 'Your HireFlow login code',
    }

    message = f"""
Hi {user.first_name or user.username},

Your HireFlow verification code is:

    {otp.code}

This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.

If you didn't request this, please ignore this email.

Best regards,
The HireFlow Team
"""
    try:
        send_mail(
            subject=subject_map.get(purpose, 'Your HireFlow code'),
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True, otp
    except Exception as e:
        return False, str(e)


def send_sms_otp(user, purpose='verify'):
    """Send OTP via SMS using Africa's Talking."""
    if not user.phone:
        return False, "No phone number on file"

    otp = create_otp(user, 'phone', purpose)

    try:
        import africastalking
        africastalking.initialize(
            settings.AFRICASTALKING_USERNAME,
            settings.AFRICASTALKING_API_KEY
        )
        sms = africastalking.SMS
        sms.send(
            f"Your HireFlow code is: {otp.code}. Expires in {settings.OTP_EXPIRY_MINUTES} minutes.",
            [user.phone]
        )
        return True, otp
    except Exception as e:
        return False, str(e)


def verify_otp(user, code, otp_type, purpose='verify'):
    """
    Verify an OTP code.
    Returns (success, message)
    """
    try:
        otp = OTP.objects.filter(
            user=user,
            otp_type=otp_type,
            purpose=purpose,
            is_used=False,
        ).latest('created_at')
    except OTP.DoesNotExist:
        return False, "No OTP found. Please request a new one."

    # Check expiry
    if otp.is_expired():
        return False, "OTP has expired. Please request a new one."

    # Check attempts (max 5)
    if otp.attempts >= 5:
        otp.is_used = True
        otp.save()
        return False, "Too many attempts. Please request a new OTP."

    # Check code
    if otp.code != code:
        otp.attempts += 1
        otp.save()
        remaining = 5 - otp.attempts
        return False, f"Invalid code. {remaining} attempts remaining."

    # Mark as used and verified
    otp.is_used = True
    otp.is_verified = True
    otp.save()

    # Update user verification status
    if otp_type == 'email':
        user.is_active = True
        user.save()
    elif otp_type == 'phone':
        user.phone = user.phone
        user.save()

    # Trigger profile verification check
    from verification.services import calculate_profile_completion
    calculate_profile_completion(user)

    return True, "Verified successfully!"