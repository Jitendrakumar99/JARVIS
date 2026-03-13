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
        user_query_clean = user_query.strip()
        
        # Step 0: Check for exact ID or Roll Number match (High Precision)
        import re
        is_identifier = re.match(r'^[a-zA-Z0-9]{8,15}$', user_query_clean) or user_query_clean.isdigit()
        
        relevant_students = []
        if is_identifier:
            # Check roll number
            exact_student = Student.query.filter(Student.roll_no.ilike(user_query_clean)).first()
            if not exact_student and user_query_clean.isdigit():
                # Check DB ID
                exact_student = Student.query.get(int(user_query_clean))
            
            if exact_student:
                relevant_students = [exact_student]
        
        # Step 1: Normal Retrieval (if no exact identifier match found or we want more context)
        if not relevant_students:
            ret = get_retriever()
            relevant_students = ret.retrieve(user_query, top_k=50, threshold=0.3)
            
            # Determine if we need keyword fallback
            is_aggregate = any(w in user_query.lower() for w in ['count', 'total', 'how many', 'all', 'list', 'show'])
            
            if len(relevant_students) < 5 or is_aggregate:
                # Clean keywords for matching
                search_stop_words = {'search', 'find', 'student', 'students', 'show', 'me', 'all', 'from', 'list', 'the', 'of', 'in', 'who', 'is', 'a'}
                keywords = [w.lower() for w in user_query.split() if w.lower() not in search_stop_words]
                
                from sqlalchemy import or_, cast, String
                existing_ids = {s.id for s in relevant_students}
                
                if is_aggregate and not keywords:
                     keyword_results = Student.query.limit(50).all()
                elif keywords:
                    filters = []
                    for keyword in keywords:
                        filters.append(Student.name.ilike(f'%{keyword}%'))
                        filters.append(Student.roll_no.ilike(f'%{keyword}%'))
                        filters.append(Student.department.ilike(f'%{keyword}%'))
                        filters.append(Student._skills.ilike(f'%{keyword}%'))
                        filters.append(Student._projects.ilike(f'%{keyword}%'))
                        filters.append(cast(Student.year, String).ilike(f'%{keyword}%'))
                    
                    # Limit keyword results to keep context clean
                    kw_limit = 50 if is_aggregate else 10
                    keyword_results = Student.query.filter(or_(*filters)).limit(kw_limit).all()
                else:
                    keyword_results = []

                for s in keyword_results:
                    if s.id not in existing_ids:
                        relevant_students.append(s)
        
        # Step 2: Build context from students
        if relevant_students:
            # We'll provide up to 30 records to the context for aggregate results, 10 for specific ones.
            ctx_limit = 30 if any(w in user_query.lower() for w in ['all', 'show', 'list', 'every', 'count']) else 10
            context_students = relevant_students[:ctx_limit]
            
            context = f"Total matching students found: {len(relevant_students)}\n"
            if len(relevant_students) > ctx_limit:
                 context += f"(Note: Only showing the first {ctx_limit} records to maintain clarity.)\n"
            context += "\n\n"
            
            context += "\n\n---\n\n".join([
                f"Student Data Record {i+1}:\n{s.to_text()}"
                for i, s in enumerate(context_students)
            ])
            # Sync the list of students to show as cards with the context provided
            display_students = context_students
        else:
            context = "No students matching those specific criteria were found in the database."
            display_students = []
        
        # Step 3: Generate response using Groq
        gc = get_groq_client()
        response = gc.generate_response(user_query, context)
        
        # Include student cards for display
        student_cards = [s.to_dict() for s in display_students]
        
        return jsonify({
            'response': response,
            'students': student_cards,
            'sources_count': len(relevant_students),
            'debug': {
                'db_total': Student.query.count(),
                'keywords_found': len(keyword_results) if 'keyword_results' in locals() else 0,
                'rag_found': len(relevant_students) - (len(keyword_results) if 'keyword_results' in locals() else 0),
                'displayed': len(display_students)
            }
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
