from app import app
from models import db, Student
import sys

with app.app_context():
    students = Student.query.all()
    print(f"DEBUG_START")
    for s in students:
        # Re-generate text embedding
        from rag.embedder import TextEmbedder
        te = TextEmbedder()
        text_emb = te.embed_text(s.to_text())
        s.text_embedding = text_emb
        print(f"UPDATED|{s.id}|{s.name}")
    db.session.commit()
    print(f"DONE")
