from django.db.models import Q

from treeherder.model.models import Job
from treeherder.push_health.utils import mark_failed_in_parent, job_to_dict


def get_lint_failures(push, parent_push=None):
    lint_failures = Job.objects.filter(
        Q(machine_platform__platform='lint') | Q(job_type__symbol='mozlint'),
        push=push,
        tier__lte=2,
        result='testfailed',
    ).select_related('machine_platform', 'taskcluster_metadata')

    failures = [job_to_dict(job) for job in lint_failures]

    if parent_push:
        mark_failed_in_parent(failures, get_lint_failures(parent_push))

    return failures


def get_lint_in_progress_count(push):
    return Job.objects.filter(
        Q(machine_platform__platform='lint') | Q(job_type__symbol='mozlint'),
        push=push,
        tier__lte=2,
        result='unknown',
    ).count()
