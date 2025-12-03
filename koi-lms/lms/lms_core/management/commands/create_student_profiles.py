from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lms_core.models import Student
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create Student profiles for all users without a profile'

    def handle(self, *args, **kwargs):
        users_without_student = User.objects.filter(student_profile__isnull=True)
        created_count = 0

        for user in users_without_student:
            # Generate a unique student_id
            student_id = f"S{user.id:05d}"

            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'student_id': student_id,
                    'program': 'Unknown',  # Update if you have real program info
                    'enrollment_date': timezone.now().date(),
                    'status': 'Active',
                    'gpa': 0.0
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created Student profile for user: {user.username}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Total Student profiles created: {created_count}"))
