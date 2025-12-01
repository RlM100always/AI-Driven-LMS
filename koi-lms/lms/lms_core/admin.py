from django.contrib import admin
from .models import (
    Student, Course, Enrollment, Assignment, 
    Quiz, Grade, Forum, Query, ResponseTemplate, KnowledgeBase
)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'program', 'status', 'gpa']
    list_filter = ['status', 'program', 'international']
    search_fields = ['student_id', 'user__username', 'user__email']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'course_name', 'instructor', 'term', 'enrolled_count']
    list_filter = ['term', 'department', 'level']
    search_fields = ['course_code', 'course_name', 'instructor']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['enrollment_id', 'student', 'course', 'status', 'final_grade']
    list_filter = ['status', 'course__term']
    search_fields = ['enrollment_id', 'student__student_id']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['assignment_id', 'course', 'title', 'due_date', 'max_marks']
    list_filter = ['course__term', 'assignment_type']
    search_fields = ['assignment_id', 'title']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['quiz_id', 'course', 'title', 'date', 'max_marks']
    list_filter = ['course__term', 'quiz_type']
    search_fields = ['quiz_id', 'title']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['grade_id', 'student', 'course', 'assessment_type', 'percentage']
    list_filter = ['assessment_type', 'course__term']
    search_fields = ['grade_id', 'student__student_id']

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['forum_id', 'course', 'topic', 'posts_count', 'views', 'status']
    list_filter = ['status', 'course__term']
    search_fields = ['forum_id', 'topic']

@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ['query_id', 'student', 'intent', 'timestamp', 'status']
    list_filter = ['status', 'intent', 'priority']
    search_fields = ['query_id', 'query_text']

@admin.register(ResponseTemplate)
class ResponseTemplateAdmin(admin.ModelAdmin):
    list_display = ['intent', 'template']
    search_fields = ['intent']

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['category', 'title', 'created_at']
    list_filter = ['category']
    search_fields = ['title', 'content']
