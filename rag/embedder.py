"""
Text Embedder for RAG Pipeline
Uses sentence-transformers for embedding generation
"""
import numpy as np

# Sentence transformers are lazy-loaded to speed up application startup
SENTENCE_TRANSFORMERS_AVAILABLE = True


class TextEmbedder:
    """Text embedding generator using sentence-transformers"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the embedder with a pre-trained model
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("Sentence transformers not available")
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            print(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def embed_text(self, text):
        """
        Generate embedding for a text string
        
        Args:
            text: Text to embed
            
        Returns:
            numpy array of embeddings
        """
        if self.model is None:
            # Return random embedding as fallback
            return np.random.rand(384).astype(np.float32)
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return np.random.rand(384).astype(np.float32)
    
    def embed_texts(self, texts):
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            numpy array of embeddings (n_texts x embedding_dim)
        """
        if self.model is None:
            return np.random.rand(len(texts), 384).astype(np.float32)
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.astype(np.float32)
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return np.random.rand(len(texts), 384).astype(np.float32)
    
    def similarity(self, embedding1, embedding2):
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score (0-1)
        """
        try:
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
