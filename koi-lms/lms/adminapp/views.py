from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from lms_core.models import (
    Student, Course, Enrollment, Assignment, 
    Quiz, Grade, Forum, Query, ResponseTemplate, KnowledgeBase
)
from .models import Teacher
from .forms import *
from lms_core.models import Enrollment,Student,Course
from .decorators import teacher_required
import csv
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db.models import Q


def admin_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if hasattr(user, 'teacher_profile'):
                    login(request, user)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "You do not have teacher access.")
            else:
                messages.error(request, "Invalid username or password")

            return redirect('admin_login')

    else:
        form = TeacherLoginForm()

    return render(request, 'adminapp/login.html', {'form': form})


def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            # Create User first
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            # Create Teacher profile with extra fields
            teacher = Teacher.objects.create(
                user=user,
                employee_id=form.cleaned_data.get('employee_id', None),
                phone=form.cleaned_data.get('phone', ''),
                department=form.cleaned_data.get('department', ''),
                designation=form.cleaned_data.get('designation', 'Lecturer'),
                specialization=form.cleaned_data.get('specialization', ''),
                office_location=form.cleaned_data.get('office_location', ''),
                is_admin=form.cleaned_data.get('is_admin', False)
            )

            # Optional: log the teacher in immediately
            login(request, user)
            messages.success(request, "Signup successful! Welcome.")
            return redirect('admin_dashboard')

    else:
        form = TeacherSignupForm()

    return render(request, 'adminapp/signup.html', {'form': form})



@teacher_required
def admin_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('admin_login')

@teacher_required
def admin_dashboard(request):
    # Statistics
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.filter(status='Enrolled').count()
    total_assignments = Assignment.objects.count()
    total_quizzes = Quiz.objects.count()
    
    # Recent activities
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrollment_date')[:5]
    recent_queries = Query.objects.select_related('student').order_by('-timestamp')[:5]
    
    # Course statistics
    courses_by_department = Course.objects.values('department').annotate(count=Count('id'))
    
    # Student performance
    avg_gpa = Student.objects.filter(status='Active').aggregate(Avg('gpa'))['gpa__avg'] or 0
    
    # Enrollment by status
    enrollment_status = Enrollment.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_assignments': total_assignments,
        'total_quizzes': total_quizzes,
        'recent_enrollments': recent_enrollments,
        'recent_queries': recent_queries,
        'courses_by_department': courses_by_department,
        'avg_gpa': round(avg_gpa, 2),
        'enrollment_status': enrollment_status,
    }
    
    return render(request, 'adminapp/dashboard.html', context)

# ============================================
# STUDENT MANAGEMENT VIEWS
# ============================================

@teacher_required
def student_list(request):
    students = Student.objects.select_related('user').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        students = students.filter(status=status_filter)
    
    program_filter = request.GET.get('program', '')
    if program_filter:
        students = students.filter(program=program_filter)
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'students': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'program_filter': program_filter,
    }
    
    return render(request, 'adminapp/students/list.html', context)

@teacher_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    grades = Grade.objects.filter(student=student).select_related('course')
    queries = Query.objects.filter(student=student).order_by('-timestamp')
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'grades': grades,
        'queries': queries,
    }
    
    return render(request, 'adminapp/students/detail.html', context)

@teacher_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            # Create user first
            user = User.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                password='koi@123'  # Default password
            )
            
            # Create student profile
            student = form.save(commit=False)
            student.user = user
            student.save()
            
            messages.success(request, f'Student {student.student_id} created successfully!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm()
    
    return render(request, 'adminapp/students/create.html', {'form': form})

@teacher_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            
            # Update user info
            student.user.first_name = request.POST.get('first_name')
            student.user.last_name = request.POST.get('last_name')
            student.user.email = request.POST.get('email')
            student.user.save()
            
            messages.success(request, 'Student updated successfully!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
        form.fields['first_name'].initial = student.user.first_name
        form.fields['last_name'].initial = student.user.last_name
        form.fields['email'].initial = student.user.email
        form.fields['username'].initial = student.user.username
    
    return render(request, 'adminapp/students/edit.html', {'form': form, 'student': student})

@teacher_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student_id = student.student_id
        user = student.user
        student.delete()
        user.delete()
        
        messages.success(request, f'Student {student_id} deleted successfully!')
        return redirect('student_list')
    
    return render(request, 'adminapp/students/delete_confirm.html', {'student': student})

# Continue with remaining CRUD views...
"""

# ============================================
# FILE 5: adminapp/views.py (Part 2 - Course CRUD)
# ============================================
"""
# ... continuing from views.py Part 1

# ============================================
# COURSE MANAGEMENT VIEWS
# ============================================

@teacher_required
def course_list(request):
    courses = Course.objects.all()
    
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(course_code__icontains=search_query) |
            Q(course_name__icontains=search_query)
        )
    
    department_filter = request.GET.get('department', '')
    if department_filter:
        courses = courses.filter(department=department_filter)
    
    paginator = Paginator(courses, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'adminapp/courses/list.html', {
        'courses': page_obj,
        'search_query': search_query,
        'department_filter': department_filter,
    })

@teacher_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    assignments = Assignment.objects.filter(course=course)
    quizzes = Quiz.objects.filter(course=course)
    forums = Forum.objects.filter(course=course)
    
    return render(request, 'adminapp/courses/detail.html', {
        'course': course,
        'enrollments': enrollments,
        'assignments': assignments,
        'quizzes': quizzes,
        'forums': forums,
    })

@teacher_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, 'Course created successfully!')
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm()
    
    return render(request, 'adminapp/courses/create.html', {'form': form})

@teacher_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'adminapp/courses/edit.html', {'form': form, 'course': course})

@teacher_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        course_code = course.course_code
        course.delete()
        messages.success(request, f'Course {course_code} deleted successfully!')
        return redirect('course_list')
    
    return render(request, 'adminapp/courses/delete_confirm.html', {'course': course})

# ============================================
# ASSIGNMENT MANAGEMENT VIEWS
# ============================================

@teacher_required
def assignment_list(request):
    # GET parameters
    search_query = request.GET.get('search', '')
    course_filter = request.GET.get('course', '')

    # Start with all assignments
    assignments = Assignment.objects.select_related('course').all()

    # Apply course filter
    if course_filter:
        assignments = assignments.filter(course__course_code=course_filter)

    # Apply search filter (search in title or assignment type)
    if search_query:
        assignments = assignments.filter(
            Q(title__icontains=search_query) |
            Q(assignment_type__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(assignments, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    # All courses for dropdown
    all_courses = Course.objects.all()

    context = {
        'assignments': page_obj,
        'search_query': search_query,
        'course_filter': course_filter,
        'all_courses': all_courses,
    }
    return render(request, 'adminapp/assignments/list.html', context)
    
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    return render(request, 'adminapp/assignments/detail.html', {'assignment': assignment})
    

@teacher_required
def assignment_create(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('assignment_list')
    else:
        form = AssignmentForm()
    
    return render(request, 'adminapp/assignments/create.html', {'form': form})

@teacher_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully!')
            return redirect('assignment_list')
    else:
        form = AssignmentForm(instance=assignment)
    
    return render(request, 'adminapp/assignments/edit.html', {'form': form, 'assignment': assignment})

@teacher_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully!')
        return redirect('assignment_list')
    
    return render(request, 'adminapp/assignments/delete_confirm.html', {'assignment': assignment})

# ============================================
# QUIZ MANAGEMENT VIEWS
# ============================================

@teacher_required
def quiz_list(request):
    quizzes = Quiz.objects.select_related('course').all()
    paginator = Paginator(quizzes, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'adminapp/quizzes/list.html', {'quizzes': page_obj})

def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'adminapp/quizzes/detail.html', {'quiz': quiz})


@teacher_required
def quiz_create(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            messages.success(request, 'Quiz created successfully!')
            return redirect('quiz_list')
    else:
        form = QuizForm()
    
    return render(request, 'adminapp/quizzes/create.html', {'form': form})

@teacher_required
def quiz_edit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('quiz_list')
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'adminapp/quizzes/edit.html', {'form': form, 'quiz': quiz})

@teacher_required
def quiz_delete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('quiz_list')
    
    return render(request, 'adminapp/quizzes/delete_confirm.html', {'quiz': quiz})

# ============================================
# GRADE MANAGEMENT VIEWS
# ============================================

@teacher_required
def grade_list(request):
    grades = Grade.objects.select_related('student', 'course').all()
    
    student_filter = request.GET.get('student', '')
    if student_filter:
        grades = grades.filter(student__student_id=student_filter)
    
    course_filter = request.GET.get('course', '')
    if course_filter:
        grades = grades.filter(course__course_code=course_filter)
    
    paginator = Paginator(grades, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'adminapp/grades/list.html', {
        'grades': page_obj,
        'student_filter': student_filter,
        'course_filter': course_filter,
    })
    

def grade_detail(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    return render(request, 'adminapp/grades/detail.html', {'grade': grade})
    

@teacher_required
def grade_create(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save()
            messages.success(request, 'Grade created successfully!')
            return redirect('grade_list')
    else:
        form = GradeForm()
    
    return render(request, 'adminapp/grades/create.html', {'form': form})

@teacher_required
def grade_edit(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade updated successfully!')
            return redirect('grade_list')
    else:
        form = GradeForm(instance=grade)
    
    return render(request, 'adminapp/grades/edit.html', {'form': form, 'grade': grade})

@teacher_required
def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Grade deleted successfully!')
        return redirect('grade_list')
    
    return render(request, 'adminapp/grades/delete_confirm.html', {'grade': grade})

# ============================================
# ENROLLMENT MANAGEMENT VIEWS
# ============================================

@teacher_required
def enrollment_list(request):
    enrollments = Enrollment.objects.select_related('student', 'course').all()
    paginator = Paginator(enrollments, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'adminapp/enrollments/list.html', {'enrollments': page_obj})


def enrollment_detail(request, pk):
    enrollment = Enrollment.objects.get(pk=pk)
    return render(request, "adminapp/enrollments/detail.html", {"enrollment": enrollment})


@teacher_required
def enrollment_create(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, 'Enrollment created successfully!')
            return redirect('enrollment_list')
    else:
        form = EnrollmentForm()
    
    return render(request, 'adminapp/enrollments/create.html', {'form': form})


@teacher_required
def enrollment_edit(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            # Update enrolled_count in the Course model
            if 'status' in form.changed_data:
                new_status = form.cleaned_data['status']
                old_status = enrollment.status
                
                if old_status == 'Enrolled' and new_status != 'Enrolled':
                    # Decrease enrolled_count
                    enrollment.course.enrolled_count = max(0, enrollment.course.enrolled_count - 1)
                    enrollment.course.save()
                elif old_status != 'Enrolled' and new_status == 'Enrolled':
                    # Increase enrolled_count
                    enrollment.course.enrolled_count += 1
                    enrollment.course.save()
            
            form.save()
            messages.success(request, 'Enrollment updated successfully!')
            return redirect('enrollment_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EnrollmentForm(instance=enrollment)
    
    context = {
        'form': form,
        'enrollment': enrollment,
    }
    
    return render(request, 'adminapp/enrollments/edit.html', context)


@teacher_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, 'Enrollment deleted successfully!')
        return redirect('enrollment_list')
    
    return render(request, 'adminapp/enrollments/delete_confirm.html', {'enrollment': enrollment})

# ============================================
# ANALYTICS & REPORTS
# ============================================

@teacher_required
def analytics_overview(request):
    # Performance analytics
    grade_distribution = Grade.objects.values('percentage').annotate(count=Count('id'))
    
    # Enrollment trends
    enrollment_by_term = Enrollment.objects.values('course__term').annotate(count=Count('id'))
    
    # Top performing students
    top_students = Student.objects.annotate(
        avg_grade=Avg('grades__percentage')
    ).order_by('-avg_grade')[:10]
    
    # Course popularity
    popular_courses = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:10]
    
    context = {
        'grade_distribution': grade_distribution,
        'enrollment_by_term': enrollment_by_term,
        'top_students': top_students,
        'popular_courses': popular_courses,
    }
    
    return render(request, 'adminapp/analytics/overview.html', context)

@teacher_required
def export_students(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Email', 'Program', 'Status', 'GPA'])
    
    students = Student.objects.select_related('user').all()
    for student in students:
        writer.writerow([
            student.student_id,
            student.user.get_full_name(),
            student.user.email,
            student.program,
            student.status,
            student.gpa
        ])
    
    return response

@teacher_required
def export_grades(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="grades.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Grade ID', 'Student', 'Course', 'Assessment', 'Marks', 'Percentage'])
    
    grades = Grade.objects.select_related('student', 'course').all()
    for grade in grades:
        writer.writerow([
            grade.grade_id,
            grade.student.student_id,
            grade.course.course_code,
            grade.assessment_id,
            f"{grade.marks_obtained}/{grade.max_marks}",
            grade.percentage
        ])
    
    return response




