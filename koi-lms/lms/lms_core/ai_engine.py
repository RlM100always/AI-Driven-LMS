import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import ResponseTemplate, KnowledgeBase, Assignment, Quiz, Course, Grade

class AIQueryEngine:
    
    INTENT_KEYWORDS = {
        'assignment_deadline': ['assignment', 'due', 'deadline', 'submit', 'submission'],
        'grade_inquiry': ['grade', 'mark', 'score', 'result', 'performance'],
        'course_content': ['lecture', 'material', 'resource', 'slide', 'content', 'topic'],
        'enrollment_help': ['enroll', 'registration', 'add course', 'drop course'],
        'technical_issue': ['login', 'access', 'error', 'problem', 'issue', 'broken'],
        'exam_schedule': ['exam', 'test', 'final', 'midterm', 'schedule'],
        'fee_payment': ['fee', 'payment', 'tuition', 'cost', 'pay'],
        'resource_access': ['download', 'access', 'library', 'book', 'reference'],
        'extension_request': ['extension', 'late', 'postpone', 'delay'],
        'general_inquiry': ['help', 'question', 'how', 'what', 'when', 'where']
    }
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.load_templates()
    
    def load_templates(self):
        try:
            self.templates = {
                rt.intent: rt.template 
                for rt in ResponseTemplate.objects.all()
            }
        except:
            self.templates = {}
    
    def detect_intent(self, query_text):
        query_lower = query_text.lower()
        intent_scores = {}
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            intent_scores[intent] = score
        
        if max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        
        return 'general_inquiry'
    
    def extract_entities(self, query_text):
        entities = {
            'course_code': None,
            'assignment_id': None,
            'date': None
        }
        
        # Extract course code (e.g., COMP101, WEB201)
        course_match = re.search(r'\b[A-Z]{3,4}\d{3}\b', query_text)
        if course_match:
            entities['course_code'] = course_match.group(0)
        
        # Extract assignment number
        assignment_match = re.search(r'assignment\s*(\d+)', query_text, re.IGNORECASE)
        if assignment_match:
            entities['assignment_id'] = assignment_match.group(1)
        
        return entities
    
    def generate_response(self, query_text, student=None, context=None):
        intent = self.detect_intent(query_text)
        entities = self.extract_entities(query_text)
        
        if intent == 'assignment_deadline':
            return self.handle_assignment_query(entities, student)
        elif intent == 'grade_inquiry':
            return self.handle_grade_query(entities, student)
        elif intent == 'course_content':
            return self.handle_course_content(entities, student)
        elif intent == 'technical_issue':
            return self.handle_technical_issue()
        elif intent == 'exam_schedule':
            return self.handle_exam_schedule(entities, student)
        else:
            return self.handle_general_query(query_text, intent)
    
    def handle_assignment_query(self, entities, student):
        if not entities['course_code']:
            return {
                'intent': 'assignment_deadline',
                'response': 'Please specify which course you need assignment information for (e.g., COMP101).',
                'confidence': 0.5
            }
        
        try:
            course = Course.objects.filter(
                course_code=entities['course_code']
            ).first()
            
            if not course:
                return {
                    'intent': 'assignment_deadline',
                    'response': f"I couldn't find the course {entities['course_code']}. Please check the course code.",
                    'confidence': 0.6
                }
            
            assignments = Assignment.objects.filter(course=course).order_by('due_date')
            
            if not assignments.exists():
                return {
                    'intent': 'assignment_deadline',
                    'response': f"There are no assignments listed for {course.course_code} yet.",
                    'confidence': 0.8
                }
            
            response = f"Here are the assignments for {course.course_code}:\n\n"
            for i, assignment in enumerate(assignments[:5], 1):
                response += f"{i}. {assignment.title}\n"
                response += f"   Due: {assignment.due_date.strftime('%d %B %Y, %I:%M %p')}\n"
                response += f"   Max Marks: {assignment.max_marks}\n\n"
            
            return {
                'intent': 'assignment_deadline',
                'response': response,
                'confidence': 0.9,
                'data': [{'title': a.title, 'due_date': str(a.due_date)} for a in assignments]
            }
        except Exception as e:
            return {
                'intent': 'assignment_deadline',
                'response': f"I encountered an error retrieving assignment information: {str(e)}",
                'confidence': 0.3
            }
    
    def handle_grade_query(self, entities, student):
        if not student:
            return {
                'intent': 'grade_inquiry',
                'response': 'Please log in to view your grades.',
                'confidence': 0.5
            }
        
        try:
            if entities['course_code']:
                course = Course.objects.filter(course_code=entities['course_code']).first()
                if course:
                    grades = Grade.objects.filter(student=student, course=course)
                    response = f"Your grades for {course.course_code}:\n\n"
                else:
                    return {
                        'intent': 'grade_inquiry',
                        'response': f"Course {entities['course_code']} not found.",
                        'confidence': 0.6
                    }
            else:
                grades = Grade.objects.filter(student=student)[:10]
                response = "Your recent grades:\n\n"
            
            if not grades.exists():
                return {
                    'intent': 'grade_inquiry',
                    'response': 'No grades available yet.',
                    'confidence': 0.8
                }
            
            for grade in grades:
                response += f"• {grade.course.course_code} - {grade.assessment_type}\n"
                response += f"  Score: {grade.marks_obtained}/{grade.max_marks} ({grade.percentage}%)\n\n"
            
            return {
                'intent': 'grade_inquiry',
                'response': response,
                'confidence': 0.9
            }
        except Exception as e:
            return {
                'intent': 'grade_inquiry',
                'response': f"Error retrieving grades: {str(e)}",
                'confidence': 0.3
            }
    
    def handle_course_content(self, entities, student):
        response = "Course materials are available in your Moodle dashboard. "
        response += "Go to your enrolled courses and click on the course to access:\n\n"
        response += "• Lecture slides and notes\n"
        response += "• Reading materials\n"
        response += "• Video lectures\n"
        response += "• Tutorial exercises\n\n"
        response += "If you need specific materials, please mention the course code and week number."
        
        return {
            'intent': 'course_content',
            'response': response,
            'confidence': 0.7
        }
    
    def handle_technical_issue(self):
        response = "For technical issues, please try the following:\n\n"
        response += "1. Clear your browser cache and cookies\n"
        response += "2. Try using a different browser (Chrome, Firefox, Edge)\n"
        response += "3. Ensure you're using the correct login credentials\n"
        response += "4. Check your internet connection\n\n"
        response += "If the problem persists, contact IT Support:\n"
        response += "Email: itsupport@koi.edu.au\n"
        response += "Phone: +61 3 9602 4110"
        
        return {
            'intent': 'technical_issue',
            'response': response,
            'confidence': 0.9
        }
    
    def handle_exam_schedule(self, entities, student):
        if not entities['course_code']:
            return {
                'intent': 'exam_schedule',
                'response': 'Please specify which course you need exam information for.',
                'confidence': 0.5
            }
        
        try:
            course = Course.objects.filter(course_code=entities['course_code']).first()
            if not course:
                return {
                    'intent': 'exam_schedule',
                    'response': f"Course {entities['course_code']} not found.",
                    'confidence': 0.6
                }
            
            quizzes = Quiz.objects.filter(course=course).order_by('date')
            
            if not quizzes.exists():
                return {
                    'intent': 'exam_schedule',
                    'response': f"No exams/quizzes scheduled for {course.course_code} yet.",
                    'confidence': 0.8
                }
            
            response = f"Exam schedule for {course.course_code}:\n\n"
            for quiz in quizzes:
                response += f"• {quiz.title}\n"
                response += f"  Date: {quiz.date.strftime('%d %B %Y, %I:%M %p')}\n"
                response += f"  Duration: {quiz.duration_minutes} minutes\n\n"
            
            return {
                'intent': 'exam_schedule',
                'response': response,
                'confidence': 0.9
            }
        except Exception as e:
            return {
                'intent': 'exam_schedule',
                'response': f"Error retrieving exam schedule: {str(e)}",
                'confidence': 0.3
            }
    
    def handle_general_query(self, query_text, intent):
        kb_items = KnowledgeBase.objects.all()
        
        if kb_items.exists():
            kb_texts = [f"{item.title} {item.content}" for item in kb_items]
            kb_texts.append(query_text)
            
            try:
                tfidf_matrix = self.vectorizer.fit_transform(kb_texts)
                cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1]).flatten()
                best_match_idx = cosine_similarities.argmax()
                
                if cosine_similarities[best_match_idx] > 0.3:
                    best_item = list(kb_items)[best_match_idx]
                    return {
                        'intent': intent,
                        'response': f"{best_item.title}\n\n{best_item.content}",
                        'confidence': float(cosine_similarities[best_match_idx])
                    }
            except:
                pass
        
        return {
            'intent': intent,
            'response': self.get_default_response(intent),
            'confidence': 0.5
        }
    
    def get_default_response(self, intent):
        default_responses = {
            'general_inquiry': "I'm here to help! You can ask me about:\n• Assignment deadlines\n• Your grades\n• Course materials\n• Exam schedules\n• Technical issues\n\nWhat would you like to know?",
            'enrollment_help': "For enrollment assistance, please visit the Student Portal or contact the Registrar's Office at registrar@koi.edu.au",
            'fee_payment': "For fee payment information, please contact the Finance Office:\nEmail: finance@koi.edu.au\nPhone: +61 3 9602 4110",
        }
        
        return default_responses.get(intent, "I'm not sure how to help with that. Please contact student support at support@koi.edu.au")
