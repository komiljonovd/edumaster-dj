from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from unfold import admin as unfold_admin
from unfold.decorators import action, display
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet
from django.http import HttpRequest
from userapp.models import ParentChild

User = get_user_model()
# admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    ordering = ("email",)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password",
                    "password2",
                    "first_name",
                    "last_name",
                    "birth_date",
                    "address",
                ),
            },
        ),
    )

    # 2. Mavjud foydalanuvchini tahrirlash oynasidan (edit) username'ni olib tashlaymiz
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "birth_date",
                    "address",
                    "role",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    list_display = [
        "id",
        "email",
        "first_name",
        "last_name",
        "show_role",
        "show_gender",
        "birth_date",
        "is_superuser",
        "is_staff",
        "is_active",
        "last_login",
        "date_joined",
    ]
    list_display_links = ["id", "email", "first_name", "last_name", "role"]
    list_filter = [
        "date_joined",
        "birth_date",
        "role",
        "is_superuser",
        "is_staff",
        "is_active",
    ]
    actions = [
        "assign_as_super_admin",
        "assign_as_admin",
        "assign_as_teacher",
        "assign_as_student",
        "assign_as_parent",
        "deactivate_user",
        "activate_user",
        "make_superuser",
        "remove_superuser",
        "make_staff",
        "remove_staff",
    ]
    search_fields = ["email", "first_name", "last_name", "role"]
    list_per_page = 50

    @action(description="Assign as ADMIN")
    def assign_as_admin(self, request: HttpRequest, queryset: QuerySet):
        users_to_update = queryset.exclude(role="ADMIN")
        count = users_to_update.update(role="ADMIN")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might already be ADMINs).",
                messages.WARNING,
            )

    @action(description="Assign as SUPER ADMIN")
    def assign_as_super_admin(self, request: HttpRequest, queryset: QuerySet):
        users_to_update = queryset.exclude(role="SUPER_ADMIN")
        count = users_to_update.update(role="SUPER_ADMIN")
        if count:
            self.message_user(
                request, f"Successfully updated: {count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might already be SUPER ADMINs).",
                messages.WARNING,
            )

    @action(description="Assign as TEACHER")
    def assign_as_teacher(self, request: HttpRequest, queryset: QuerySet):
        users_to_update = queryset.exclude(role="TEACHER")
        count = users_to_update.update(role="TEACHER")
        if count:
            self.message_user(
                request, f"Successfully updated: {count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might already be TEACHERs).",
                messages.WARNING,
            )

    @action(description="Assign as STUDENT")
    def assign_as_student(self, request: HttpRequest, queryset: QuerySet):
        users_to_update = queryset.exclude(role="STUDENT")
        count = users_to_update.update(role="STUDENT")
        if count:
            self.message_user(
                request, f"Successfully updated: {count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might already be STUDENTs).",
                messages.WARNING,
            )

    @action(description="Assign as PARENT")
    def assign_as_parent(self, request: HttpRequest, queryset: QuerySet):
        users_to_update = queryset.exclude(role="PARENT")
        count = users_to_update.update(role="PARENT")
        if count:
            self.message_user(
                request, f"Successfully updated: {count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might already be PARENTs).",
                messages.WARNING,
            )

    @action(description="Deactivate USER")
    def deactivate_user(self, request: HttpRequest, queryset: QuerySet):
        users_to_update = queryset.exclude(is_active=False).exclude(pk=request.user.pk)
        count = users_to_update.update(is_active=False)
        if count:
            self.message_user(
                request, f"Successfully updated: {count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might already DEACTIVATED).",
                messages.WARNING,
            )

    @action(description="Activate USER")
    def activate_user(self, request: HttpRequest, queryset: QuerySet):
        users_to_update = queryset.exclude(is_active=True)
        count = users_to_update.update(is_active=True)
        if count:
            self.message_user(
                request, f"Successfully updated: {count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might already DEACTIVATED).",
                messages.WARNING,
            )

    @action(description="Assign SUPERUSER")
    def make_superuser(self, request: HttpRequest, queryset: QuerySet) -> None:
        users_to_update = queryset.exclude(is_superuser=True)
        count = users_to_update.update(is_superuser=True, is_staff=True)
        if count:
            self.message_user(
                request,
                f"Successfully assigned SUPERUSER to {count} user(s).",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might already be SUPERUSERs).",
                messages.WARNING,
            )

    @action(description="Remove SUPERUSER")
    def remove_superuser(self, request: HttpRequest, queryset: QuerySet) -> None:
        users_to_update = queryset.exclude(is_superuser=False).exclude(
            pk=request.user.pk
        )
        count = users_to_update.update(is_superuser=False)
        if count:
            self.message_user(
                request,
                f"Successfully removed SUPERUSER from {count} user(s).",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might not be SUPERUSERs).",
                messages.WARNING,
            )

    @action(description="Assign STAFF")
    def make_staff(self, request: HttpRequest, queryset: QuerySet) -> None:
        users_to_update = queryset.exclude(is_staff=True)
        count = users_to_update.update(is_staff=True)
        if count:
            self.message_user(
                request,
                f"Successfully assigned STAFF to {count} user(s).",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might already be STAFF).",
                messages.WARNING,
            )

    @action(description="Remove STAFF")
    def remove_staff(self, request: HttpRequest, queryset: QuerySet) -> None:
        users_to_update = queryset.exclude(is_staff=False).exclude(pk=request.user.pk)
        count = users_to_update.update(is_staff=False)
        if count:
            self.message_user(
                request,
                f"Successfully removed STAFF from {count} user(s).",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No users were updated (they might not be STAFF).",
                messages.WARNING,
            )

    @display(
        description="Role",
        ordering="role",
        label={
            "SUPER_ADMIN": "success",
            "ADMIN": "success",
            "TEACHER": "danger",
            "STUDENT": "warning",
            "PARENT": "info",
        },
    )
    def show_role(self, obj):
        return obj.get_role_display()

    @display(description="Gender", ordering="gender", label=True)
    def show_gender(self, obj):
        return obj.get_gender_display()


@admin.register(ParentChild)
class ParentChildAdmin(ModelAdmin):
    list_display = ["id", "parent", "student", "is_confirmed", "created_at"]
    list_display_links = ["id", "parent", "student", "is_confirmed", "created_at"]
    search_fields = ["id", "parent__email", "student__email"]
    ordering = ["-created_at"]
    list_filter = ["is_confirmed"]
    actions = ["remove_confirmation", "select_confirmation"]

    @action(description="Remove CONFIRMATION")
    def remove_confirmation(self, request: HttpRequest, queryset: QuerySet) -> None:
        users_to_update = queryset.exclude(is_confirmed=False)
        count = users_to_update.update(is_confirmed=False)
        if count:
            self.message_user(
                request,
                f"Successfully: {count}",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "It was already not CONFIRMED.",
                messages.WARNING,
            )

    @action(description="Select CONFIRMATION")
    def select_confirmation(self, request: HttpRequest, queryset: QuerySet) -> None:
        users_to_update = queryset.exclude(is_confirmed=True)
        count = users_to_update.update(is_confirmed=True)
        if count:
            self.message_user(
                request,
                f"Successfully: {count}",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "It was already CONFIRMED",
                messages.WARNING,
            )


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
