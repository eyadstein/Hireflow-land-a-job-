from django.utils import timezone
from .models import ProfileVerification


# Required fields and their weights (must all be filled for verification)
REQUIRED_FIELDS = {
    'has_name': 15,
    'has_email': 10,
    'has_phone': 10,
    'has_location': 10,
    'has_bio': 10,
    'has_skills': 15,
    'has_experience_level': 10,
    'has_education': 10,
    'has_desired_roles': 10,
    'has_gender': 5,
    # Optional (bonus points but not blocking)
    'has_profile_photo': 5,
    'has_linkedin': 3,
    'has_resume': 5,
    'has_portfolio': 2,
}

REQUIRED_FOR_VERIFICATION = [
    'has_name', 'has_email', 'has_phone', 'has_location',
    'has_bio', 'has_skills', 'has_experience_level',
    'has_education', 'has_desired_roles', 'has_gender',
]


def calculate_profile_completion(user):
    """
    Calculate profile completion percentage and
    update verification record.
    """
    verification, _ = ProfileVerification.objects.get_or_create(user=user)

    # Check each field
    checks = {
        'has_name': bool(user.first_name or user.last_name or user.username),
        'has_email': bool(user.email),
        'has_phone': bool(user.phone),
        'has_location': bool(user.location),
        'has_bio': bool(user.bio),
        'has_skills': bool(user.skills and len(user.skills) > 0),
        'has_experience_level': bool(user.experience_level),
        'has_education': bool(user.education),
        'has_desired_roles': bool(user.desired_roles and len(user.desired_roles) > 0),
        'has_gender': bool(user.gender),
        'has_profile_photo': bool(user.profile_photo),
        'has_linkedin': bool(user.linkedin_url),
        'has_resume': bool(user.resume_url),
        'has_portfolio': bool(user.portfolio_url),
    }

    # Calculate score
    total_score = 0
    for field, has_it in checks.items():
        if has_it:
            total_score += REQUIRED_FIELDS.get(field, 0)

    # Cap at 100
    completion = min(total_score, 100)

    # Update verification record
    for field, value in checks.items():
        setattr(verification, field, value)

    verification.completion_percentage = completion

    # Check if all required fields are filled
    all_required_filled = all(checks[f] for f in REQUIRED_FOR_VERIFICATION)

    if all_required_filled and completion >= 85:
        verification.status = 'verified'
        # Update user
        user.is_profile_verified = True
        user.profile_completion = completion
        # Assign badge
        assign_badge(user)
        user.verification_date = timezone.now()
        user.save()
    else:
        verification.status = 'incomplete'
        user.is_profile_verified = False
        user.profile_completion = completion
        user.badge = 'none'
        user.save()

    verification.save()
    return verification


def assign_badge(user):
    """Assign badge based on plan and gender."""
    if user.plan == 'pro':
        user.badge = 'gold'
    elif user.gender == 'female':
        user.badge = 'pink'
    else:
        user.badge = 'blue'


def get_missing_fields(user):
    """Return list of missing required fields."""
    verification = calculate_profile_completion(user)

    missing = []
    field_labels = {
        'has_name': 'Full Name',
        'has_email': 'Email Address',
        'has_phone': 'Phone Number',
        'has_location': 'Location',
        'has_bio': 'Bio / About Me',
        'has_skills': 'Skills (at least 1)',
        'has_experience_level': 'Experience Level',
        'has_education': 'Education',
        'has_desired_roles': 'Desired Job Roles',
        'has_gender': 'Gender',
    }

    for field in REQUIRED_FOR_VERIFICATION:
        if not getattr(verification, field):
            missing.append({
                'field': field.replace('has_', ''),
                'label': field_labels.get(field, field),
                'required': True,
            })

    return missing


def can_apply_to_job(user):
    """Check if user is allowed to apply to jobs."""
    if user.role == 'recruiter':
        return True, "Recruiters can always apply"

    if not user.is_profile_verified:
        verification = calculate_profile_completion(user)
        missing = get_missing_fields(user)
        return False, {
            'error': 'profile_not_verified',
            'message': 'Complete your profile to apply to jobs',
            'completion': verification.completion_percentage,
            'missing_fields': missing,
        }

    return True, "OK"