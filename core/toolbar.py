def toolabar_permission(request):
    return request.user.is_superuser and request.user.is_authenticated
