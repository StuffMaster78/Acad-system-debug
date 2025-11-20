# services/progress.py

from class_management.models import ProgressReport

def submit_progress(session, tutor, data):
    return ProgressReport.objects.create(
        session=session,
        tutor=tutor,
        **data
    )

def get_progress_for_bundle(bundle):
    return ProgressReport.objects.filter(
        session__bundle=bundle
    ).select_related('session', 'tutor')