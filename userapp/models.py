from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


# Create your models here.
class Role(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", _("SUPER_ADMIN")
    ADMIN = "ADMIN", _("ADMIN")
    TEACHER = "TEACHER", _("TEACHER")
    STUDENT = "STUDENT", _("STUDENT")
    PARENT = "PARENT", _("PARENT")


class Gender(models.TextChoices):
    UNKNOWN = "UNKNOWN", _("UNKNOWN")
    MALE = "MALE", _("MALE")
    FEMALE = "FEMALE", _("FEMALE")


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.SUPER_ADMIN
    )
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20, choices=Gender.choices, default=Gender.UNKNOWN
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def __str__(self):
        return f"{self.email} - {self.role}"


class ParentChild(models.Model):
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="child_relationships",
        limit_choices_to={"role": "PARENT"},
        verbose_name="Parent",
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="parent_relationships",
        limit_choices_to={"role": "STUDENT"},
        verbose_name="Child",
    )
    is_confirmed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:

        if self.parent_id == self.student_id:
            raise ValidationError("Пользователь не может быть родителем самого себя.")

        if hasattr(self.parent, "role") and self.parent.role != "PARENT":
            raise ValidationError(
                "Указанный пользователь 'parent' должен иметь роль 'parent'."
            )

        if hasattr(self.student, "role") and self.student.role != "STUDENT":
            raise ValidationError(
                "Указанный пользователь 'student' должен иметь роль 'student'."
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Parent: {self.parent.get_full_name() or self.parent.email} -> Child: {self.student.get_full_name() or self.student.email}"

    class Meta:
        db_table = "ParentChild"
        verbose_name = "Parent Child"
        verbose_name_plural = "Parent Childs"
        unique_together = ("parent", "student")
