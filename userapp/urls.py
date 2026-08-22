from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import logout_views,register_view,user_profile_view,change_password_view

urlpatterns = [
    # JWT Login (Authentication)
    path('users/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/logout/', logout_views.LogoutView.as_view(), name='logout'),

    # Profile & Registration
    path('users/register/', register_view.RegisterView.as_view(), name='register'),
    path('users/profile/me', user_profile_view.UserProfileView.as_view(), name='profile'), # GET va PATCH uchun
    path('users/change-password/', change_password_view.ChangePasswordView.as_view(), name='change_password'),
]