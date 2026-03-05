"""
Student Retriever for RAG Pipeline
Retrieves relevant students based on query similarity
"""
import numpy as np
from models import Student
from .embedder import TextEmbedder

# Try to import FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: faiss-cpu not installed. Using fallback retrieval.")


class StudentRetriever:
    """Retrieves relevant students using semantic search"""
    
    def __init__(self):
        self.embedder = TextEmbedder()
        self.index = None
        self.student_ids = []
    
    def build_index(self, students):
        """
        Build or rebuild the FAISS index from students
        
        Args:
            students: List of Student objects
        """
        if not students:
            return
        
        self.student_ids = []
        embeddings = []
        
        for student in students:
            if student.text_embedding is not None:
                embeddings.append(student.text_embedding)
                self.student_ids.append(student.id)
            else:
                # Generate embedding on the fly
                emb = self.embedder.embed_text(student.to_text())
                embeddings.append(emb)
                self.student_ids.append(student.id)
        
        if not embeddings:
            return
        
        embeddings = np.array(embeddings).astype('float32')
        
        if FAISS_AVAILABLE:
            # Build FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
        else:
            # Store embeddings for fallback
            self.embeddings = embeddings
    
    def retrieve(self, query, top_k=5, threshold=0.5):
        """
        Retrieve top-k relevant students for a query
        
        Args:
            query: Search query string
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of Student objects
        """
        # Get all students and build index if needed
        students = Student.query.all()
        
        if not students:
            return []
        
        # Build index if not built
        if self.index is None or len(self.student_ids) != len(students):
            self.build_index(students)
        
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        if FAISS_AVAILABLE and self.index is not None:
            # Normalize query
            faiss.normalize_L2(query_embedding)
            
            # Search
            k = min(top_k, self.index.ntotal)
            if k == 0:
                return []
            
            distances, indices = self.index.search(query_embedding, k)
            
            # Get matching students that meet the threshold
            result_ids = []
            for i, dist in zip(indices[0], distances[0]):
                if i < len(self.student_ids) and dist >= threshold:
                    result_ids.append(self.student_ids[i])
            
            # Filter and maintain order
            ordered_results = []
            for rid in result_ids:
                for s in students:
                    if s.id == rid:
                        ordered_results.append(s)
                        break
            return ordered_results
        
        else:
            # Fallback: brute force similarity search
            return self._fallback_search(query_embedding[0], students, top_k, threshold)
    
    def _fallback_search(self, query_embedding, students, top_k, threshold=0.5):
        """Fallback search without FAISS"""
        similarities = []
        
        for student in students:
            if student.text_embedding is not None:
                emb = student.text_embedding
            else:
                emb = self.embedder.embed_text(student.to_text())
            
            sim = self.embedder.similarity(query_embedding, emb)
            if sim >= threshold:
                similarities.append((student, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k
        return [s[0] for s in similarities[:top_k]]
    
    def search_by_skills(self, skills_query, top_k=5):
        """
        Search students by skills
        
        Args:
            skills_query: Skills to search for (comma-separated)
            top_k: Number of results
            
        Returns:
            List of matching students
        """
        skills = [s.strip().lower() for s in skills_query.split(',')]
        
        students = Student.query.all()
        matches = []
        
        for student in students:
            student_skills = [s.lower() for s in student.skills]
            match_count = sum(1 for skill in skills if any(skill in ss for ss in student_skills))
            
            if match_count > 0:
                matches.append((student, match_count))
        
        # Sort by match count
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return [m[0] for m in matches[:top_k]]
