from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Application, CandidateNote
from .serializers import ApplicationSerializer, CandidateNoteSerializer

User = get_user_model()


ACTIVE_STATUSES = ["pending", "applied", "screening", "interview", "offer"]
FINAL_STATUSES = ["accepted", "rejected", "withdrawn"]
RECRUITER_DECISION_STATUSES = [
    "pending",
    "applied",
    "screening",
    "interview",
    "offer",
    "accepted",
    "rejected",
    "withdrawn",
]


def is_recruiter_user(user):
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_staff
            or getattr(user, "role", None) in ["recruiter", "company", "admin"]
        )
    )


def get_recruiter_job_ids(user):
    from jobs.models import Job

    return Job.objects.filter(posted_by=user).values_list("id", flat=True)


def get_owned_job_or_404(user, job_id):
    from jobs.models import Job

    return get_object_or_404(Job, id=job_id, posted_by=user)


def stamp_review_time(old_status, new_status, current_reviewed_at):
    if old_status != new_status:
        return timezone.now()

    return current_reviewed_at


class IsJobOwner(permissions.BasePermission):
    message = "Only the recruiter who owns the job can update this application."

    def has_object_permission(self, request, view, obj):
        if not obj.job:
            return obj.applicant == request.user or request.user.is_staff

        return obj.job.posted_by == request.user or request.user.is_staff


class ApplyView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        job_id = request.data.get("job") or request.data.get("job_id")

        if not job_id:
            return Response(
                {"detail": "job is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from jobs.models import Job

        job = get_object_or_404(Job, id=job_id)

        existing = Application.objects.filter(
            applicant=request.user,
            job=job,
        ).first()

        if existing:
            return Response(
                {
                    "detail": "You have already applied to this job.",
                    "application": ApplicationSerializer(existing).data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        application = Application.objects.create(
            applicant=request.user,
            job=job,
            job_title=job.title,
            company=job.company,
            status="pending",
            applied_date=timezone.now().date(),
        )

        return Response(
            ApplicationSerializer(application).data,
            status=status.HTTP_201_CREATED,
        )


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Application.objects
            .filter(applicant=self.request.user)
            .select_related("job", "applicant", "job__posted_by")
            .order_by("-updated_at", "-created_at")
        )


class JobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs["job_id"]
        job = get_owned_job_or_404(self.request.user, job_id)

        return (
            Application.objects
            .filter(job=job)
            .select_related("job", "applicant", "job__posted_by")
            .order_by("-created_at")
        )


class UpdateStatusView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]
    queryset = Application.objects.select_related("job", "applicant", "job__posted_by").all()

    def update(self, request, *args, **kwargs):
        application = self.get_object()

        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {"error": "status is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_status not in RECRUITER_DECISION_STATUSES:
            return Response(
                {"error": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = application.status
        application.status = new_status
        application.reviewed_at = stamp_review_time(
            old_status,
            new_status,
            application.reviewed_at,
        )
        application.save()

        return Response(ApplicationSerializer(application).data)


class CandidateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        candidate = get_object_or_404(User, id=user_id)
        my_job_ids = get_recruiter_job_ids(request.user)

        apps = (
            Application.objects
            .filter(applicant=candidate, job_id__in=my_job_ids)
            .select_related("job", "applicant", "job__posted_by")
            .order_by("-created_at")
        )

        notes_count = CandidateNote.objects.filter(
            candidate=candidate,
            recruiter=request.user,
        ).count()

        return Response({
            "user_id": candidate.id,
            "username": candidate.username,
            "email": candidate.email,
            "first_name": candidate.first_name or "",
            "last_name": candidate.last_name or "",
            "total_applications": apps.count(),
            "pending": apps.filter(status="pending").count(),
            "applied": apps.filter(status="applied").count(),
            "screening": apps.filter(status="screening").count(),
            "interview": apps.filter(status="interview").count(),
            "offer": apps.filter(status="offer").count(),
            "accepted": apps.filter(status="accepted").count(),
            "rejected": apps.filter(status="rejected").count(),
            "withdrawn": apps.filter(status="withdrawn").count(),
            "first_applied": apps.last().created_at.isoformat() if apps.exists() else None,
            "last_applied": apps.first().created_at.isoformat() if apps.exists() else None,
            "applications": ApplicationSerializer(apps, many=True).data,
            "notes_count": notes_count,
        })


class CandidateTimelineView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        candidate = get_object_or_404(User, id=user_id)
        my_job_ids = get_recruiter_job_ids(request.user)

        apps = (
            Application.objects
            .filter(applicant=candidate, job_id__in=my_job_ids)
            .select_related("job")
        )

        notes = CandidateNote.objects.filter(
            candidate=candidate,
            recruiter=request.user,
        )

        timeline = []

        for app in apps:
            timeline.append({
                "type": "application",
                "date": app.created_at.isoformat(),
                "description": f"Applied to {app.job.title if app.job else app.job_title}",
                "status": app.status,
                "job_id": app.job.id if app.job else None,
                "application_id": app.id,
            })

            if app.reviewed_at:
                timeline.append({
                    "type": "decision",
                    "date": app.reviewed_at.isoformat(),
                    "description": f"Status changed to {app.status}",
                    "status": app.status,
                    "job_id": app.job.id if app.job else None,
                    "application_id": app.id,
                })

        for note in notes:
            timeline.append({
                "type": "note",
                "date": note.created_at.isoformat(),
                "description": note.content[:150],
                "note_id": note.id,
            })

        timeline.sort(key=lambda item: item["date"], reverse=True)

        return Response({
            "candidate_id": candidate.id,
            "candidate_name": candidate.username,
            "timeline": timeline,
        })


class CandidateNotesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        candidate = get_object_or_404(User, id=user_id)

        notes = CandidateNote.objects.filter(
            candidate=candidate,
            recruiter=request.user,
        )

        return Response(CandidateNoteSerializer(notes, many=True).data)

    def post(self, request, user_id):
        candidate = get_object_or_404(User, id=user_id)
        content = request.data.get("content", "").strip()

        if not content:
            return Response(
                {"error": "Note content is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        note = CandidateNote.objects.create(
            candidate=candidate,
            recruiter=request.user,
            content=content,
        )

        return Response(
            CandidateNoteSerializer(note).data,
            status=status.HTTP_201_CREATED,
        )


class NoteDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_note(self, note_id, user):
        return get_object_or_404(CandidateNote, id=note_id, recruiter=user)

    def put(self, request, note_id):
        note = self.get_note(note_id, request.user)
        content = request.data.get("content", "").strip()

        if not content:
            return Response(
                {"error": "Note content is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        note.content = content
        note.save()

        return Response(CandidateNoteSerializer(note).data)

    def delete(self, request, note_id):
        note = self.get_note(note_id, request.user)
        note.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


def build_candidate_comparison_profile(candidate, recruiter_job_ids):
    apps = (
        Application.objects
        .filter(applicant=candidate, job_id__in=recruiter_job_ids)
        .select_related("job", "applicant")
    )

    total = apps.count()
    pending = apps.filter(status="pending").count()
    applied = apps.filter(status="applied").count()
    screening = apps.filter(status="screening").count()
    interview = apps.filter(status="interview").count()
    offer = apps.filter(status="offer").count()
    accepted = apps.filter(status="accepted").count()
    rejected = apps.filter(status="rejected").count()
    withdrawn = apps.filter(status="withdrawn").count()

    score = 40
    score += accepted * 20
    score += offer * 12
    score += interview * 8
    score += screening * 5
    score += total * 5
    score -= rejected * 7
    score -= withdrawn * 4
    score = max(0, min(score, 100))

    if score >= 80:
        tier = "star"
    elif score >= 60:
        tier = "strong"
    elif score >= 40:
        tier = "average"
    else:
        tier = "below_average"

    return {
        "user_id": candidate.id,
        "username": candidate.username,
        "email": candidate.email,
        "first_name": candidate.first_name or "",
        "last_name": candidate.last_name or "",
        "score": score,
        "tier": tier,
        "stats": {
            "total_applications": total,
            "pending": pending,
            "applied": applied,
            "screening": screening,
            "interview": interview,
            "offer": offer,
            "accepted": accepted,
            "rejected": rejected,
            "withdrawn": withdrawn,
        },
        "applications": ApplicationSerializer(apps, many=True).data,
    }


class CompareCandidatesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        candidate_ids = request.data.get("candidate_ids", [])
        application_ids = request.data.get("application_ids", [])

        my_job_ids = list(get_recruiter_job_ids(request.user))

        if application_ids:
            selected_apps = Application.objects.filter(
                id__in=application_ids,
                job_id__in=my_job_ids,
            )

            candidate_ids = list(
                selected_apps
                .values_list("applicant_id", flat=True)
                .distinct()
            )

        if not candidate_ids or len(candidate_ids) < 2:
            return Response(
                {"error": "Select at least two candidates to compare."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(candidate_ids) > 4:
            return Response(
                {"error": "You can compare up to four candidates only."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        candidates = User.objects.filter(id__in=candidate_ids)

        profiles = [
            build_candidate_comparison_profile(candidate, my_job_ids)
            for candidate in candidates
        ]

        profiles.sort(key=lambda item: item["score"], reverse=True)

        for index, profile in enumerate(profiles):
            profile["rank"] = index + 1

        return Response({
            "total_compared": len(profiles),
            "candidates": profiles,
            "recommended": profiles[0] if profiles else None,
        })


class BulkDecisionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        application_ids = request.data.get("application_ids", [])
        decision = request.data.get("decision", "")

        if not application_ids or not isinstance(application_ids, list):
            return Response(
                {"error": "Provide a list of application_ids."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if decision not in RECRUITER_DECISION_STATUSES:
            return Response(
                {"error": "Invalid decision."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        my_job_ids = get_recruiter_job_ids(request.user)

        apps = Application.objects.filter(
            id__in=application_ids,
            job_id__in=my_job_ids,
        )

        if not apps.exists():
            return Response(
                {"error": "No valid applications found for the given IDs."},
                status=status.HTTP_404_NOT_FOUND,
            )

        updated_count = apps.count()
        updated_ids = list(apps.values_list("id", flat=True))

        apps.update(
            status=decision,
            reviewed_at=timezone.now(),
        )

        updated_apps = (
            Application.objects
            .filter(id__in=updated_ids)
            .select_related("job", "applicant", "job__posted_by")
        )

        return Response({
            "decision": decision,
            "updated_count": updated_count,
            "updated_ids": updated_ids,
            "applications": ApplicationSerializer(updated_apps, many=True).data,
            "message": f"{updated_count} application(s) updated to {decision}.",
        })


class RejectAllPendingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        job = get_owned_job_or_404(request.user, job_id)

        pending_apps = Application.objects.filter(job=job, status="pending")
        count = pending_apps.count()

        pending_apps.update(
            status="rejected",
            reviewed_at=timezone.now(),
        )

        return Response({
            "job_id": job.id,
            "job_title": job.title,
            "rejected_count": count,
            "message": f"Rejected {count} pending application(s).",
        })


class RejectAllActiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        job = get_owned_job_or_404(request.user, job_id)

        active_apps = Application.objects.filter(
            job=job,
            status__in=ACTIVE_STATUSES,
        )

        count = active_apps.count()

        active_apps.update(
            status="rejected",
            reviewed_at=timezone.now(),
        )

        return Response({
            "job_id": job.id,
            "job_title": job.title,
            "rejected_count": count,
            "message": f"Rejected {count} active application(s).",
        })


class AcceptTopCandidatesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        job = get_owned_job_or_404(request.user, job_id)

        try:
            top_n = int(request.data.get("top_n", 1))
        except (TypeError, ValueError):
            return Response(
                {"error": "top_n must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if top_n < 1:
            return Response(
                {"error": "top_n must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_apps = Application.objects.filter(
            job=job,
            status__in=ACTIVE_STATUSES,
        ).order_by("created_at")

        to_accept = list(active_apps[:top_n].values_list("id", flat=True))
        to_reject = list(active_apps[top_n:].values_list("id", flat=True))

        now = timezone.now()

        Application.objects.filter(id__in=to_accept).update(
            status="accepted",
            reviewed_at=now,
        )

        Application.objects.filter(id__in=to_reject).update(
            status="rejected",
            reviewed_at=now,
        )

        return Response({
            "job_id": job.id,
            "job_title": job.title,
            "accepted_count": len(to_accept),
            "rejected_count": len(to_reject),
            "accepted_ids": to_accept,
            "rejected_ids": to_reject,
            "message": f"Accepted {len(to_accept)} and rejected {len(to_reject)} application(s).",
        })


class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Application.objects
            .filter(applicant=self.request.user)
            .select_related("job", "applicant", "job__posted_by")
            .order_by("-updated_at", "-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(
            applicant=self.request.user,
            applied_date=timezone.now().date(),
        )


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Application.objects
            .filter(applicant=self.request.user)
            .select_related("job", "applicant", "job__posted_by")
        )