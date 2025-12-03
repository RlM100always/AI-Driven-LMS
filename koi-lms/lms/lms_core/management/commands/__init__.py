from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lms_core.models import (
    Student, Course, Enrollment, Assignment, 
    Quiz, Grade, Forum, Query, ResponseTemplate, KnowledgeBase
)
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class Command(BaseCommand):
    help = 'Import data from CSV and JSON files'

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        data_dir = base_dir / 'data'
        
        self.stdout.write(self.style.SUCCESS('Starting data import...'))
        
        # Import students
        self.import_students(data_dir / 'students.csv')
        
        # Import courses
        self.import_courses(data_dir / 'courses.csv')
        
        # Import assignments
        self.import_assignments(data_dir / 'assignments.csv')
        
        # Import quizzes (if file exists)
        quizzes_file = data_dir / 'quizzes.csv'
        if quizzes_file.exists():
            self.import_quizzes(quizzes_file)
        
        # Import grades (if file exists)
        grades_file = data_dir / 'grades.csv'
        if grades_file.exists():
            self.import_grades(grades_file)
        
        # Import forums (if file exists)
        forums_file = data_dir / 'forums.csv'
        if forums_file.exists():
            self.import_forums(forums_file)
        
        # Import response templates
        responses_file = data_dir / 'responses.csv'
        if responses_file.exists():
            self.import_responses(responses_file)
        
        # Import knowledge base
        kb_file = data_dir / 'knowledge_base.json'
        if kb_file.exists():
            self.import_knowledge_base(kb_file)
        
        self.stdout.write(self.style.SUCCESS('Data import completed successfully!'))

    def import_students(self, filepath):
        """Import student data"""
        if not filepath.exists():
            self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
            return
            
        df = pd.read_csv(filepath)
        count = 0
        
        for _, row in df.iterrows():
            # Create user
            user, created = User.objects.get_or_create(
                username=row['username'],
                defaults={
                    'email': row['email'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                }
            )
            
            if created:
                user.set_password('student123')  # Default password
                user.save()
            
            # Create student profile
            student, created = Student.objects.get_or_create(
                student_id=row['student_id'],
                defaults={
                    'user': user,
                    'phone': row.get('phone', ''),
                    'program': row['program'],
                    'enrollment_date': pd.to_datetime(row['enrollment_date']).date(),
                    'status': row.get('status', 'Active'),
                    'gpa': row.get('gpa', 0.0),
                    'address': row.get('address', ''),
                    'postcode': row.get('postcode', ''),
                    'state': row.get('state', ''),
                    'international': row.get('international', False),
                    'scholarship': row.get('scholarship', False),
                }
            )
            
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} students'))

    def import_courses(self, filepath):
        """Import course data"""
        if not filepath.exists():
            self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
            return
            
        df = pd.read_csv(filepath)
        count = 0
        
        for _, row in df.iterrows():
            course, created = Course.objects.get_or_create(
                course_id=row['course_id'],
                defaults={
                    'course_code': row['course_code'],
                    'course_name': row['course_name'],
                    'instructor': row['instructor'],
                    'term': row['term'],
                    'level': row['level'],
                    'credits': row['credits'],
                    'department': row['department'],
                    'max_students': row.get('max_students', 50),
                    'enrolled_count': row.get('enrolled_count', 0),
                    'mode': row.get('mode', 'On-campus'),
                    'start_date': pd.to_datetime(row['start_date']).date(),
                    'end_date': pd.to_datetime(row['end_date']).date(),
                    'description': row['description'],
                }
            )
            
            if created:
                count += 1
                
                # Create enrollments for all students
                students = Student.objects.all()[:3]  # Enroll first 3 students in each course
                for i, student in enumerate(students, 1):
                    Enrollment.objects.get_or_create(
                        enrollment_id=f"E{course.course_id[-3:]}{student.student_id[-3:]}",
                        student=student,
                        course=course,
                        defaults={
                            'enrollment_date': course.start_date,
                            'status': 'Enrolled',
                        }
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} courses'))

    def import_assignments(self, filepath):
        """Import assignment data"""
        if not filepath.exists():
            self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
            return
            
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
                        'due_date': pd.to_datetime(row['due_date']),
                        'submission_type': row['submission_type'],
                        'allow_late': row.get('allow_late', False),
                        'late_penalty': row.get('late_penalty', 0),
                    }
                )
                
                if created:
                    count += 1
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Course not found: {row["course_id"]}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} assignments'))

    def import_quizzes(self, filepath):
        """Import quiz data"""
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
                        'date': pd.to_datetime(row['date']),
                        'attempts_allowed': row.get('attempts_allowed', '1'),
                        'time_limit': row.get('time_limit', True),
                        'shuffle_questions': row.get('shuffle_questions', False),
                    }
                )
                
                if created:
                    count += 1
            except Course.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} quizzes'))

    def import_grades(self, filepath):
        """Import grade data"""
        df = pd.read_csv(filepath)
        count = 0
        
        for _, row in df.iterrows():
            try:
                student = Student.objects.get(student_id=row['student_id'])
                course = Course.objects.get(course_id=row['course_id'])
                
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
                        'submitted_date': pd.to_datetime(row['submitted_date']),
                        'graded_date': pd.to_datetime(row['graded_date']),
                        'feedback': row.get('feedback', ''),
                    }
                )
                
                if created:
                    count += 1
            except (Student.DoesNotExist, Course.DoesNotExist):
                pass
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} grades'))

    def import_forums(self, filepath):
        """Import forum data"""
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
                        'posts_count': row.get('posts_count', 0),
                        'views': row.get('views', 0),
                        'status': row.get('status', 'Open'),
                    }
                )
                
                if created:
                    count += 1
            except Course.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} forums'))

    def import_responses(self, filepath):
        """Import response templates"""
        df = pd.read_csv(filepath)
        count = 0
        
        for _, row in df.iterrows():
            template, created = ResponseTemplate.objects.get_or_create(
                intent=row['intent'],
                defaults={
                    'template': row['template'],
                }
            )
            
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} response templates'))

    def import_knowledge_base(self, filepath):
        """Import knowledge base"""
        with open(filepath, 'r') as f:
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
            
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} knowledge base items'))
