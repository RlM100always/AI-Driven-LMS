from django import forms
from django.contrib.auth.models import User
from lms_core.models import (
    Student, Course, Enrollment, Assignment, 
    Quiz, Grade, Forum, Query, ResponseTemplate, KnowledgeBase
)
from .models import Teacher

class TeacherSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
        
class TeacherLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

class StudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Student
        fields = ['student_id', 'phone', 'date_of_birth', 'program', 
                  'enrollment_date', 'status', 'gpa', 'address', 
                  'postcode', 'state', 'international', 'scholarship']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'program': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Bachelor of IT', 'Bachelor of IT'),
                ('Bachelor of Business', 'Bachelor of Business'),
                ('Diploma of IT', 'Diploma of IT'),
                ('Diploma of Business', 'Diploma of Business'),
            ]),
            'enrollment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Active', 'Active'),
                ('On Leave', 'On Leave'),
                ('Graduated', 'Graduated'),
                ('Withdrawn', 'Withdrawn'),
            ]),
            'gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'postcode': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('VIC', 'Victoria'),
                ('NSW', 'New South Wales'),
                ('QLD', 'Queensland'),
                ('WA', 'Western Australia'),
                ('SA', 'South Australia'),
            ]),
            'international': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'scholarship': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'course_id': forms.TextInput(attrs={'class': 'form-control'}),
            'course_code': forms.TextInput(attrs={'class': 'form-control'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            'instructor': forms.TextInput(attrs={'class': 'form-control'}),
            'term': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.NumberInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('IT', 'Information Technology'),
                ('Business', 'Business'),
                ('General', 'General Education'),
            ]),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'}),
            'enrolled_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'mode': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('On-campus', 'On-campus'),
                ('Online', 'Online'),
                ('Blended', 'Blended'),
            ]),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = '__all__'
        widgets = {
            'assignment_id': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'assignment_type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Essay', 'Essay'),
                ('Programming Assignment', 'Programming Assignment'),
                ('Case Study', 'Case Study'),
                ('Project', 'Project'),
                ('Report', 'Report'),
            ]),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'submission_type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('File upload', 'File upload'),
                ('Online text', 'Online text'),
                ('Both', 'Both'),
            ]),
            'allow_late': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'late_penalty': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = '__all__'
        widgets = {
            'quiz_id': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'quiz_type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Multiple Choice', 'Multiple Choice'),
                ('True/False', 'True/False'),
                ('Mixed', 'Mixed'),
                ('Short Answer', 'Short Answer'),
            ]),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'attempts_allowed': forms.TextInput(attrs={'class': 'form-control'}),
            'time_limit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shuffle_questions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = '__all__'
        widgets = {
            'grade_id': forms.TextInput(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'assessment_id': forms.TextInput(attrs={'class': 'form-control'}),
            'assessment_type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Assignment', 'Assignment'),
                ('Quiz', 'Quiz'),
                ('Exam', 'Exam'),
            ]),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'submitted_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'graded_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class EnrollmentForm(forms.ModelForm):
    # Add choice fields for better UX
    status = forms.ChoiceField(
        choices=[
            ('Enrolled', 'Enrolled'),
            ('Pending', 'Pending'),
            ('Withdrawn', 'Withdrawn'),
            ('Completed', 'Completed'),
            ('Failed', 'Failed'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='Enrolled'
    )
    
    role = forms.ChoiceField(
        choices=[
            ('Student', 'Student'),
            ('Auditor', 'Auditor'),
            ('TA', 'Teaching Assistant'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='Student'
    )
    
    class Meta:
        model = Enrollment
        fields = '__all__'
        widgets = {
            'enrollment_id': forms.TextInput(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'enrollment_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'final_grade': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
        }


class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = '__all__'
        widgets = {
            'forum_id': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'created_by': forms.TextInput(attrs={'class': 'form-control'}),
            'created_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'posts_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'views': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Open', 'Open'),
                ('Closed', 'Closed'),
                ('Pinned', 'Pinned'),
            ]),
        }

class ResponseTemplateForm(forms.ModelForm):
    class Meta:
        model = ResponseTemplate
        fields = '__all__'
        widgets = {
            'intent': forms.TextInput(attrs={'class': 'form-control'}),
            'template': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class KnowledgeBaseForm(forms.ModelForm):
    class Meta:
        model = KnowledgeBase
        fields = ['category', 'title', 'content', 'keywords']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Policy', 'Policy'),
                ('FAQ', 'FAQ'),
                ('Course', 'Course'),
                ('Technical', 'Technical'),
            ]),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }