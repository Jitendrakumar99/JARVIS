"""
Sample Data Script
Adds sample students to the database for demo purposes
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Student, Admin

# Sample student data
SAMPLE_STUDENTS = [
    {
        "name": "Rahul Sharma",
        "roll_no": "21CSE001",
        "department": "CSE",
        "year": 4,
        "email": "rahul.sharma@college.edu",
        "phone": "9876543210",
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "Flask"],
        "projects": ["Face Recognition Attendance System", "Sentiment Analysis on Twitter Data", "Chatbot using BERT"],
        "internships": ["Google Summer of Code 2024", "AI Research Intern at IIT Delhi"]
    },
    {
        "name": "Priya Patel",
        "roll_no": "21CSE002",
        "department": "CSE",
        "year": 4,
        "email": "priya.patel@college.edu",
        "phone": "9876543211",
        "skills": ["Java", "Spring Boot", "React", "PostgreSQL", "Docker"],
        "projects": ["E-commerce Platform", "Hospital Management System", "Online Banking App"],
        "internships": ["TCS Digital Intern", "Infosys Software Developer Intern"]
    },
    {
        "name": "Arjun Kumar",
        "roll_no": "21CSE003",
        "department": "CSE",
        "year": 3,
        "email": "arjun.kumar@college.edu",
        "phone": "9876543212",
        "skills": ["Python", "Django", "JavaScript", "MongoDB", "AWS"],
        "projects": ["Social Media Dashboard", "REST API Development", "Cloud Deployment Pipeline"],
        "internships": ["Amazon Web Services Intern"]
    },
    {
        "name": "Sneha Reddy",
        "roll_no": "21ECE001",
        "department": "ECE",
        "year": 4,
        "email": "sneha.reddy@college.edu",
        "phone": "9876543213",
        "skills": ["MATLAB", "Embedded C", "VHDL", "Arduino", "Raspberry Pi"],
        "projects": ["IoT Smart Home System", "Signal Processing for Audio", "Drone Control System"],
        "internships": ["Texas Instruments Embedded Intern", "ISRO Project Trainee"]
    },
    {
        "name": "Vikram Singh",
        "roll_no": "21ME001",
        "department": "ME",
        "year": 3,
        "email": "vikram.singh@college.edu",
        "phone": "9876543214",
        "skills": ["AutoCAD", "SolidWorks", "ANSYS", "3D Printing", "CNC Programming"],
        "projects": ["Automotive Engine Design", "Heat Exchanger Optimization", "Robotic Arm Prototype"],
        "internships": ["Tata Motors Summer Intern"]
    },
    {
        "name": "Ananya Gupta",
        "roll_no": "21AIDS001",
        "department": "AIDS",
        "year": 4,
        "email": "ananya.gupta@college.edu",
        "phone": "9876543215",
        "skills": ["Python", "R", "Pandas", "Scikit-learn", "Tableau", "Power BI"],
        "projects": ["Customer Churn Prediction", "Sales Forecasting Model", "COVID-19 Data Analysis Dashboard"],
        "internships": ["Deloitte Data Analytics Intern", "Microsoft Data Science Intern"]
    },
    {
        "name": "Karthik Rajan",
        "roll_no": "21AIML001",
        "department": "AIML",
        "year": 4,
        "email": "karthik.rajan@college.edu",
        "phone": "9876543216",
        "skills": ["Python", "PyTorch", "Computer Vision", "NLP", "Transformers", "LangChain"],
        "projects": ["RAG-based QA System", "Object Detection for Autonomous Vehicles", "Text Summarization using GPT"],
        "internships": ["NVIDIA AI Research Intern", "OpenAI Fellows Program"]
    },
    {
        "name": "Divya Menon",
        "roll_no": "21IT001",
        "department": "IT",
        "year": 3,
        "email": "divya.menon@college.edu",
        "phone": "9876543217",
        "skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB"],
        "projects": ["Portfolio Website", "Task Management App", "Real-time Chat Application"],
        "internships": ["Zoho Web Developer Intern"]
    },
    {
        "name": "Aditya Verma",
        "roll_no": "21CSE004",
        "department": "CSE",
        "year": 2,
        "email": "aditya.verma@college.edu",
        "phone": "9876543218",
        "skills": ["C++", "Data Structures", "Algorithms", "Competitive Programming"],
        "projects": ["Algorithm Visualizer", "Competitive Programming Solutions Repository"],
        "internships": []
    },
    {
        "name": "Meera Krishnan",
        "roll_no": "21CSE-DS001",
        "department": "CSE-DS",
        "year": 4,
        "email": "meera.krishnan@college.edu",
        "phone": "9876543219",
        "skills": ["Python", "SQL", "Apache Spark", "Hadoop", "Data Engineering", "ETL"],
        "projects": ["Data Pipeline for E-commerce", "Real-time Analytics Dashboard", "Data Warehouse Design"],
        "internships": ["Flipkart Data Engineering Intern", "Netflix Data Platform Intern"]
    }
]


def add_sample_data():
    """Add sample students to database"""
    app = create_app('development')
    
    with app.app_context():
        # Check if students already exist
        existing = Student.query.count()
        if existing > 0:
            print(f"Database already has {existing} students.")
            response = input("Add more sample data? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
        
        added = 0
        for data in SAMPLE_STUDENTS:
            # Check if roll number exists
            if Student.query.filter_by(roll_no=data['roll_no']).first():
                print(f"Skipping {data['name']} - already exists")
                continue
            
            student = Student(
                name=data['name'],
                roll_no=data['roll_no'],
                department=data['department'],
                year=data['year'],
                email=data['email'],
                phone=data['phone']
            )
            student.skills = data['skills']
            student.projects = data['projects']
            student.internships = data['internships']
            
            db.session.add(student)
            added += 1
            print(f"Added: {data['name']} ({data['department']})")
        
        db.session.commit()
        print(f"\n✅ Added {added} sample students!")
        print(f"Total students in database: {Student.query.count()}")


if __name__ == '__main__':
    print("=" * 50)
    print("  Sample Data Generator")
    print("  Smart College Student Assistance Portal")
    print("=" * 50)
    print()
    add_sample_data()
