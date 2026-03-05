"""
Groq Client for RAG Pipeline
Handles communication with Groq API
"""
import os

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: groq not installed. AI features will be limited.")


class GroqClient:
    """Client for Groq API"""
    
    def __init__(self, api_key=None, model="llama-3.3-70b-versatile"):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (uses env var if not provided)
            model: Groq model name
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY', '')
        self.model_name = model
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the Groq client"""
        if not GROQ_AVAILABLE:
            print("Groq library not available")
            return
        
        if not self.api_key:
            print("Warning: GROQ_API_KEY not set. AI features will use fallback responses.")
            return
        
        try:
            self.client = Groq(api_key=self.api_key)
            print(f"Groq client initialized with model: {self.model_name}")
        except Exception as e:
            print(f"Error initializing Groq: {e}")
            self.client = None
    
    def generate_response(self, query, context):
        """
        Generate response using RAG approach
        
        Args:
            query: User's question
            context: Retrieved student context
            
        Returns:
            Generated response string
        """
        if self.client is None:
            return self._fallback_response(query, context)
        
        system_prompt = f"""You are a helpful college assistant AI. Answer the user's question based ONLY on the student information provided below. 
If the information needed to answer is not in the context, say so politely.

STUDENT DATABASE CONTEXT:
{context}"""

        user_prompt = f"USER QUESTION: {query}\n\nProvide a helpful, accurate, and concise response. If listing students, format them clearly. If asked about skills or qualifications, mention specific students who match."

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=self.model_name,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._fallback_response(query, context)
    
    def generate_raw(self, prompt):
        """
        Generate response for any prompt
        
        Args:
            prompt: Full prompt to send
            
        Returns:
            Generated response string
        """
        if self.client is None:
            return "AI features require a valid Groq API key. Please configure GROQ_API_KEY in your .env file."
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt},
                ],
                model=self.model_name,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _fallback_response(self, query, context):
        """
        Provide a fallback response when API is unavailable
        
        Args:
            query: User's question
            context: Retrieved context
            
        Returns:
            Fallback response string
        """
        if "No relevant students" in context:
            return "I couldn't find any students matching your query. Please add some students through the Admin Panel first."
        
        # Extract basic info from context
        student_count = context.count('Student ')
        
        response = f"""Based on the student database, I found {student_count} potentially relevant student(s).

Here's a summary of the available information:
{context[:500]}{'...' if len(context) > 500 else ''}

Note: For more detailed AI-powered responses, please configure your Groq API key in the .env file."""
        
        return response

    def summarize_student(self, student_data):
        """
        Generate an AI summary for a student
        
        Args:
            student_data: Student text representation
            
        Returns:
            AI-generated summary
        """
        prompt = f"""Create a brief, professional summary (2-3 sentences) for this student's profile:

{student_data}

Focus on their key strengths, notable achievements, and career potential."""

        return self.generate_raw(prompt)
