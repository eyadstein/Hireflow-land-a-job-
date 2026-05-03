from datetime import datetime, timezone
from .models import ReferralCode, Referral


def get_or_create_referral_code(user):
    """Get existing referral code or create new one."""
    code, created = ReferralCode.objects.get_or_create(user=user)
    return code


def process_referral(referred_user, referral_code):
    """
    Process a referral when a new user registers with a code.
    Returns True if successful, False if invalid code.
    """
    try:
        code_obj = ReferralCode.objects.get(code=referral_code.upper())
    except ReferralCode.DoesNotExist:
        return False

    referrer = code_obj.user

    # Can't refer yourself
    if referrer == referred_user:
        return False

    # Already referred
    if Referral.objects.filter(
        referrer=referrer,
        referred=referred_user
    ).exists():
        return False

    # Create referral
    Referral.objects.create(
        referrer=referrer,
        referred=referred_user,
        code_used=referral_code.upper(),
        status='completed',
    )

    # Check if referrer deserves reward (3 completed referrals = pro)
    check_and_reward(referrer)
    return True


def check_and_reward(user):
    """Upgrade user to pro if they have 3+ completed referrals."""
    completed = Referral.objects.filter(
        referrer=user,
        status='completed'
    ).count()

    if completed >= 3 and user.plan == 'free':
        user.plan = 'pro'
        user.save()

        # Mark referrals as rewarded
        Referral.objects.filter(
            referrer=user,
            status='completed'
        ).update(
            status='rewarded',
            rewarded_at=datetime.now(timezone.utc)
        )
        return True
    return False


def get_referral_stats(user):
    """Get full referral stats for a user."""
    code = get_or_create_referral_code(user)
    referrals = Referral.objects.filter(referrer=user)

    return {
        'referral_code': code.code,
        'referral_link': f"https://hireflow.app/register?ref={code.code}",
        'total_referrals': referrals.count(),
        'completed': referrals.filter(status='completed').count(),
        'rewarded': referrals.filter(status='rewarded').count(),
        'pending': referrals.filter(status='pending').count(),
        'referrals_needed_for_pro': max(0, 3 - referrals.filter(
            status__in=['completed', 'rewarded']
        ).count()),
        'is_pro': user.plan == 'pro',
    }