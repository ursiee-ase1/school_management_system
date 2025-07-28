# models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

# Common choices
GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('graduated', 'Graduated'),
    ('transferred', 'Transferred'),
]

# Grade Model (Enhanced)
class Grade(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True, help_text="Grade description or notes")
    capacity = models.PositiveIntegerField(default=30, help_text="Maximum students per grade")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def student_count(self):
        return self.student_set.count()

    def available_spots(self):
        return self.capacity - self.student_count()

# Student Model (Enhanced)
class Student(models.Model):
    # Basic Information
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True, blank=True, help_text="Auto-generated if empty")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    
    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    # Parent/Guardian Information
    parent_name = models.CharField(max_length=100, blank=True)
    parent_phone = models.CharField(max_length=15, blank=True)
    parent_email = models.EmailField(blank=True, null=True)
    
    # Financial Information
    fees_due = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    fees_paid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Status and Dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    enrolled_on = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['grade', 'status']),
            models.Index(fields=['student_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.student_id})"

    def save(self, *args, **kwargs):
        # Auto-generate student ID if not provided
        if not self.student_id:
            last_student = Student.objects.order_by('-id').first()
            if last_student:
                last_id = int(last_student.student_id.split('-')[-1]) if '-' in last_student.student_id else 0
                self.student_id = f"STU-{last_id + 1:04d}"
            else:
                self.student_id = "STU-0001"
        super().save(*args, **kwargs)

    def balance(self):
        return self.fees_due - self.fees_paid

    def payment_status(self):
        balance = self.balance()
        if balance <= 0:
            return 'paid'
        elif balance <= 100:  # You can adjust this threshold
            return 'outstanding'
        else:
            return 'overdue'

    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

# Staff Model (Enhanced)
class Staff(models.Model):
    ROLE_CHOICES = [
        ('Teacher', 'Teacher'),
        ('Admin', 'Administrator'),
        ('Support', 'Support Staff'),
        ('Principal', 'Principal'),
        ('Vice Principal', 'Vice Principal'),
        ('Counselor', 'Counselor'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=20, unique=True, blank=True, help_text="Auto-generated if empty")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Teacher')
    department = models.CharField(max_length=100, blank=True, help_text="e.g., Mathematics, Science, etc.")
    
    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    # Employment Information
    date_joined = models.DateField(default=timezone.now, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Additional Information
    qualifications = models.TextField(blank=True, help_text="Educational qualifications and certifications")
    subjects = models.CharField(max_length=200, blank=True, help_text="Subjects taught (comma-separated)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Staff'
        indexes = [
            models.Index(fields=['role', 'status']),
            models.Index(fields=['staff_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.role})"

    def save(self, *args, **kwargs):
        # Auto-generate staff ID if not provided
        if not self.staff_id:
            last_staff = Staff.objects.order_by('-id').first()
            if last_staff:
                last_id = int(last_staff.staff_id.split('-')[-1]) if '-' in last_staff.staff_id else 0
                self.staff_id = f"STF-{last_id + 1:04d}"
            else:
                self.staff_id = "STF-0001"
        super().save(*args, **kwargs)

# Notification Model (Enhanced)
class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    TARGET_CHOICES = [
        ('all', 'All'),
        ('students', 'Students'),
        ('staff', 'Staff'),
        ('parents', 'Parents'),
        ('grade_specific', 'Grade Specific'),
    ]
    
    title = models.CharField(max_length=200, default="General Notification")
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    target_audience = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all')
    target_grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, 
                                   help_text="Specific grade if target is grade_specific")
    
    # Status and Dates
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date = models.DateField(default=timezone.now)  # Keep for backward compatibility
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.title} - {self.message[:50]}..."

# Event Model (Enhanced)
class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('meeting', 'Meeting'),
        ('holiday', 'Holiday'),
        ('exam', 'Examination'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='other')
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    target_grades = models.ManyToManyField(Grade, blank=True, help_text="Leave empty for all grades")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%Y-%m-%d')}"

# Activity Model (Enhanced)
class Activity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('club', 'Club'),
        ('sport', 'Sport'),
        ('academic', 'Academic'),
        ('volunteer', 'Volunteer'),
        ('arts', 'Arts & Crafts'),
        ('music', 'Music'),
        ('drama', 'Drama'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES, default='other')
    instructor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    max_participants = models.PositiveIntegerField(default=20)
    schedule = models.CharField(max_length=200, blank=True, help_text="e.g., Mondays 3-4 PM")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Activities'

    def __str__(self):
        return self.title

    def participant_count(self):
        return self.activityparticipant_set.count()

    def available_spots(self):
        return self.max_participants - self.participant_count()

# New Model: Activity Participants
class ActivityParticipant(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['activity', 'student']

    def __str__(self):
        return f"{self.student.name} - {self.activity.title}"

# New Model: Fee Payment History
class FeePayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('online', 'Online Payment'),
        ('card', 'Card Payment'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Dates
    payment_date = models.DateField(default=timezone.now, null=True, blank= True)
    recorded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    recorded_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.student.name} - ${self.amount} ({self.payment_date})"