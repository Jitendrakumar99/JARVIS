"""
Admin Routes - Student Management & Dashboard
"""
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Admin, Student
from face.face_engine import FaceEngine
from rag.embedder import TextEmbedder

admin_bp = Blueprint('admin', __name__)

# Initialize engines (lazy loading)
face_engine = None
text_embedder = None


def get_face_engine():
    global face_engine
    if face_engine is None:
        face_engine = FaceEngine()
    return face_engine


def get_text_embedder():
    global text_embedder
    if text_embedder is None:
        text_embedder = TextEmbedder()
    return text_embedder


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@admin_bp.route('/profile')
@login_required
def profile():
    """Admin profile page"""
    return render_template('admin/profile.html', user=current_user)


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard with statistics"""
    total_students = Student.query.count()
    departments = db.session.query(Student.department, db.func.count(Student.id))\
        .group_by(Student.department).all()
    year_stats = db.session.query(Student.year, db.func.count(Student.id))\
        .group_by(Student.year).all()
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         departments=departments,
                         year_stats=year_stats,
                         recent_students=recent_students)


@admin_bp.route('/students')
@login_required
def students():
    """List all students"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '')
    department = request.args.get('department', '')
    
    query = Student.query
    
    if search:
        query = query.filter(
            (Student.name.ilike(f'%{search}%')) |
            (Student.roll_no.ilike(f'%{search}%')) |
            (Student.email.ilike(f'%{search}%'))
        )
    
    if department:
        query = query.filter(Student.department == department)
    
    students = query.order_by(Student.name).paginate(page=page, per_page=per_page)
    departments = db.session.query(Student.department).distinct().all()
    
    return render_template('admin/students.html',
                         students=students,
                         departments=[d[0] for d in departments],
                         search=search,
                         selected_department=department)


@admin_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add new student"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            roll_no = request.form.get('roll_no')
            department = request.form.get('department')
            year = int(request.form.get('year'))
            email = request.form.get('email')
            phone = request.form.get('phone')
            
            # Parse JSON fields
            skills = [s.strip() for s in request.form.get('skills', '').split(',') if s.strip()]
            projects = [p.strip() for p in request.form.get('projects', '').split(',') if p.strip()]
            internships = [i.strip() for i in request.form.get('internships', '').split(',') if i.strip()]
            
            # Check for existing roll number
            if Student.query.filter_by(roll_no=roll_no).first():
                flash('A student with this roll number already exists.', 'error')
                return redirect(url_for('admin.add_student'))
            
            # Create student
            student = Student(
                name=name,
                roll_no=roll_no,
                department=department,
                year=year,
                email=email,
                phone=phone
            )
            student.skills = skills
            student.projects = projects
            student.internships = internships
            
            # Handle image upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    student.image_path = f"uploads/{filename}"
                    
                    # Extract face embedding
                    try:
                        fe = get_face_engine()
                        embedding = fe.get_face_embedding(filepath)
                        if embedding is not None:
                            student.face_embedding = embedding
                    except Exception as e:
                        print(f"Face embedding error: {e}")
            
            # Generate text embedding for RAG
            try:
                te = get_text_embedder()
                text_emb = te.embed_text(student.to_text())
                student.text_embedding = text_emb
            except Exception as e:
                print(f"Text embedding error: {e}")
            
            db.session.add(student)
            db.session.commit()
            
            flash(f'Student {name} added successfully!', 'success')
            return redirect(url_for('admin.students'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'error')
    
    departments = ['CSE', 'ECE', 'EEE', 'ME', 'CE', 'IT', 'AIDS', 'AIML', 'CSE-DS']
    return render_template('admin/student_form.html', 
                         student=None, 
                         departments=departments,
                         action='Add')


@admin_bp.route('/students/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    """Edit existing student"""
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            student.name = request.form.get('name')
            student.roll_no = request.form.get('roll_no')
            student.department = request.form.get('department')
            student.year = int(request.form.get('year'))
            student.email = request.form.get('email')
            student.phone = request.form.get('phone')
            
            student.skills = [s.strip() for s in request.form.get('skills', '').split(',') if s.strip()]
            student.projects = [p.strip() for p in request.form.get('projects', '').split(',') if p.strip()]
            student.internships = [i.strip() for i in request.form.get('internships', '').split(',') if i.strip()]
            
            # Handle new image upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename and allowed_file(file.filename):
                    # Delete old image if exists
                    if student.image_path:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                              student.image_path.replace('uploads/', ''))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    student.image_path = f"uploads/{filename}"
                    
                    # Update face embedding
                    try:
                        fe = get_face_engine()
                        embedding = fe.get_face_embedding(filepath)
                        if embedding is not None:
                            student.face_embedding = embedding
                    except Exception as e:
                        print(f"Face embedding error: {e}")
            
            # Update text embedding
            try:
                te = get_text_embedder()
                text_emb = te.embed_text(student.to_text())
                student.text_embedding = text_emb
            except Exception as e:
                print(f"Text embedding error: {e}")
            
            db.session.commit()
            flash(f'Student {student.name} updated successfully!', 'success')
            return redirect(url_for('admin.students'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'error')
    
    departments = ['CSE', 'ECE', 'EEE', 'ME', 'CE', 'IT', 'AIDS', 'AIML', 'CSE-DS']
    return render_template('admin/student_form.html',
                         student=student,
                         departments=departments,
                         action='Edit')


@admin_bp.route('/students/<int:id>/delete', methods=['POST'])
@login_required
def delete_student(id):
    """Delete student"""
    student = Student.query.get_or_404(id)
    
    try:
        # Delete image file
        if student.image_path:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                  student.image_path.replace('uploads/', ''))
            if os.path.exists(filepath):
                os.remove(filepath)
        
        name = student.name
        db.session.delete(student)
        db.session.commit()
        flash(f'Student {name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'error')
    
    return redirect(url_for('admin.students'))


@admin_bp.route('/api/students')
@login_required
def api_students():
    """API endpoint to get all students as JSON"""
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])
