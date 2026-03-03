import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Custom manager — creates users by email (no password required)."""

    def create_user(self, email=None, **extra_fields):
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user = self.model(email=self.normalize_email(email), **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_guest(self):
        """Create an anonymous guest user."""
        guest_id = uuid.uuid4().hex[:8]
        user = self.model(
            username=f'guest_{guest_id}',
            is_guest=True,
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user


AGE_GROUP_CHOICES = [
    ('child', 'Criança (6–12)'),
    ('teen', 'Jovem (13–17)'),
    ('adult', 'Adulto (18+)'),
]


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Kwijiya user — email OTP auth + guest mode."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    avatar = models.CharField(max_length=100, blank=True, default='')
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES, default='adult')
    date_of_birth = models.DateField(null=True, blank=True)

    # Gamification fields
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak_days = models.PositiveIntegerField(default=0)
    coins = models.PositiveIntegerField(default=0)  # Makuta
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Progress flags
    placement_test_completed = models.BooleanField(default=False)

    # Account flags
    is_guest = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'
        ordering = ['-created_at']

    def __str__(self):
        return self.email or self.username or str(self.id)

    def save(self, *args, **kwargs):
        self.update_age_group()
        super().save(*args, **kwargs)

    def update_age_group(self):
        """Update age group based on date of birth."""
        if not self.date_of_birth:
            return
            
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
        
        if age < 13:
            self.age_group = 'child'
        elif age < 18:
            self.age_group = 'teen'
        else:
            self.age_group = 'adult'

    @property
    def xp_for_next_level(self):
        """XP required to reach the next level."""
        return 100 * self.level

    @property
    def xp_progress(self):
        """XP accumulated towards the current level (percentage)."""
        required = self.xp_for_next_level
        # Calculate XP within current level
        xp_at_current_level = sum(100 * i for i in range(1, self.level))
        current = self.total_xp - xp_at_current_level
        return min(round(current / required * 100, 1), 100.0) if required else 100.0

    @property
    def title(self):
        """Cultural title based on level."""
        titles = [
            (1, 'Aprendiz'),
            (5, 'Iniciando'),
            (10, 'Explorador Cultural'),
            (20, 'Guardião da Língua'),
            (35, 'Mestre da Tradição'),
            (50, 'Sábio Kwijiya'),
        ]
        current_title = 'Aprendiz'
        for lvl, t in titles:
            if self.level >= lvl:
                current_title = t
        return current_title


class OTPCode(models.Model):
    """One-time code for email verification."""

    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Código OTP'
        verbose_name_plural = 'Códigos OTP'
        ordering = ['-created_at']

    def __str__(self):
        return f'OTP {self.code} → {self.email}'

    @property
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
