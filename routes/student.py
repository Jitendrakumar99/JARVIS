"""
Student Routes - Face Search & Profile Viewing
"""
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from werkzeug.utils import secure_filename
from models import db, Student
from face.face_engine import FaceEngine
from utils.pdf_generator import generate_student_pdf

student_bp = Blueprint('student', __name__)

# Lazy load face engine
face_engine = None


def get_face_engine():
    global face_engine
    if face_engine is None:
        face_engine = FaceEngine()
    return face_engine


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@student_bp.route('/explore')
def explore():
    """Student exploration page with image upload"""
    return render_template('explore/search.html')


@student_bp.route('/explore/search', methods=['POST'])
def search_by_image():
    """Find student by uploaded image using face recognition"""
    if 'photo' not in request.files:
        flash('No image uploaded', 'error')
        return redirect(url_for('student.explore'))
    
    file = request.files['photo']
    
    if file.filename == '':
        flash('No image selected', 'error')
        return redirect(url_for('student.explore'))
    
    if file and allowed_file(file.filename):
        # Save temporary file for processing
        filename = f"search_{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        file.save(temp_path)
        
        try:
            # Check if face recognition (DeepFace) is available
            from face.face_engine import DEEPFACE_AVAILABLE
            if not DEEPFACE_AVAILABLE:
                flash('Face recognition not available. Please install: pip install deepface tf-keras', 'error')
                os.remove(temp_path)
                return redirect(url_for('student.explore'))
            
            # Get all students with face embeddings
            students = Student.query.filter(Student._face_embedding.isnot(None)).all()
            
            if not students:
                # Check total students
                total = Student.query.count()
                if total == 0:
                    flash('No students in database. Please add students through Admin Panel first.', 'warning')
                else:
                    flash(f'Found {total} students but none have face embeddings. Re-add students with photos after installing face-recognition library.', 'warning')
                os.remove(temp_path)
                return redirect(url_for('student.explore'))
            
            # Find matching student
            fe = get_face_engine()
            match = fe.find_matching_student(temp_path, students)
            
            # Clean up temp file
            os.remove(temp_path)
            
            if match:
                student, confidence = match
                return render_template('explore/result.html',
                                     student=student,
                                     confidence=confidence)
            else:
                flash('No matching student found. Please try with a clearer image showing the face.', 'warning')
                return redirect(url_for('student.explore'))
                
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            flash(f'Error processing image: {str(e)}', 'error')
            return redirect(url_for('student.explore'))
    
    flash('Invalid file type. Please upload an image (PNG, JPG, JPEG, GIF).', 'error')
    return redirect(url_for('student.explore'))


@student_bp.route('/student/<int:id>')
def profile(id):
    """View student profile"""
    student = Student.query.get_or_404(id)
    return render_template('explore/profile.html', student=student)


@student_bp.route('/student/<int:id>/download-pdf')
def download_pdf(id):
    """Download student profile as PDF"""
    student = Student.query.get_or_404(id)
    
    try:
        # Generate PDF
        pdf_path = generate_student_pdf(student, current_app.config['UPLOAD_FOLDER'])
        
        # Send file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"{student.name.replace(' ', '_')}_Profile.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('student.profile', id=id))


@student_bp.route('/students/all')
def all_students():
    """View all students (public page)"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    search = request.args.get('search', '')
    department = request.args.get('department', '')
    
    query = Student.query
    
    if search:
        query = query.filter(
            (Student.name.ilike(f'%{search}%')) |
            (Student.roll_no.ilike(f'%{search}%'))
        )
    
    if department:
        query = query.filter(Student.department == department)
    
    students = query.order_by(Student.name).paginate(page=page, per_page=per_page)
    departments = db.session.query(Student.department).distinct().all()
    
    return render_template('explore/all_students.html',
                         students=students,
                         departments=[d[0] for d in departments],
                         search=search,
                         selected_department=department)
