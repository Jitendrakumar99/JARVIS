"""
Face Recognition Engine - Using DeepFace (Easy Install)
Handles face detection, embedding extraction, and matching
"""
import numpy as np
import os

# DeepFace is lazy-loaded inside methods to speed up application startup
DEEPFACE_AVAILABLE = True # Assume available since it's in requirements.txt
FACE_RECOGNITION_AVAILABLE = True  


class FaceEngine:
    """Face recognition engine using DeepFace"""
    
    def __init__(self):
        # Facenet is much lighter than VGG-Face (~90MB vs 500MB+)
        # This is critical for Render Free Tier (512MB limit)
        self.model_name = "Facenet"  
        self.distance_metric = "cosine"
        self.threshold = 0.4  # Lower = more strict
    
    def get_face_embedding(self, image_path):
        """
        Extract face embedding from an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            numpy array of face embedding or None if no face found
        """
        if not DEEPFACE_AVAILABLE:
            print("DeepFace not available")
            return None
        
        try:
            from deepface import DeepFace
            # Get embedding using DeepFace
            embedding_objs = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                enforce_detection=False
            )
            
            if embedding_objs and len(embedding_objs) > 0:
                embedding = np.array(embedding_objs[0]["embedding"])
                return embedding.astype(np.float32)
            else:
                print(f"No face found in {image_path}")
                return None
                
        except Exception as e:
            print(f"Error extracting face embedding: {e}")
            return None
    
    def compare_faces(self, known_embedding, unknown_embedding):
        """
        Compare two face embeddings using cosine similarity
        
        Args:
            known_embedding: Stored face embedding
            unknown_embedding: New face embedding to compare
            
        Returns:
            tuple of (is_match, distance)
        """
        if known_embedding is None or unknown_embedding is None:
            return False, 1.0
        
        try:
            # Calculate cosine distance
            dot_product = np.dot(known_embedding, unknown_embedding)
            norm1 = np.linalg.norm(known_embedding)
            norm2 = np.linalg.norm(unknown_embedding)
            
            if norm1 == 0 or norm2 == 0:
                return False, 1.0
            
            cosine_similarity = dot_product / (norm1 * norm2)
            distance = 1 - cosine_similarity
            
            is_match = distance <= self.threshold
            return is_match, distance
            
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return False, 1.0
    
    def find_matching_student(self, image_path, students):
        """
        Find the best matching student from a list
        
        Args:
            image_path: Path to the search image
            students: List of Student objects with face_embedding attribute
            
        Returns:
            tuple of (best_match_student, confidence) or None
        """
        if not DEEPFACE_AVAILABLE:
            print("DeepFace not available")
            return None
        
        # Get embedding from search image
        search_embedding = self.get_face_embedding(image_path)
        
        if search_embedding is None:
            print("No face found in search image")
            return None
        
        best_match = None
        best_distance = float('inf')
        
        for student in students:
            if student.face_embedding is None:
                continue
            
            try:
                is_match, distance = self.compare_faces(
                    student.face_embedding, 
                    search_embedding
                )
                
                if distance < best_distance and distance <= self.threshold:
                    best_distance = distance
                    best_match = student
                    
            except Exception as e:
                print(f"Error comparing with student {student.id}: {e}")
                continue
        
        if best_match:
            # Convert distance to confidence (0-100%)
            confidence = round((1 - best_distance) * 100, 2)
            return best_match, confidence
        
        return None
    
    def verify_faces(self, img1_path, img2_path):
        """
        Verify if two images contain the same person
        
        Args:
            img1_path: Path to first image
            img2_path: Path to second image
            
        Returns:
            dict with verified (bool) and distance
        """
        if not DEEPFACE_AVAILABLE:
            return {"verified": False, "distance": 1.0}
        
        try:
            from deepface import DeepFace
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=self.model_name,
                enforce_detection=False
            )
            return result
        except Exception as e:
            print(f"Error verifying faces: {e}")
            return {"verified": False, "distance": 1.0}
    
    def detect_faces(self, image_path):
        """
        Detect all faces in an image
        
        Returns:
            List of face regions
        """
        if not DEEPFACE_AVAILABLE:
            return []
        
        try:
            from deepface import DeepFace
            faces = DeepFace.extract_faces(
                img_path=image_path,
                enforce_detection=False
            )
            return faces
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def get_face_count(self, image_path):
        """Get the number of faces in an image"""
        return len(self.detect_faces(image_path))
