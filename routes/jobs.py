"""
Jobs Routes - AI-Powered Job Application Assistant
"""
from flask import Blueprint, render_template, request, jsonify
from models import db, Student, Job
from rag.groq_client import GroqClient

jobs_bp = Blueprint('jobs', __name__)

# Lazy load Groq client
groq_client = None


def get_groq_client():
    global groq_client
    if groq_client is None:
        groq_client = GroqClient()
    return groq_client


@jobs_bp.route('/')
def index():
    """Job assistant main page"""
    students = Student.query.order_by(Student.name).all()
    return render_template('jobs/index.html', students=students)


@jobs_bp.route('/analyze', methods=['POST'])
def analyze_job():
    """Analyze job description and find suitable students"""
    data = request.get_json()
    job_description = data.get('job_description', '')
    
    if not job_description:
        return jsonify({'error': 'No job description provided'}), 400
    
    try:
        # Get all students
        students = Student.query.all()
        
        if not students:
            return jsonify({
                'error': 'No students in database',
                'suitable_students': [],
                'analysis': 'No students found to match against.'
            })
        
        # Build student context
        student_summaries = "\n\n".join([
            f"ID: {s.id}, Name: {s.name}, Department: {s.department}, "
            f"Skills: {', '.join(s.skills)}, Projects: {', '.join(s.projects)}"
            for s in students
        ])
        
        # Use Groq to analyze and match
        gc = get_groq_client()
        
        prompt = f"""Analyze this job description and find suitable students from the database.

Job Description:
{job_description}

Available Students:
{student_summaries}

Provide:
1. Key requirements extracted from job description
2. Top 3-5 most suitable students with their IDs and reasons
3. Skills gap analysis

Format your response in a clear, structured way."""

        analysis = gc.generate_raw(prompt)
        
        # Extract mentioned student IDs and get their data
        mentioned_ids = []
        for s in students:
            if str(s.id) in analysis or s.name.lower() in analysis.lower():
                mentioned_ids.append(s.id)
        
        suitable_students = [s.to_dict() for s in students if s.id in mentioned_ids[:5]]
        
        return jsonify({
            'analysis': analysis,
            'suitable_students': suitable_students,
            'total_students': len(students)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/generate-resume', methods=['POST'])
def generate_resume():
    """Generate resume bullet points for a student based on job"""
    data = request.get_json()
    student_id = data.get('student_id')
    job_description = data.get('job_description', '')
    
    if not student_id:
        return jsonify({'error': 'No student selected'}), 400
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    try:
        gc = get_groq_client()
        
        prompt = f"""Generate powerful resume bullet points for this student tailored to the job description.

Student Profile:
{student.to_text()}

Job Description:
{job_description if job_description else 'General software engineering role'}

Generate:
1. 5-7 strong resume bullet points using the STAR method (Situation, Task, Action, Result)
2. Each bullet should start with a strong action verb
3. Include quantifiable achievements where possible
4. Tailor points to match job requirements

Format each bullet point on a new line starting with •"""

        resume_points = gc.generate_raw(prompt)
        
        return jsonify({
            'student': student.to_dict(),
            'resume_points': resume_points
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """Generate cover letter for a student"""
    data = request.get_json()
    student_id = data.get('student_id')
    job_description = data.get('job_description', '')
    company_name = data.get('company_name', 'the company')
    role = data.get('role', 'the position')
    
    if not student_id:
        return jsonify({'error': 'No student selected'}), 400
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    try:
        gc = get_groq_client()
        
        prompt = f"""Write a professional cover letter for this student applying to the specified role.

Student Profile:
{student.to_text()}

Company: {company_name}
Role: {role}

Job Description:
{job_description if job_description else 'Not specified - write a general cover letter'}

Requirements:
1. Professional and enthusiastic tone
2. Highlight relevant skills and experiences
3. Show genuine interest in the company
4. Keep it concise (3-4 paragraphs)
5. Include a strong opening and closing"""

        cover_letter = gc.generate_raw(prompt)
        
        return jsonify({
            'student': student.to_dict(),
            'cover_letter': cover_letter,
            'company': company_name,
            'role': role
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/auto-fill', methods=['POST'])
def auto_fill():
    """Auto-fill common job application fields"""
    data = request.get_json()
    student_id = data.get('student_id')
    fields = data.get('fields', [])
    
    if not student_id:
        return jsonify({'error': 'No student selected'}), 400
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    try:
        gc = get_groq_client()
        
        fields_str = ", ".join(fields) if fields else "all common job application fields"
        
        prompt = f"""Generate answers for job application form fields based on this student's profile.

Student Profile:
{student.to_text()}

Fill these fields: {fields_str}

Common fields to fill if not specified:
- Why do you want to work here?
- What are your strengths?
- Describe a challenging project
- Where do you see yourself in 5 years?
- Why should we hire you?

Provide clear, concise answers suitable for form fields. Format as:
Field: Answer"""

        filled_fields = gc.generate_raw(prompt)
        
        return jsonify({
            'student': student.to_dict(),
            'filled_fields': filled_fields
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
