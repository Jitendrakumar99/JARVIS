"""
AI Chat Routes - RAG-based Student Query System
"""
from flask import Blueprint, render_template, request, jsonify
from models import db, Student
from rag.retriever import StudentRetriever
from rag.groq_client import GroqClient

chat_bp = Blueprint('chat', __name__)

# Lazy load components
retriever = None
groq_client = None


def get_retriever():
    global retriever
    if retriever is None:
        retriever = StudentRetriever()
    return retriever


def get_groq_client():
    global groq_client
    if groq_client is None:
        groq_client = GroqClient()
    return groq_client


@chat_bp.route('/')
def chat():
    """Chat interface"""
    return render_template('chat.html')


@chat_bp.route('/query', methods=['POST'])
def query():
    """Process natural language query using RAG pipeline"""
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Step 1: Retrieve relevant students (threshold prevents irrelevant results)
        ret = get_retriever()
        relevant_students = ret.retrieve(user_query, top_k=5, threshold=0.6)
        
        # If no highly relevant students found via embeddings, try explicit database search
        if not relevant_students:
            # Fallback: simple keyword search on name, department, roll_no, and skills
            keywords = user_query.lower().split()
            query = Student.query
            
            for keyword in keywords:
                query = query.filter(
                    (Student.name.ilike(f'%{keyword}%')) |
                    (Student.roll_no.ilike(f'%{keyword}%')) |
                    (Student.department.ilike(f'%{keyword}%')) |
                    (Student._skills.ilike(f'%{keyword}%'))
                )
            
            relevant_students = query.limit(5).all()
        
        # Step 2: Build context from students
        if relevant_students:
            context = "\n\n---\n\n".join([
                f"Student {i+1}:\n{s.to_text()}"
                for i, s in enumerate(relevant_students)
            ])
        else:
            context = "No relevant students found in the database."
        
        # Step 3: Generate response using Groq
        gc = get_groq_client()
        response = gc.generate_response(user_query, context)
        
        # Include student cards for display
        student_cards = [s.to_dict() for s in relevant_students] if relevant_students else []
        
        return jsonify({
            'response': response,
            'students': student_cards,
            'sources_count': len(relevant_students) if relevant_students else 0
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'error': f'Error processing query: {str(e)}',
            'response': "I apologize, but I encountered an error. Please check if the Groq API key is configured correctly.",
            'students': []
        }), 500


@chat_bp.route('/suggestions')
def suggestions():
    """Get query suggestions"""
    suggestions = [
        "Show all students from CSE department",
        "Who has Python and Machine Learning skills?",
        "Find students suitable for AI internship",
        "List students with web development experience",
        "Show details of final year students",
        "Who has done internships at tech companies?",
        "Find students with data science projects"
    ]
    return jsonify({'suggestions': suggestions})
