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
from django.views.decorators.csrf import csrf_exempt  # <-- ADD THIS IMPORT
import uuid
import os



from .models import (
    Student, Course, Enrollment, Assignment, 
    Quiz, Grade, Forum, Query, ConversationState,QueryLog

)
from .forms import SignUpForm, QueryForm
import json

# Initialize AI Engine

def home(request):
    """Redirect to dashboard or login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

from .models import Student
import random


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Generate unique student_id
            while True:
                student_id = f"ST{random.randint(1000, 9999999)}"  # Example: S1234
                if not Student.objects.filter(student_id=student_id).exists():
                    break
            
            # Auto-create student profile with student_id
            Student.objects.create(
                user=user,
                student_id=student_id,
                program='',  # temporary empty or default
            )
            
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




# Load JSON data with UTF-8 encoding
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'data.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except UnicodeDecodeError:
        # Try with different encodings if utf-8 fails
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            return json.load(file)
    except FileNotFoundError:
        # Create default data if file doesn't exist
        return create_default_data()

def create_default_data():
    """Create default JSON data structure"""
    default_data = {
        "intents": {
            "greeting": {
                "patterns": ["hello", "hi", "hey"],
                "responses": ["Hello! How can I help you?"],
                "suggestions": []
            }
        },
        "user_data": {
            "name": "Student",
            "student_id": "S000000"
        },
        "system_info": {
            "academic_year": "2024",
            "semester": "Semester 1"
        }
    }
    
    # Save it for future use
    file_path = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(default_data, file, indent=2, ensure_ascii=False)
    
    return default_data

# Preprocess data
try:
    data = load_data()
except Exception as e:
    print(f"Error loading data: {e}")
    data = create_default_data()

class AIAssistant:
    def __init__(self):
        self.intents = data['intents']
        self.user_data = data.get('user_data', {})
        self.system_info = data.get('system_info', {})
        self.conversation_history = []
        
    # ... rest of your AIAssistant class methods remain the same ...
    def preprocess_text(self, text):
        """Clean and preprocess input text"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def get_intent(self, text):
        """Determine the intent of the user query"""
        processed_text = self.preprocess_text(text)
        
        # Check for exact matches first
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data['patterns']:
                if pattern.lower() in processed_text:
                    return intent_name, 0.9
        
        # Check for keyword matches
        best_intent = None
        best_score = 0
        
        for intent_name, intent_data in self.intents.items():
            score = 0
            words = processed_text.split()
            
            for pattern in intent_data['patterns']:
                pattern_words = pattern.split()
                matches = sum(1 for word in words if word in pattern_words)
                if matches > 0:
                    score = matches / len(pattern_words)
                    if score > best_score:
                        best_score = score
                        best_intent = intent_name
        
        return best_intent, best_score
    
    def extract_entities(self, text):
        """Extract relevant entities from text"""
        entities = {}
        processed_text = text.lower()
        
        # Extract course codes
        course_patterns = [r'comp\d{3}', r'web\d{3}', r'data\d{3}', r'math\d{3}']
        for pattern in course_patterns:
            matches = re.findall(pattern, processed_text)
            if matches:
                entities['course'] = matches[0].upper()
        
        # Extract assignment numbers
        assignment_match = re.search(r'assignment\s*(\d+)', processed_text, re.IGNORECASE)
        if assignment_match:
            entities['assignment_number'] = assignment_match.group(1)
        
        return entities
    
    def generate_response(self, intent, entities=None):
        """Generate response based on intent and entities"""
        if intent not in self.intents:
            return "I'm not sure how to help with that. Could you rephrase your question?"
        
        intent_data = self.intents[intent]
        response = random.choice(intent_data['responses'])
        
        # Personalize response with user data
        response = response.replace("{student_name}", self.user_data.get('name', 'Student'))
        response = response.replace("{student_id}", self.user_data.get('student_id', 'S000000'))
        
        # Add course-specific information if entity exists
        if entities and 'course' in entities:
            course = entities['course']
            if 'courses' in self.user_data and course in self.user_data['courses']:
                response += f"\n\n**Specific to {course}:**\n"
                if course == "COMP101":
                    response += "• Instructor: Dr. Sarah Chen\n• Next class: Tomorrow 9 AM\n• Current topic: Python Functions"
                elif course == "WEB201":
                    response += "• Instructor: Prof. James Wilson\n• Next lab: Tuesday 2 PM\n• Current project: E-commerce Website"
        
        return response
    
    def get_suggestions(self, intent):
        """Get follow-up suggestions based on intent"""
        if intent in self.intents:
            return self.intents[intent].get('suggestions', [])
        return ["Ask about assignments", "Check grades", "View timetable"]
    
    def process_query(self, query):
        """Main processing function"""
        start_time = datetime.now()
        
        # Get intent and confidence
        intent, confidence = self.get_intent(query)
        
        # Extract entities
        entities = self.extract_entities(query)
        
        # Generate response
        if intent:
            response = self.generate_response(intent, entities)
        else:
            response = "I'm not sure I understand. Could you try rephrasing your question? For example:\n• 'When is my next assignment due?'\n• 'What are my grades?'\n• 'Show my class schedule'"
            intent = "unknown"
            confidence = 0.1
        
        # Get suggestions
        suggestions = self.get_suggestions(intent)
        
        # Check for spelling corrections
        corrected_query = self.correct_spelling(query)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Store in history
        self.conversation_history.append({
            'query': query,
            'response': response,
            'intent': intent,
            'timestamp': datetime.now().isoformat(),
            'confidence': confidence
        })
        
        # Keep only last 10 conversations
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return {
            'response': response,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'suggestions': suggestions,
            'corrected_query': corrected_query if corrected_query != query else None,
            'processing_time': processing_time,
            'user_data': self.user_data,
            'timestamp': datetime.now().strftime("%H:%M")
        }
    
    def correct_spelling(self, text):
        """Simple spelling correction"""
        common_mistakes = {
            'assigment': 'assignment',
            'timetible': 'timetable',
            'grads': 'grades',
            'exams': 'exams',
            'libary': 'library'
        }
        
        words = text.lower().split()
        corrected_words = []
        
        for word in words:
            if word in common_mistakes:
                corrected_words.append(common_mistakes[word])
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)

# Global assistant instance
assistant = AIAssistant()

@login_required
def ai_chat(request):
    """Render the main chat interface"""
    # Get recent conversations (last 5)
    recent_conversations = assistant.conversation_history[-5:] if assistant.conversation_history else []
    
    context = {
        'conversation_history': recent_conversations,
        'recent_queries': len(assistant.conversation_history),
        'confidence': sum([conv.get('confidence', 0) for conv in assistant.conversation_history]) / len(assistant.conversation_history) if assistant.conversation_history else 0,
        'user_name': assistant.user_data.get('name', 'Student'),
        'student_id': assistant.user_data.get('student_id', 'S000000')
    }
    
    return render(request, 'lms_core/ai_query.html', context)

@csrf_exempt
@login_required
def ai_chat_api(request):
    """API endpoint for processing chat queries"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
            
            if not query:
                return JsonResponse({
                    'success': False,
                    'error': 'Empty query'
                })
            
            # Process the query
            result = assistant.process_query(query)
            
            return JsonResponse({
                'success': True,
                'query': query,
                **result
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
def clear_conversation(request):
    """Clear conversation history"""
    assistant.conversation_history = []
    return redirect('ai_chat')
