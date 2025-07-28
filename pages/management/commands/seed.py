# pages/management/commands/seed.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from decimal import Decimal
from datetime import date, timedelta

from pages.models import Grade, Student, Staff, Notification, Event, Activity

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with school data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=50,
            help='Number of students to create (default: 50)'
        )
        parser.add_argument(
            '--staff',
            type=int,
            default=15,
            help='Number of staff members to create (default: 15)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('Seeding data...')
        self.seed_grades()
        self.seed_students(options['students'])
        self.seed_staff(options['staff'])
        self.seed_notifications()
        self.seed_events()
        self.seed_activities()
        self.stdout.write(self.style.SUCCESS('Database seeding complete.'))

    def clear_data(self):
        """Clear existing data (optional)"""
        Activity.objects.all().delete()
        Event.objects.all().delete()
        Notification.objects.all().delete()
        Student.objects.all().delete()
        Staff.objects.all().delete()
        Grade.objects.all().delete()
        self.stdout.write('Existing data cleared.')

    def seed_grades(self):
        """Create grades with enhanced fields"""
        grades_data = [
            {"name": "Kindergarten", "description": "Foundation level education", "capacity": 25},
            {"name": "Grade 1", "description": "First grade primary education", "capacity": 30},
            {"name": "Grade 2", "description": "Second grade primary education", "capacity": 30},
            {"name": "Grade 3", "description": "Third grade primary education", "capacity": 30},
            {"name": "Grade 4", "description": "Fourth grade primary education", "capacity": 30},
            {"name": "Grade 5", "description": "Fifth grade primary education", "capacity": 30},
            {"name": "Grade 6", "description": "Sixth grade primary education", "capacity": 30},
            {"name": "Grade 7", "description": "Seventh grade middle school", "capacity": 35},
            {"name": "Grade 8", "description": "Eighth grade middle school", "capacity": 35},
            {"name": "Grade 9", "description": "Ninth grade high school", "capacity": 35},
            {"name": "Grade 10", "description": "Tenth grade high school", "capacity": 35},
            {"name": "Grade 11", "description": "Eleventh grade high school", "capacity": 40},
            {"name": "Grade 12", "description": "Twelfth grade high school", "capacity": 40},
        ]
        
        for grade_data in grades_data:
            grade, created = Grade.objects.get_or_create(
                name=grade_data["name"],
                defaults={
                    'description': grade_data["description"],
                    'capacity': grade_data["capacity"]
                }
            )
            if created:
                self.stdout.write(f'Created grade: {grade.name}')

    def seed_students(self, count):
        """Create students with enhanced fields"""
        grades = list(Grade.objects.all())
        genders = ['M', 'F']
        statuses = ['active', 'active', 'active', 'active', 'inactive']  # More active students
        
        for i in range(count):
            grade = random.choice(grades)
            fees_due = Decimal(str(random.randint(500, 2000)))
            fees_paid = Decimal(str(random.randint(0, int(fees_due))))
            
            # Generate realistic age based on grade
            grade_number = self.extract_grade_number(grade.name)
            if grade_number:
                age = grade_number + 5  # Approximate age
                birth_year = date.today().year - age
                date_of_birth = fake.date_of_birth(
                    minimum_age=age-1, 
                    maximum_age=age+1
                )
            else:
                date_of_birth = fake.date_of_birth(minimum_age=5, maximum_age=18)
            
            student = Student.objects.create(
                name=fake.name(),
                grade=grade,
                date_of_birth=date_of_birth,
                gender=random.choice(genders),
                email=fake.email() if random.choice([True, False]) else '',
                phone=fake.phone_number()[:15] if random.choice([True, False]) else '',
                address=fake.address() if random.choice([True, False]) else '',
                parent_name=fake.name(),
                parent_phone=fake.phone_number()[:15],
                parent_email=fake.email() if random.choice([True, False]) else '',
                fees_due=fees_due,
                fees_paid=fees_paid,
                status=random.choice(statuses),
                enrolled_on=fake.date_between(start_date='-2y', end_date='today')
            )
            
            if i % 10 == 0:
                self.stdout.write(f'Created {i+1} students...')
        
        self.stdout.write(f'Created {count} students total.')

    def seed_staff(self, count):
        """Create staff with enhanced fields"""
        roles = ['Teacher', 'Teacher', 'Teacher', 'Admin', 'Support', 'Principal', 'Vice Principal']
        departments = ['Mathematics', 'Science', 'English', 'History', 'Physical Education', 
                      'Art', 'Music', 'Computer Science', 'Administration', 'Library']
        statuses = ['active', 'active', 'active', 'active', 'inactive']
        
        # Subjects for teachers
        subjects_list = [
            'Mathematics, Algebra', 'Physics, Chemistry', 'English Literature, Grammar',
            'World History, Geography', 'Physical Education, Sports', 'Visual Arts, Crafts',
            'Music Theory, Choir', 'Computer Programming, IT', 'Biology, Environmental Science',
            'Foreign Languages, Cultural Studies'
        ]
        
        for i in range(count):
            role = random.choice(roles)
            department = random.choice(departments) if role == 'Teacher' else 'Administration'
            subjects = random.choice(subjects_list) if role == 'Teacher' else ''
            
            staff = Staff.objects.create(
                name=fake.name(),
                role=role,
                department=department,
                email=fake.email(),
                phone=fake.phone_number()[:15],
                address=fake.address() if random.choice([True, False]) else '',
                date_joined=fake.date_between(start_date='-5y', end_date='today'),
                salary=Decimal(str(random.randint(30000, 80000))) if random.choice([True, False]) else None,
                status=random.choice(statuses),
                qualifications=fake.text(max_nb_chars=200) if random.choice([True, False]) else '',
                subjects=subjects
            )
        
        self.stdout.write(f'Created {count} staff members.')

    def seed_notifications(self):
        """Create notifications with enhanced fields"""
        notifications_data = [
            {
                "title": "Term End Examinations",
                "message": "Final examinations for all grades will begin next Monday. Please ensure students are well prepared.",
                "priority": "high",
                "target_audience": "all"
            },
            {
                "title": "PTA Meeting",
                "message": "Parent-Teacher Association meeting scheduled for this Friday at 6 PM in the main auditorium.",
                "priority": "medium",
                "target_audience": "parents"
            },
            {
                "title": "Library New Books",
                "message": "New collection of science and literature books have arrived. Students can check them out starting tomorrow.",
                "priority": "low",
                "target_audience": "students"
            },
            {
                "title": "Staff Development Workshop",
                "message": "Professional development workshop on modern teaching methods this Saturday from 9 AM to 3 PM.",
                "priority": "medium",
                "target_audience": "staff"
            },
            {
                "title": "School Closure Notice",
                "message": "School will be closed on Monday due to maintenance work. All classes will resume on Tuesday.",
                "priority": "urgent",
                "target_audience": "all"
            },
            {
                "title": "Sports Day Preparation",
                "message": "All students participating in Sports Day events should report to the sports ground for practice.",
                "priority": "medium",
                "target_audience": "students"
            }
        ]
        
        # Get a random staff member to be the creator
        staff_members = list(Staff.objects.all())
        
        for notif_data in notifications_data:
            notification = Notification.objects.create(
                title=notif_data["title"],
                message=notif_data["message"],
                priority=notif_data["priority"],
                target_audience=notif_data["target_audience"],
                is_active=True,
                date=fake.date_between(start_date='-30d', end_date='today'),
                created_by=random.choice(staff_members) if staff_members else None
            )
        
        self.stdout.write(f'Created {len(notifications_data)} notifications.')

    def seed_events(self):
        """Create events with enhanced fields"""
        events_data = [
            {
                "title": "Annual Science Fair",
                "description": "Students will showcase their science projects and innovations.",
                "event_type": "academic",
                "location": "Main Auditorium"
            },
            {
                "title": "Inter-School Basketball Tournament",
                "description": "Basketball competition between local schools.",
                "event_type": "sports",
                "location": "School Gymnasium"
            },
            {
                "title": "Cultural Heritage Day",
                "description": "Celebration of diverse cultures with performances and exhibitions.",
                "event_type": "cultural",
                "location": "School Courtyard"
            },
            {
                "title": "Parent-Teacher Conference",
                "description": "Individual meetings between parents and teachers to discuss student progress.",
                "event_type": "meeting",
                "location": "Classrooms"
            },
            {
                "title": "End of Term Examinations",
                "description": "Final examinations for all grade levels.",
                "event_type": "exam",
                "location": "Examination Halls"
            },
            {
                "title": "Graduation Ceremony",
                "description": "Celebration ceremony for graduating students.",
                "event_type": "academic",
                "location": "Main Auditorium"
            }
        ]
        
        staff_members = list(Staff.objects.all())
        grades = list(Grade.objects.all())
        
        for event_data in events_data:
            start_date = fake.future_datetime(end_date='+90d')
            end_date = start_date + timedelta(hours=random.randint(2, 8))
            
            event = Event.objects.create(
                title=event_data["title"],
                description=event_data["description"],
                event_type=event_data["event_type"],
                start_date=start_date,
                end_date=end_date,
                location=event_data["location"],
                is_active=True,
                created_by=random.choice(staff_members) if staff_members else None
            )
            
            # Add some target grades randomly
            if random.choice([True, False]):
                target_grades = random.sample(grades, random.randint(1, 3))
                event.target_grades.set(target_grades)
        
        self.stdout.write(f'Created {len(events_data)} events.')

    def seed_activities(self):
        """Create activities with enhanced fields"""
        activities_data = [
            {
                "title": "Chess Club",
                "description": "Weekly chess games and tournaments for strategy enthusiasts.",
                "activity_type": "club",
                "max_participants": 20,
                "schedule": "Wednesdays 3:00-4:00 PM"
            },
            {
                "title": "School Orchestra",
                "description": "Musical ensemble practicing classical and contemporary pieces.",
                "activity_type": "music",
                "max_participants": 30,
                "schedule": "Tuesdays and Thursdays 3:30-5:00 PM"
            },
            {
                "title": "Drama Society",
                "description": "Acting and theater production group for creative students.",
                "activity_type": "drama",
                "max_participants": 25,
                "schedule": "Mondays and Fridays 3:15-4:45 PM"
            },
            {
                "title": "Environmental Club",
                "description": "Promoting environmental awareness and sustainability projects.",
                "activity_type": "volunteer",
                "max_participants": 15,
                "schedule": "Fridays 3:00-4:00 PM"
            },
            {
                "title": "Basketball Team",
                "description": "Competitive basketball team representing the school.",
                "activity_type": "sport",
                "max_participants": 15,
                "schedule": "Daily 4:00-5:30 PM"
            },
            {
                "title": "Art & Crafts Workshop",
                "description": "Creative arts and crafts sessions for artistic expression.",
                "activity_type": "arts",
                "max_participants": 20,
                "schedule": "Wednesdays 3:00-4:30 PM"
            },
            {
                "title": "Debate Team",
                "description": "Competitive debating and public speaking training.",
                "activity_type": "academic",
                "max_participants": 12,
                "schedule": "Tuesdays 3:30-5:00 PM"
            },
            {
                "title": "Community Service",
                "description": "Volunteer work in the local community and charity projects.",
                "activity_type": "volunteer",
                "max_participants": 25,
                "schedule": "Saturdays 9:00 AM-12:00 PM"
            }
        ]
        
        staff_members = list(Staff.objects.filter(role='Teacher'))  # Only teachers as instructors
        
        for activity_data in activities_data:
            activity = Activity.objects.create(
                title=activity_data["title"],
                description=activity_data["description"],
                activity_type=activity_data["activity_type"],
                instructor=random.choice(staff_members) if staff_members else None,
                max_participants=activity_data["max_participants"],
                schedule=activity_data["schedule"],
                is_active=True
            )
        
        self.stdout.write(f'Created {len(activities_data)} activities.')

    def extract_grade_number(self, grade_name):
        """Extract numeric grade from grade name"""
        try:
            if 'Grade' in grade_name:
                return int(grade_name.split()[1])
            elif 'Kindergarten' in grade_name:
                return 0
            return None
        except (IndexError, ValueError):
            return None