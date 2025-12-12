# ============================================
# FILE: lms_core/views.py
# ============================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.utils import timezone
from .forms import ProfileUpdateForm

from .models import (
    Student, Course, Enrollment, Assignment, 
    Quiz, Grade, Forum, Query
)
from .forms import SignUpForm, QueryForm
from .ai_engine import AIQueryEngine
import json

# Initialize AI Engine
ai_engine = AIQueryEngine()

def home(request):
    """Redirect to dashboard or login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

from .models import Student

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto-create student profile
            Student.objects.create(user=user)
            
            login(request, user)
            messages.success(request, 'Account created successfully! Please complete your profile.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'lms_core/signup.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'lms_core/login.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')



@login_required
def update_profile(request):
    student = request.user.student_profile  # OneToOne relation
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('update_profile')  # match the URL name
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(
            instance=student,
            initial={
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        )

    return render(request, 'profile/update_profile.html', {'form': form})




@login_required
def dashboard(request):
    """Main dashboard view"""
    try:
        student = request.user.student_profile
    except:
        messages.warning(request, 'Student profile not found. Please contact administration.')
        return redirect('login')
    
    # Get all enrollments with different statuses
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related('course').order_by('-enrollment_date')
    
    # Get enrolled courses (active)
    enrolled_courses = enrollments.filter(status='Enrolled')
    
    # Get completed courses
    completed_courses = enrollments.filter(status='Completed')
    
    # Get failed courses
    failed_courses = enrollments.filter(status='Failed')
    
    # Get withdrawn courses
    withdrawn_courses = enrollments.filter(status='Withdrawn')
    
    # Get all active courses for assignments
    active_courses = enrollments.filter(status='Enrolled')
    
    # Get upcoming assignments from active courses
    upcoming_assignments = []
    for enrollment in active_courses:
        assignments = Assignment.objects.filter(
            course=enrollment.course,
            due_date__gte=timezone.now()
        ).order_by('due_date')[:3]
        upcoming_assignments.extend(assignments)
    
    # Sort by due date and limit
    upcoming_assignments = sorted(upcoming_assignments, key=lambda x: x.due_date)[:5]
    
    # Get recent grades from all courses
    recent_grades = Grade.objects.filter(
        student=student
    ).select_related('course').order_by('-graded_date')[:5]
    
    # Calculate statistics
    all_grades = Grade.objects.filter(student=student)
    avg_grade = all_grades.aggregate(Avg('percentage'))['percentage__avg'] or 0
    
    # Calculate GPA (example calculation)
    total_credits = 0
    weighted_points = 0
    
    for enrollment in completed_courses:
        # Get the latest grade for this course
        latest_grade = Grade.objects.filter(
            student=student,
            course=enrollment.course
        ).order_by('-graded_date').first()
        
        if latest_grade and latest_grade.percentage is not None:
            # Convert percentage to GPA points
            if latest_grade.percentage >= 85:
                points = 4.0  # HD
            elif latest_grade.percentage >= 75:
                points = 3.5  # D
            elif latest_grade.percentage >= 65:
                points = 3.0  # C
            elif latest_grade.percentage >= 50:
                points = 2.0  # P
            else:
                points = 0.0  # F
            
            # Assume each course has 3 credits (adjust based on your model)
            credits = 3
            weighted_points += points * credits
            total_credits += credits
    
    gpa = weighted_points / total_credits if total_credits > 0 else 0.0
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'enrolled_courses': enrolled_courses,
        'completed_courses': completed_courses,
        'failed_courses': failed_courses,
        'withdrawn_courses': withdrawn_courses,
        'active_courses': active_courses,
        'upcoming_assignments': upcoming_assignments,
        'recent_grades': recent_grades,
        'avg_grade': round(avg_grade, 2),
        'gpa': round(gpa, 2),
        'total_courses': enrollments.count(),
        'enrolled_count': enrolled_courses.count(),
        'completed_count': completed_courses.count(),
        'failed_count': failed_courses.count(),
        'withdrawn_count': withdrawn_courses.count(),
    }
    
    return render(request, 'lms_core/dashboard.html', context)

@login_required
def course_detail(request, course_id):
    """View course details"""
    try:
        student = request.user.student_profile
    except:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')
    
    course = get_object_or_404(Course, course_id=course_id)
    
    # Check enrollment
    enrollment = Enrollment.objects.filter(
        student=student,
        course=course
    ).first()
    
    if not enrollment:
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('dashboard')
    
    # Get course materials
    assignments = Assignment.objects.filter(course=course).order_by('due_date')
    quizzes = Quiz.objects.filter(course=course).order_by('date')
    forums = Forum.objects.filter(course=course).order_by('-created_date')
    grades = Grade.objects.filter(student=student, course=course).order_by('-graded_date')
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'assignments': assignments,
        'quizzes': quizzes,
        'forums': forums,
        'grades': grades,
    }
    
    return render(request, 'lms_core/course_detail.html', context)

@login_required
def assignments_view(request):
    """View all assignments"""
    try:
        student = request.user.student_profile
    except:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')
    
    enrolled_courses = Course.objects.filter(
        enrollments__student=student,
        enrollments__status='Enrolled'
    )
    
    assignments = Assignment.objects.filter(
        course__in=enrolled_courses
    ).select_related('course').order_by('due_date')
    
    submitted_assignments = Grade.objects.filter(
        student=student,
        assessment_type='Assignment'
    ).values_list('assessment_id', flat=True)
    
    context = {
        'assignments': assignments,
        'submitted_assignments': submitted_assignments,
    }
    
    return render(request, 'lms_core/assignments.html', context)

@login_required
def quizzes_view(request):
    """View all quizzes"""
    try:
        student = request.user.student_profile
    except:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')
    
    enrolled_courses = Course.objects.filter(
        enrollments__student=student,
        enrollments__status='Enrolled'
    )
    
    quizzes = Quiz.objects.filter(
        course__in=enrolled_courses
    ).select_related('course').order_by('date')
    
    completed_quizzes = Grade.objects.filter(
        student=student,
        assessment_type='Quiz'
    ).values_list('assessment_id', flat=True)
    
    context = {
        'quizzes': quizzes,
        'completed_quizzes': completed_quizzes,
    }
    
    return render(request, 'lms_core/quizzes.html', context)

@login_required
def grades_view(request):
    """View all grades"""
    try:
        student = request.user.student_profile
    except:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')
    
    enrolled_courses = Course.objects.filter(
        enrollments__student=student
    ).distinct()
    
    course_grades = []
    for course in enrolled_courses:
        grades = Grade.objects.filter(
            student=student,
            course=course
        ).order_by('assessment_type', '-graded_date')
        
        if grades.exists():
            avg = grades.aggregate(Avg('percentage'))['percentage__avg']
            course_grades.append({
                'course': course,
                'grades': grades,
                'average': round(avg, 2) if avg else 0
            })
    
    context = {
        'course_grades': course_grades,
    }
    
    return render(request, 'lms_core/grades.html', context)

@login_required
def forums_view(request):
    """View forum discussions"""
    try:
        student = request.user.student_profile
    except:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')
    
    enrolled_courses = Course.objects.filter(
        enrollments__student=student,
        enrollments__status='Enrolled'
    )
    
    forums = Forum.objects.filter(
        course__in=enrolled_courses
    ).select_related('course').order_by('-created_date')
    
    context = {
        'forums': forums,
    }
    
    return render(request, 'lms_core/forums.html', context)

@login_required
def ai_query_view(request):
    """AI-powered query interface"""
    try:
        student = request.user.student_profile
    except:
        student = None
    
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            query_text = form.cleaned_data['query_text']
            
            # Generate AI response
            ai_response = ai_engine.generate_response(query_text, student)
            
            # Save query
            query = Query.objects.create(
                query_id=f"Q{Query.objects.count() + 1:06d}",
                student=student,
                query_text=query_text,
                intent=ai_response['intent'],
                response_text=ai_response['response'],
                status='Resolved'
            )
            
            context = {
                'form': QueryForm(),
                'query': query_text,
                'response': ai_response['response'],
                'intent': ai_response['intent'],
                'confidence': ai_response.get('confidence', 0.5)
            }
            
            return render(request, 'lms_core/ai_query.html', context)
    else:
        form = QueryForm()
    
    recent_queries = Query.objects.filter(
        student=student
    ).order_by('-timestamp')[:10] if student else []
    
    context = {
        'form': form,
        'recent_queries': recent_queries
    }
    
    return render(request, 'lms_core/ai_query.html', context)

@login_required
def api_query(request):
    """API endpoint for AI queries"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query_text = data.get('query', '')
            
            student = None
            try:
                student = request.user.student_profile
            except:
                pass
            
            ai_response = ai_engine.generate_response(query_text, student)
            
            return JsonResponse({
                'success': True,
                'response': ai_response['response'],
                'intent': ai_response['intent'],
                'confidence': ai_response.get('confidence', 0.5)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
