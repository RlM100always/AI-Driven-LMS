# ============================================
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from lms_core.models import (
    Student, Course, Enrollment, Assignment, Quiz, Grade, Forum, Query, ResponseTemplate, KnowledgeBase
)
import pandas as pd
import json
from pathlib import Path

class Command(BaseCommand):
    help = 'Import LMS data from CSV and JSON files'

    def handle(self, *args, **options):
        self.stdout.write("✅ Starting data import...")

        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        data_dir = base_dir / 'data'

        # Students
        self.import_students(data_dir / 'students.csv')
        # Courses and enrollments
        self.import_courses(data_dir / 'courses.csv')
        # Assignments
        self.import_assignments(data_dir / 'assignments.csv')
        # Quizzes
        self.import_quizzes(data_dir / 'quizzes.csv')
        # Grades
        self.import_grades(data_dir / 'grades.csv')
        # Forums
        self.import_forums(data_dir / 'forums.csv')
        # Queries
        self.import_queries(data_dir / 'queries.csv')
        # Response Templates
        self.import_responses(data_dir / 'responses.csv')
        # Knowledge Base
        self.import_knowledge_base(data_dir / 'knowledge_base.json')

        self.stdout.write(self.style.SUCCESS('✅ Data import completed successfully!'))

    # ---------------------- Students ----------------------
    def import_students(self, filepath):
        if not filepath.exists():
            self.stdout.write(self.style.WARNING(f'Students file not found: {filepath}'))
            return
        
        df = pd.read_csv(filepath)
        count = 0
        for _, row in df.iterrows():
            username = row['email'].split('@')[0]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': row['email'], 'first_name': row['first_name'], 'last_name': row['last_name']}
            )
            if created:
                user.set_password('student123')
                user.save()
            student, created = Student.objects.get_or_create(
                student_id=row['student_id'],
                defaults={
                    'user': user,
                    'phone': row.get('phone',''),
                    'date_of_birth': pd.to_datetime(row['date_of_birth']).date() if row.get('date_of_birth') else None,
                    'program': row['program'],
                    'enrollment_date': pd.to_datetime(row['enrollment_date']).date(),
                    'status': row.get('status','Active'),
                    'gpa': row.get('gpa',0.0),
                    'address': row.get('address',''),
                    'postcode': row.get('postcode',''),
                    'state': row.get('state',''),
                    'international': bool(row.get('international', False)),
                    'scholarship': bool(row.get('scholarship', False)),
                }
            )
            if created: count += 1
        self.stdout.write(self.style.SUCCESS(f'Imported {count} students'))

    # ---------------------- Courses & Enrollments ----------------------
    def import_courses(self, filepath):
        if not filepath.exists():
            self.stdout.write(self.style.WARNING(f'Courses file not found: {filepath}'))
            return

        df = pd.read_csv(filepath)
        count_courses = 0
        count_enrollments = 0
        students = list(Student.objects.all())

        for _, row in df.iterrows():
            course, created_course = Course.objects.get_or_create(
                course_id=row['course_id'],
                defaults={
                    'course_code': row['course_code'],
                    'course_name': row['course_name'],
                    'instructor': row['instructor'],
                    'term': row['term'],
                    'level': row['level'],
                    'credits': row['credits'],
                    'department': row['department'],
                    'max_students': row.get('max_students',50),
                    'enrolled_count': row.get('enrolled_count',0),
                    'mode': row.get('mode','On-campus'),
                    'start_date': pd.to_datetime(row['start_date']).date(),
                    'end_date': pd.to_datetime(row['end_date']).date(),
                    'description': row['description'],
                }
            )
            if created_course: count_courses += 1

            # Safe enrollments: first 3 students
            for student in students[:3]:
                enrollment_id = f"E{course.course_id[-3:]}{student.student_id[-3:]}"
                if not Enrollment.objects.filter(enrollment_id=enrollment_id).exists():
                    Enrollment.objects.create(
                        enrollment_id=enrollment_id,
                        student=student,
                        course=course,
                        enrollment_date=course.start_date,
                        status='Enrolled'
                    )
                    count_enrollments += 1

        self.stdout.write(self.style.SUCCESS(f'Imported {count_courses} courses'))
        self.stdout.write(self.style.SUCCESS(f'Created {count_enrollments} enrollments'))

    # ---------------------- Assignments ----------------------
    def import_assignments(self, filepath):
        if not filepath.exists(): return
        df = pd.read_csv(filepath)
        count = 0
        for _, row in df.iterrows():
            try:
                course = Course.objects.get(course_id=row['course_id'])
                assignment, created = Assignment.objects.get_or_create(
                    assignment_id=row['assignment_id'],
                    defaults={
                        'course': course,
                        'title': row['title'],
                        'assignment_type': row['assignment_type'],
                        'description': row['description'],
                        'max_marks': row['max_marks'],
                        'weight': row['weight'],
                        'due_date': timezone.make_aware(pd.to_datetime(row['due_date'])),
                        'submission_type': row['submission_type'],
                        'allow_late': bool(row.get('allow_late', False)),
                        'late_penalty': row.get('late_penalty',0),
                    }
                )
                if created: count += 1
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Assignment skipped, course not found: {row["course_id"]}'))
        self.stdout.write(self.style.SUCCESS(f'Imported {count} assignments'))

    # ---------------------- Quizzes ----------------------
    def import_quizzes(self, filepath):
        if not filepath.exists(): return
        df = pd.read_csv(filepath)
        count = 0
        for _, row in df.iterrows():
            try:
                course = Course.objects.get(course_id=row['course_id'])
                quiz, created = Quiz.objects.get_or_create(
                    quiz_id=row['quiz_id'],
                    defaults={
                        'course': course,
                        'title': row['title'],
                        'quiz_type': row['quiz_type'],
                        'max_marks': row['max_marks'],
                        'duration_minutes': row['duration_minutes'],
                        'date': timezone.make_aware(pd.to_datetime(row['date'])),
                        'attempts_allowed': row.get('attempts_allowed',1),
                        'time_limit': bool(row.get('time_limit',True)),
                        'shuffle_questions': bool(row.get('shuffle_questions',False)),
                    }
                )
                if created: count += 1
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Quiz skipped, course not found: {row["course_id"]}'))
        self.stdout.write(self.style.SUCCESS(f'Imported {count} quizzes'))

    # ---------------------- Grades ----------------------
    def import_grades(self, filepath):
        if not filepath.exists(): return
        df = pd.read_csv(filepath)
        count = 0
        for _, row in df.iterrows():
            try:
                student = Student.objects.get(student_id=row['student_id'])
                course = Course.objects.get(course_id=row['course_id'])
                submitted_date = timezone.make_aware(pd.to_datetime(row['submitted_date']))
                graded_date = timezone.make_aware(pd.to_datetime(row['graded_date']))
                grade, created = Grade.objects.get_or_create(
                    grade_id=row['grade_id'],
                    defaults={
                        'student': student,
                        'course': course,
                        'assessment_id': row['assessment_id'],
                        'assessment_type': row['assessment_type'],
                        'marks_obtained': row['marks_obtained'],
                        'max_marks': row['max_marks'],
                        'percentage': row['percentage'],
                        'submitted_date': submitted_date,
                        'graded_date': graded_date,
                        'feedback': row.get('feedback',''),
                    }
                )
                if created: count += 1
            except (Student.DoesNotExist, Course.DoesNotExist):
                self.stdout.write(self.style.WARNING(f"Grade skipped: student {row['student_id']} or course {row['course_id']} missing"))
        self.stdout.write(self.style.SUCCESS(f'Imported {count} grades'))

    # ---------------------- Forums ----------------------
    def import_forums(self, filepath):
        if not filepath.exists(): return
        df = pd.read_csv(filepath)
        count = 0
        for _, row in df.iterrows():
            try:
                course = Course.objects.get(course_id=row['course_id'])
                forum, created = Forum.objects.get_or_create(
                    forum_id=row['forum_id'],
                    defaults={
                        'course': course,
                        'topic': row['topic'],
                        'created_by': row['created_by'],
                        'created_date': pd.to_datetime(row['created_date']).date(),
                        'posts_count': row.get('posts_count',0),
                        'views': row.get('views',0),
                        'status': row.get('status','Open'),
                    }
                )
                if created: count += 1
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Forum skipped, course not found: {row["course_id"]}'))
        self.stdout.write(self.style.SUCCESS(f'Imported {count} forums'))

    # ---------------------- Queries ----------------------
    def import_queries(self, filepath):
        if not filepath.exists(): return
        df = pd.read_csv(filepath)
        count = 0
        for _, row in df.iterrows():
            try:
                student = Student.objects.get(student_id=row['student_id'])
                timestamp = timezone.make_aware(pd.to_datetime(row['timestamp']))
                query, created = Query.objects.get_or_create(
                    query_id=row['query_id'],
                    defaults={
                        'student': student,
                        'query_text': row['query_text'],
                        'intent': row['intent'],
                        'timestamp': timestamp,
                        'status': row.get('status','Pending'),
                        'priority': row.get('priority','Medium'),
                    }
                )
                if created: count += 1
            except Student.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Query skipped, student not found: {row["student_id"]}'))
        self.stdout.write(self.style.SUCCESS(f'Imported {count} queries'))

    # ---------------------- Response Templates ----------------------
    def import_responses(self, filepath):
        if not filepath.exists(): return
        df = pd.read_csv(filepath)
        count = 0
        for _, row in df.iterrows():
            template, created = ResponseTemplate.objects.get_or_create(
                intent=row['intent'],
                defaults={
                    'template': row['template'],
                    'variations': row.get('variations', '[]')
                }
            )
            if created: count += 1
        self.stdout.write(self.style.SUCCESS(f'Imported {count} response templates'))

    # ---------------------- Knowledge Base ----------------------
    def import_knowledge_base(self, filepath):
        if not filepath.exists(): return
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = 0
        for item in data:
            kb, created = KnowledgeBase.objects.get_or_create(
                category=item['category'],
                title=item['title'],
                defaults={
                    'content': item['content'],
                    'keywords': item.get('keywords', []),
                }
            )
            if created: count += 1
        self.stdout.write(self.style.SUCCESS(f'Imported {count} knowledge base items'))
