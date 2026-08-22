from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from service.tasks.report_dashboard import sync_dashboard_to_redis_task, CACHE_KEY
from django.shortcuts import render, get_object_or_404
from .models import Certificate


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    if (
        request.user.is_superuser
        and getattr(request.user, "role", None) == "SUPER_ADMIN"
    ):

        stats = cache.get(CACHE_KEY)

        if stats is None:
            sync_dashboard_to_redis_task.delay()
            stats = {}

        return render(request, "admin/dashboard.html", {"stats": stats})

    raise PermissionDenied


from django.shortcuts import render, get_object_or_404


def certificate_view(request, certificate_number):
    certificate = get_object_or_404(Certificate, certificate_number=certificate_number)
    return render(request, "certificate.html", {"certificate": certificate})
