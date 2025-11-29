from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    program = models.CharField(max_length=100)
    enrollment_date = models.DateField(default=timezone.now)  # <- default added
    status = models.CharField(max_length=20, default='Active')
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    address = models.TextField(blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    state = models.CharField(max_length=10, blank=True)
    international = models.BooleanField(default=False)
    scholarship = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    class Meta:
        ordering = ['student_id']

class Course(models.Model):
    course_id = models.CharField(max_length=50, unique=True)
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=200)
    instructor = models.CharField(max_length=100)
    term = models.CharField(max_length=50)
    level = models.IntegerField()
    credits = models.IntegerField()
    department = models.CharField(max_length=50)
    max_students = models.IntegerField(default=50)
    enrolled_count = models.IntegerField(default=0)
    mode = models.CharField(max_length=20, default='On-campus')
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
    
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"
    
    class Meta:
        ordering = ['course_code', 'term']

class Enrollment(models.Model):
    enrollment_id = models.CharField(max_length=20, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField()
    role = models.CharField(max_length=20, default='Student')
    status = models.CharField(max_length=20, default='Enrolled')
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.student_id} enrolled in {self.course.course_code}"
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrollment_date']

class Assignment(models.Model):
    assignment_id = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    assignment_type = models.CharField(max_length=50)
    description = models.TextField()
    max_marks = models.IntegerField()
    weight = models.IntegerField()
    due_date = models.DateTimeField()
    submission_type = models.CharField(max_length=50)
    allow_late = models.BooleanField(default=False)
    late_penalty = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.course.course_code} - {self.title}"
    
    class Meta:
        ordering = ['due_date']

class Quiz(models.Model):
    quiz_id = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    quiz_type = models.CharField(max_length=50)
    max_marks = models.IntegerField()
    duration_minutes = models.IntegerField()
    date = models.DateTimeField()
    attempts_allowed = models.CharField(max_length=20)
    time_limit = models.BooleanField(default=True)
    shuffle_questions = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.course.course_code} - {self.title}"
    
    class Meta:
        ordering = ['date']

class Grade(models.Model):
    grade_id = models.CharField(max_length=20, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    assessment_id = models.CharField(max_length=50)
    assessment_type = models.CharField(max_length=20)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    submitted_date = models.DateTimeField()
    graded_date = models.DateTimeField()
    feedback = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.student.student_id} - {self.assessment_id}: {self.percentage}%"
    
    class Meta:
        ordering = ['-submitted_date']

class Forum(models.Model):
    forum_id = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forums')
    topic = models.CharField(max_length=200)
    created_by = models.CharField(max_length=50)
    created_date = models.DateField()
    posts_count = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='Open')
    
    def __str__(self):
        return f"{self.course.course_code} - {self.topic}"
    
    class Meta:
        ordering = ['-created_date']

class Query(models.Model):
    query_id = models.CharField(max_length=20, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='queries', null=True, blank=True)
    query_text = models.TextField()
    intent = models.CharField(max_length=50)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default='Pending')
    priority = models.CharField(max_length=20, default='Medium')
    response_text = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.query_id} - {self.intent}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Queries'

class ResponseTemplate(models.Model):
    intent = models.CharField(max_length=50, unique=True)
    template = models.TextField()
    variations = models.JSONField(default=list)
    
    def __str__(self):
        return self.intent
    
    class Meta:
        ordering = ['intent']

class KnowledgeBase(models.Model):
    category = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    content = models.TextField()
    keywords = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.category} - {self.title}"
    
    class Meta:
        ordering = ['category', 'title']
