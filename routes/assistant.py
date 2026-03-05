"""
Personal Assistant Routes - Conversation History & Persistence
"""
from flask import Blueprint, render_template, request, jsonify
from models import db, AssistantConversation, AssistantMessage
from rag.groq_client import GroqClient
from datetime import datetime

assistant_bp = Blueprint('assistant', __name__)
groq_client_instance = None

def get_groq_client():
    global groq_client_instance
    if groq_client_instance is None:
        groq_client_instance = GroqClient()
    return groq_client_instance

@assistant_bp.route('/')
def assistant_page():
    """Main assistant page with sidebar"""
    conversations = AssistantConversation.query.order_by(AssistantConversation.updated_at.desc()).all()
    return render_template('assistant.html', conversations=conversations)

@assistant_bp.route('/conversation/<int:conv_id>')
def get_conversation(conv_id):
    """Retrieve all messages for a specific conversation"""
    conv = AssistantConversation.query.get_or_404(conv_id)
    messages = [m.to_dict() for m in conv.messages]
    return jsonify({
        'title': conv.title,
        'messages': messages
    })

@assistant_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat interaction with conversation persistence"""
    data = request.get_json()
    user_query = data.get('query', '')
    conv_id = data.get('conversation_id')
    
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    # Find or create conversation
    if conv_id:
        conversation = AssistantConversation.query.get(conv_id)
        if not conversation:
            conversation = AssistantConversation(title=user_query[:40] + "...")
            db.session.add(conversation)
            db.session.commit()
    else:
        conversation = AssistantConversation(title=user_query[:40] + "...")
        db.session.add(conversation)
        db.session.commit()
    
    # Save user message
    user_message = AssistantMessage(
        conversation_id=conversation.id,
        role='user',
        content=user_query
    )
    db.session.add(user_message)
    
    # Get AI Client
    gc = get_groq_client()
    
    # Build Neural Memory Context
    # 1. Long-Term Memory (Global context across all conversations)
    global_messages = AssistantMessage.query.order_by(AssistantMessage.timestamp.desc()).limit(20).all()
    global_messages.reverse()
    
    memory_context = "--- LONG TERM NEURAL MEMORY ---\n"
    for m in global_messages:
        memory_context += f"{m.role.upper()}: {m.content}\n"
    memory_context += "--- END MEMORY ---\n"

    messages = [
        {"role": "system", "content": f"You are J.A.R.V.I.S, an advanced personal assistant. You are sophisticated, intelligent, and helpful. You have a Unified Neural Memory, meaning you remember everything the user tells you across all conversation threads. Use the LONG TERM NEURAL MEMORY provided below to recall previous details like the user's name, projects, or interests.\n\n{memory_context}"}
    ]
    
    # 2. Short-Term Context (Current conversation history)
    history_messages = AssistantMessage.query.filter_by(conversation_id=conversation.id).order_by(AssistantMessage.timestamp.asc()).all()
    
    for m in history_messages:
        messages.append({"role": m.role, "content": m.content})
    
    try:
        # Generate completion using Groq
        if gc.client:
            chat_completion = gc.client.chat.completions.create(
                messages=messages,
                model=gc.model_name
            )
            ai_content = chat_completion.choices[0].message.content
        else:
            ai_content = "Connection to Neural Network failed. Please ensure your GROQ_API_KEY is configured."
        
        # Save assistant message
        assistant_message = AssistantMessage(
            conversation_id=conversation.id,
            role='assistant',
            content=ai_content
        )
        db.session.add(assistant_message)
        
        # Update conversation timestamp for sorting
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'response': ai_content,
            'conversation_id': conversation.id,
            'title': conversation.title
        })
    except Exception as e:
        db.session.rollback()
        print(f"Assistant Chat Error: {e}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/conversations')
def list_conversations():
    """API to get list of conversations"""
    conversations = AssistantConversation.query.order_by(AssistantConversation.updated_at.desc()).all()
    return jsonify([c.to_dict() for c in conversations])

@assistant_bp.route('/delete/<int:conv_id>', methods=['POST'])
def delete_conversation(conv_id):
    """Delete a conversation thread"""
    conv = AssistantConversation.query.get_or_404(conv_id)
    db.session.delete(conv)
    db.session.commit()
    return jsonify({'status': 'deleted'})

@assistant_bp.route('/clear', methods=['POST'])
def clear_history():
    """Wipe all conversations"""
    AssistantConversation.query.delete()
    db.session.commit()
    return jsonify({'status': 'cleared'})
