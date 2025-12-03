"""
King's Own Institute - Complete LMS Dataset Generator
Generates Moodle-like data for AI training and LMS simulation
Australian context with realistic course structures
"""

import csv
import json
import random
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd
import os

# Initialize Faker with Australian locale
fake = Faker(['en_AU'])
random.seed(42)
Faker.seed(42)

# Create output directory
os.makedirs('koi_lms_dataset', exist_ok=True)

# ============================================
# CONFIGURATION & DATA STRUCTURES
# ============================================

# Australian terms/semesters
TERMS = ['Semester 1 2024', 'Semester 2 2024', 'Summer 2024/25']

# King's Own Institute courses (realistic IT/Business programs)
COURSES_DATA = [
    # IT Courses
    {'course_code': 'COMP101', 'course_name': 'Introduction to Programming', 'level': 1, 'credits': 12, 'department': 'IT'},
    {'course_code': 'COMP201', 'course_name': 'Data Structures and Algorithms', 'level': 2, 'credits': 12, 'department': 'IT'},
    {'course_code': 'COMP301', 'course_name': 'Database Management Systems', 'level': 3, 'credits': 12, 'department': 'IT'},
    {'course_code': 'COMP401', 'course_name': 'Artificial Intelligence', 'level': 4, 'credits': 12, 'department': 'IT'},
    {'course_code': 'WEB201', 'course_name': 'Web Development', 'level': 2, 'credits': 12, 'department': 'IT'},
    {'course_code': 'NET301', 'course_name': 'Computer Networks', 'level': 3, 'credits': 12, 'department': 'IT'},
    {'course_code': 'SEC401', 'course_name': 'Cybersecurity Fundamentals', 'level': 4, 'credits': 12, 'department': 'IT'},
    {'course_code': 'DATA301', 'course_name': 'Data Science and Analytics', 'level': 3, 'credits': 12, 'department': 'IT'},
    {'course_code': 'SOFT301', 'course_name': 'Software Engineering', 'level': 3, 'credits': 12, 'department': 'IT'},
    {'course_code': 'CLOUD401', 'course_name': 'Cloud Computing', 'level': 4, 'credits': 12, 'department': 'IT'},
    
    # Business Courses
    {'course_code': 'BUS101', 'course_name': 'Introduction to Business', 'level': 1, 'credits': 12, 'department': 'Business'},
    {'course_code': 'ACC201', 'course_name': 'Financial Accounting', 'level': 2, 'credits': 12, 'department': 'Business'},
    {'course_code': 'MKT201', 'course_name': 'Marketing Principles', 'level': 2, 'credits': 12, 'department': 'Business'},
    {'course_code': 'MGT301', 'course_name': 'Strategic Management', 'level': 3, 'credits': 12, 'department': 'Business'},
    {'course_code': 'FIN301', 'course_name': 'Corporate Finance', 'level': 3, 'credits': 12, 'department': 'Business'},
    
    # General Education
    {'course_code': 'MATH101', 'course_name': 'Mathematics for IT', 'level': 1, 'credits': 12, 'department': 'General'},
    {'course_code': 'STAT201', 'course_name': 'Statistics for Business', 'level': 2, 'credits': 12, 'department': 'General'},
    {'course_code': 'COMM101', 'course_name': 'Professional Communication', 'level': 1, 'credits': 12, 'department': 'General'},
]

# Instructors
INSTRUCTORS = [
    'Dr. Sarah Mitchell', 'Prof. James Chen', 'Dr. Emily Roberts',
    'Dr. Michael Wong', 'Prof. Lisa Anderson', 'Dr. David Kumar',
    'Dr. Rachel Thompson', 'Prof. Peter Williams', 'Dr. Amanda Lee',
    'Dr. Christopher Brown', 'Prof. Jennifer Davis', 'Dr. Mark Wilson'
]

# Assignment types
ASSIGNMENT_TYPES = [
    'Essay', 'Programming Assignment', 'Case Study', 'Project',
    'Report', 'Presentation', 'Lab Exercise', 'Research Paper',
    'Group Project', 'Tutorial Exercise'
]

# Query intents for AI system
QUERY_INTENTS = [
    'assignment_deadline', 'grade_inquiry', 'course_content',
    'enrollment_help', 'technical_issue', 'exam_schedule',
    'fee_payment', 'resource_access', 'extension_request',
    'general_inquiry', 'policy_question', 'assessment_criteria'
]

# ============================================
# GENERATOR FUNCTIONS
# ============================================

def generate_students(num_students=500):
    """Generate student data"""
    students = []
    programs = ['Bachelor of IT', 'Bachelor of Business', 'Diploma of IT', 'Diploma of Business']
    
    for i in range(1, num_students + 1):
        student = {
            'student_id': f'KOI{str(i).zfill(6)}',
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': f'student{i}@koi.edu.au',
            'phone': fake.phone_number(),
            'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=45).strftime('%Y-%m-%d'),
            'program': random.choice(programs),
            'enrollment_date': fake.date_between(start_date='-3y', end_date='today').strftime('%Y-%m-%d'),
            'status': random.choice(['Active', 'Active', 'Active', 'On Leave', 'Graduated']),
            'gpa': round(random.uniform(2.5, 4.0), 2),
            'address': fake.address().replace('\n', ', '),
            'postcode': fake.postcode(),
            'state': random.choice(['VIC', 'NSW', 'QLD', 'WA', 'SA']),
            'international': random.choice([True, False]),
            'scholarship': random.choice([True, False])
        }
        students.append(student)
    
    return students

def generate_courses():
    """Generate course data with instructors and terms"""
    courses = []
    
    for course in COURSES_DATA:
        for term in TERMS:
            course_entry = {
                'course_id': f"{course['course_code']}_{term.replace(' ', '_')}",
                'course_code': course['course_code'],
                'course_name': course['course_name'],
                'instructor': random.choice(INSTRUCTORS),
                'term': term,
                'level': course['level'],
                'credits': course['credits'],
                'department': course['department'],
                'max_students': random.randint(30, 100),
                'enrolled_count': 0,  # Will be updated
                'mode': random.choice(['On-campus', 'Online', 'Blended']),
                'start_date': get_term_dates(term)[0],
                'end_date': get_term_dates(term)[1],
                'description': f"This course covers fundamental and advanced topics in {course['course_name']}.",
            }
            courses.append(course_entry)
    
    return courses

def get_term_dates(term):
    """Get start and end dates for term"""
    if 'Semester 1 2024' in term:
        return ('2024-02-26', '2024-06-14')
    elif 'Semester 2 2024' in term:
        return ('2024-07-15', '2024-11-08')
    else:  # Summer
        return ('2024-12-02', '2025-02-21')

def generate_enrollments(students, courses):
    """Generate student enrollments"""
    enrollments = []
    
    for student in students:
        if student['status'] == 'Graduated':
            continue
            
        # Each student enrolls in 3-5 courses
        num_courses = random.randint(3, 5)
        student_courses = random.sample(courses, min(num_courses, len(courses)))
        
        for course in student_courses:
            # Convert string dates to datetime objects
            start_dt = datetime.strptime(course['start_date'], '%Y-%m-%d')
            end_dt = datetime.strptime(course['end_date'], '%Y-%m-%d')
            
            enrollment = {
                'enrollment_id': f"ENR{len(enrollments) + 1:06d}",
                'student_id': student['student_id'],
                'course_id': course['course_id'],
                'course_code': course['course_code'],
                'term': course['term'],
                'enrollment_date': fake.date_between(
                    start_date=start_dt, 
                    end_date=end_dt
                ).strftime('%Y-%m-%d'),
                'role': 'Student',
                'status': random.choice(['Enrolled', 'Enrolled', 'Enrolled', 'Completed', 'Withdrawn']),
                'final_grade': round(random.uniform(50, 100), 1) if random.random() > 0.3 else None,
            }
            enrollments.append(enrollment)
    
    return enrollments

def generate_assignments(courses):
    """Generate assignments for each course"""
    assignments = []
    
    for course in courses:
        # Each course has 3-6 assignments
        num_assignments = random.randint(3, 6)
        start_date = datetime.strptime(course['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(course['end_date'], '%Y-%m-%d')
        
        for i in range(1, num_assignments + 1):
            due_date = start_date + timedelta(
                days=random.randint(14, (end_date - start_date).days)
            )
            
            assignment = {
                'assignment_id': f"{course['course_id']}_A{i}",
                'course_id': course['course_id'],
                'course_code': course['course_code'],
                'title': f"Assignment {i}: {random.choice(ASSIGNMENT_TYPES)}",
                'assignment_type': random.choice(ASSIGNMENT_TYPES),
                'description': f"Complete the {random.choice(ASSIGNMENT_TYPES).lower()} as per course requirements.",
                'max_marks': random.choice([20, 25, 30, 40, 50, 100]),
                'weight': random.choice([10, 15, 20, 25, 30]),
                'due_date': due_date.strftime('%Y-%m-%d %H:%M:%S'),
                'submission_type': random.choice(['File upload', 'Online text', 'Both']),
                'allow_late': random.choice([True, False]),
                'late_penalty': random.choice([5, 10, 15, 20]) if random.random() > 0.5 else 0,
            }
            assignments.append(assignment)
    
    return assignments

def generate_quizzes(courses):
    """Generate quizzes for each course"""
    quizzes = []
    
    for course in courses:
        # Each course has 2-4 quizzes
        num_quizzes = random.randint(2, 4)
        start_date = datetime.strptime(course['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(course['end_date'], '%Y-%m-%d')
        
        for i in range(1, num_quizzes + 1):
            quiz_date = start_date + timedelta(
                days=random.randint(7, (end_date - start_date).days)
            )
            
            quiz = {
                'quiz_id': f"{course['course_id']}_Q{i}",
                'course_id': course['course_id'],
                'course_code': course['course_code'],
                'title': f"Quiz {i}: {random.choice(['Mid-term', 'Weekly', 'Module', 'Final'])} Assessment",
                'quiz_type': random.choice(['Multiple Choice', 'True/False', 'Mixed', 'Short Answer']),
                'max_marks': random.choice([10, 15, 20, 25, 30]),
                'duration_minutes': random.choice([30, 45, 60, 90]),
                'date': quiz_date.strftime('%Y-%m-%d %H:%M:%S'),
                'attempts_allowed': random.choice([1, 2, 3, 'Unlimited']),
                'time_limit': random.choice([True, False]),
                'shuffle_questions': random.choice([True, False]),
            }
            quizzes.append(quiz)
    
    return quizzes

def generate_grades(enrollments, assignments, quizzes):
    """Generate grades for assignments and quizzes"""
    grades = []
    
    for enrollment in enrollments:
        if enrollment['status'] != 'Enrolled' and enrollment['status'] != 'Completed':
            continue
        
        # Assignment grades
        course_assignments = [a for a in assignments if a['course_id'] == enrollment['course_id']]
        for assignment in course_assignments:
            if random.random() > 0.2:  # 80% submission rate
                grade = {
                    'grade_id': f"GRD{len(grades) + 1:08d}",
                    'student_id': enrollment['student_id'],
                    'course_id': enrollment['course_id'],
                    'assessment_id': assignment['assignment_id'],
                    'assessment_type': 'Assignment',
                    'marks_obtained': round(random.uniform(0.5, 1.0) * assignment['max_marks'], 1),
                    'max_marks': assignment['max_marks'],
                    'percentage': round(random.uniform(50, 100), 1),
                    'submitted_date': (datetime.strptime(assignment['due_date'], '%Y-%m-%d %H:%M:%S') - 
                                     timedelta(days=random.randint(0, 3))).strftime('%Y-%m-%d %H:%M:%S'),
                    'graded_date': (datetime.strptime(assignment['due_date'], '%Y-%m-%d %H:%M:%S') + 
                                  timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d %H:%M:%S'),
                    'feedback': random.choice([
                        'Excellent work!', 'Good effort, well done.', 
                        'Satisfactory. Consider improvement in...',
                        'Well researched and presented.',
                        'Needs improvement in analysis.'
                    ]),
                }
                grades.append(grade)
        
        # Quiz grades
        course_quizzes = [q for q in quizzes if q['course_id'] == enrollment['course_id']]
        for quiz in course_quizzes:
            if random.random() > 0.15:  # 85% participation rate
                grade = {
                    'grade_id': f"GRD{len(grades) + 1:08d}",
                    'student_id': enrollment['student_id'],
                    'course_id': enrollment['course_id'],
                    'assessment_id': quiz['quiz_id'],
                    'assessment_type': 'Quiz',
                    'marks_obtained': round(random.uniform(0.6, 1.0) * quiz['max_marks'], 1),
                    'max_marks': quiz['max_marks'],
                    'percentage': round(random.uniform(60, 100), 1),
                    'submitted_date': quiz['date'],
                    'graded_date': quiz['date'],
                    'feedback': 'Auto-graded',
                }
                grades.append(grade)
    
    return grades

def generate_forums(courses):
    """Generate forum discussions"""
    forums = []
    
    topics = [
        'Week 1 Discussion', 'Assignment Help', 'General Questions',
        'Study Group', 'Project Collaboration', 'Resource Sharing',
        'Exam Preparation', 'Technical Issues', 'Course Feedback'
    ]
    
    for course in courses:
        num_forums = random.randint(5, 10)
        
        # Convert string dates to datetime objects
        start_dt = datetime.strptime(course['start_date'], '%Y-%m-%d')
        end_dt = datetime.strptime(course['end_date'], '%Y-%m-%d')
        
        for i in range(num_forums):
            forum = {
                'forum_id': f"{course['course_id']}_F{i+1}",
                'course_id': course['course_id'],
                'course_code': course['course_code'],
                'topic': random.choice(topics),
                'created_by': random.choice(['Instructor', 'Student']),
                'created_date': fake.date_between(
                    start_date=start_dt,
                    end_date=end_dt
                ).strftime('%Y-%m-%d'),
                'posts_count': random.randint(1, 50),
                'views': random.randint(10, 500),
                'status': random.choice(['Open', 'Closed', 'Pinned']),
            }
            forums.append(forum)
    
    return forums

def generate_queries():
    """Generate sample student queries for AI training"""
    queries = []
    
    query_templates = {
        'assignment_deadline': [
            "When is Assignment 2 due for COMP101?",
            "What's the deadline for the programming assignment?",
            "Can you tell me when I need to submit my essay?",
            "Is there an extension for Assignment 3?",
        ],
        'grade_inquiry': [
            "What's my current grade in Data Structures?",
            "Have the quiz results been released?",
            "Why did I get this mark on my assignment?",
            "Can I see the marking rubric?",
        ],
        'course_content': [
            "Where can I find lecture slides for Week 5?",
            "What topics are covered in the final exam?",
            "Are there any additional resources for this course?",
            "Can you explain the assessment criteria?",
        ],
        'enrollment_help': [
            "How do I enroll in Web Development?",
            "Can I change my course selection?",
            "What are the prerequisites for AI course?",
            "When is the enrollment deadline?",
        ],
        'technical_issue': [
            "I can't access the course materials",
            "The quiz submission isn't working",
            "Login issues with Moodle",
            "Video lectures won't play",
        ],
        'exam_schedule': [
            "When is the final exam for COMP201?",
            "Where will the exam be held?",
            "What's the exam format?",
            "Can I get special consideration for exams?",
        ],
        'fee_payment': [
            "How do I pay my tuition fees?",
            "What's my outstanding balance?",
            "Are there payment plans available?",
            "When is the fee deadline?",
        ],
    }
    
    query_id = 1
    for intent, templates in query_templates.items():
        for template in templates:
            for _ in range(random.randint(3, 8)):
                query = {
                    'query_id': f"Q{query_id:06d}",
                    'student_id': f"KOI{random.randint(1, 500):06d}",
                    'query_text': template,
                    'intent': intent,
                    'timestamp': fake.date_time_between(start_date='-6m', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                    'status': random.choice(['Resolved', 'Pending', 'Resolved', 'Resolved']),
                    'priority': random.choice(['Low', 'Medium', 'High']),
                }
                queries.append(query)
                query_id += 1
    
    return queries

def generate_knowledge_base(courses):
    """Generate knowledge base JSON"""
    knowledge_base = {
        'institution': {
            'name': "King's Own Institute",
            'location': 'Melbourne, Australia',
            'website': 'https://www.koi.edu.au',
            'contact': {
                'phone': '+61 3 9602 4110',
                'email': 'info@koi.edu.au',
                'address': '340 Burnley Street, Richmond VIC 3121'
            }
        },
        'policies': [
            {
                'policy_id': 'POL001',
                'title': 'Academic Integrity Policy',
                'category': 'Academic',
                'content': 'Students must maintain academic honesty in all assessments. Plagiarism and cheating will result in severe penalties.',
                'effective_date': '2024-01-01'
            },
            {
                'policy_id': 'POL002',
                'title': 'Late Submission Policy',
                'category': 'Assessment',
                'content': 'Late submissions will incur a 10% penalty per day unless prior approval is obtained.',
                'effective_date': '2024-01-01'
            },
            {
                'policy_id': 'POL003',
                'title': 'Special Consideration',
                'category': 'Assessment',
                'content': 'Students facing extenuating circumstances may apply for special consideration with supporting documentation.',
                'effective_date': '2024-01-01'
            },
            {
                'policy_id': 'POL004',
                'title': 'Attendance Policy',
                'category': 'Attendance',
                'content': 'Students must maintain 80% attendance in all courses. Failure to do so may result in academic penalties.',
                'effective_date': '2024-01-01'
            },
        ],
        'faqs': [
            {
                'question': 'How do I access course materials?',
                'answer': 'Log in to Moodle with your KOI credentials and navigate to your enrolled courses.',
                'category': 'Technical'
            },
            {
                'question': 'What is the grading scale?',
                'answer': 'HD (80-100), D (70-79), C (60-69), P (50-59), F (0-49)',
                'category': 'Academic'
            },
            {
                'question': 'How do I apply for special consideration?',
                'answer': 'Submit the special consideration form with supporting documents at least 3 days before the due date.',
                'category': 'Assessment'
            },
            {
                'question': 'Can I withdraw from a course?',
                'answer': 'Yes, but you must withdraw before the census date to avoid academic and financial penalties.',
                'category': 'Enrollment'
            },
            {
                'question': 'How do I contact my instructor?',
                'answer': 'Use the messaging system in Moodle or email them directly. Check course outline for office hours.',
                'category': 'Communication'
            },
        ],
        'courses': []
    }
    
    # Add course details
    for course in courses[:5]:  # Sample of courses
        knowledge_base['courses'].append({
            'course_code': course['course_code'],
            'course_name': course['course_name'],
            'instructor': course['instructor'],
            'credits': course['credits'],
            'description': course['description'],
            'learning_outcomes': [
                f"Understand fundamental concepts of {course['course_name']}",
                f"Apply practical skills in {course['course_name']}",
                f"Analyze and solve problems in {course['course_name']}",
                f"Demonstrate proficiency in {course['course_name']}"
            ],
            'assessment': {
                'assignments': '40%',
                'quizzes': '20%',
                'final_exam': '40%'
            }
        })
    
    return knowledge_base

def generate_response_templates():
    """Generate response templates for AI system"""
    responses = [
        {
            'intent': 'assignment_deadline',
            'template': 'The deadline for {assignment_name} in {course_code} is {due_date}. Please ensure you submit before this time.',
            'variations': [
                'Your assignment {assignment_name} is due on {due_date}.',
                '{assignment_name} must be submitted by {due_date} for {course_code}.'
            ]
        },
        {
            'intent': 'grade_inquiry',
            'template': 'Your current grade in {course_code} is {grade}. You can view detailed breakdown in the gradebook.',
            'variations': [
                'You have scored {grade} in {course_code} so far.',
                'Your performance in {course_code} shows a grade of {grade}.'
            ]
        },
        {
            'intent': 'course_content',
            'template': 'Course materials for {course_code} are available in the Moodle course page under {section}.',
            'variations': [
                'You can find {course_code} materials in the {section} section of Moodle.',
                'Access {course_code} content through Moodle > Courses > {course_code} > {section}.'
            ]
        },
        {
            'intent': 'technical_issue',
            'template': 'I understand you are experiencing technical issues. Please try: 1) Clear browser cache, 2) Try different browser, 3) Contact IT support at itsupport@koi.edu.au',
            'variations': [
                'For technical problems, contact IT support or try clearing your browser cache.',
                'Technical issues can often be resolved by logging out and back in. If persisting, email itsupport@koi.edu.au'
            ]
        },
        {
            'intent': 'enrollment_help',
            'template': 'To enroll in {course_code}, log in to student portal and navigate to Course Enrollment. Check prerequisites before enrolling.',
            'variations': [
                'Enrollment for {course_code} can be done through the student portal under Course Management.',
                'Visit the Enrollment section in student portal to add {course_code} to your schedule.'
            ]
        },
    ]
    
    return responses

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    print("🎓 Generating King's Own Institute LMS Dataset...")
    print("=" * 60)
    
    # Generate all data
    print("\n📊 Generating Students...")
    students = generate_students(500)
    
    print("📚 Generating Courses...")
    courses = generate_courses()
    
    print("✏️ Generating Enrollments...")
    enrollments = generate_enrollments(students, courses)
    
    print("📝 Generating Assignments...")
    assignments = generate_assignments(courses)
    
    print("❓ Generating Quizzes...")
    quizzes = generate_quizzes(courses)
    
    print("🎯 Generating Grades...")
    grades = generate_grades(enrollments, assignments, quizzes)
    
    print("💬 Generating Forums...")
    forums = generate_forums(courses)
    
    print("🤖 Generating Queries...")
    queries = generate_queries()
    
    print("📖 Generating Knowledge Base...")
    knowledge_base = generate_knowledge_base(courses)
    
    print("💡 Generating Response Templates...")
    response_templates = generate_response_templates()
    
    # Save to CSV files
    print("\n💾 Saving CSV files...")
    
    pd.DataFrame(students).to_csv('koi_lms_dataset/students.csv', index=False)
    pd.DataFrame(courses).to_csv('koi_lms_dataset/courses.csv', index=False)
    pd.DataFrame(enrollments).to_csv('koi_lms_dataset/enrollments.csv', index=False)
    pd.DataFrame(assignments).to_csv('koi_lms_dataset/assignments.csv', index=False)
    pd.DataFrame(quizzes).to_csv('koi_lms_dataset/quizzes.csv', index=False)
    pd.DataFrame(grades).to_csv('koi_lms_dataset/grades.csv', index=False)
    pd.DataFrame(forums).to_csv('koi_lms_dataset/forums.csv', index=False)
    pd.DataFrame(queries).to_csv('koi_lms_dataset/queries.csv', index=False)
    pd.DataFrame(response_templates).to_csv('koi_lms_dataset/response_templates.csv', index=False)
    
    # Save JSON files
    print("💾 Saving JSON files...")
    with open('koi_lms_dataset/knowledge_base.json', 'w') as f:
        json.dump(knowledge_base, f, indent=2)
    
    # Generate statistics
    print("\n" + "=" * 60)
    print("📈 DATASET STATISTICS")
    print("=" * 60)
    print(f"Students: {len(students)}")
    print(f"Courses: {len(courses)}")
    print(f"Enrollments: {len(enrollments)}")
    print(f"Assignments: {len(assignments)}")
    print(f"Quizzes: {len(quizzes)}")
    print(f"Grades: {len(grades)}")
    print(f"Forums: {len(forums)}")
    print(f"Queries: {len(queries)}")
    print(f"Policies: {len(knowledge_base['policies'])}")
    print(f"FAQs: {len(knowledge_base['faqs'])}")
    
    print("\n✅ Dataset generation complete!")
    print(f"📁 Files saved in: koi_lms_dataset/")
    print("\nGenerated files:")
    print("  • students.csv")
    print("  • courses.csv")
    print("  • enrollments.csv")
    print("  • assignments.csv")
    print("  • quizzes.csv")
    print("  • grades.csv")
    print("  • forums.csv")
    print("  • queries.csv")
    print("  • response_templates.csv")
    print("  • knowledge_base.json")

if __name__ == "__main__":
    main()