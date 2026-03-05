
import os
import sys

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from models import db, Student
from rag.retriever import StudentRetriever

def verify():
    app = create_app('development')
    with app.app_context():
        retriever = StudentRetriever()
        
        # Get all students to know what we have
        all_students = Student.query.all()
        if not all_students:
            print("No students found in database. Please run add_sample_data.py first.")
            return

        print(f"Total students in DB: {len(all_students)}")
        
        # Test 1: Search for a specific student name
        test_student = all_students[0]
        print(f"\nTesting search for: {test_student.name}")
        results = retriever.retrieve(test_student.name, top_k=5, threshold=0.6)
        print(f"Results count: {len(results)}")
        for i, s in enumerate(results):
            print(f"  {i+1}: {s.name} (ID: {s.id})")
        
        # Test 2: Search for something completely irrelevant
        print("\nTesting irrelevant search: 'purple elephants playing tennis'")
        results = retriever.retrieve("purple elephants playing tennis", top_k=5, threshold=0.6)
        print(f"Results count: {len(results)}")
        if len(results) == 0:
            print("  SUCCESS: Irrelevant query returned no results.")
        else:
            print(f"  FAILURE: Irrelevant query returned {len(results)} results.")
            for i, s in enumerate(results):
                print(f"    {i+1}: {s.name}")

        # Test 3: Search for a roll number (Fallback logic test)
        # Note: retriever.retrieve with threshold 0.6 might return empty for exact roll number
        # unless it triggers fallback in ai_chat.py logic.
        # But let's check retrieve directly.
        roll = test_student.roll_no
        print(f"\nTesting search for roll number: {roll}")
        results = retriever.retrieve(roll, top_k=2, threshold=0.6)
        print(f"Initial AI retrieval count: {len(results)}")
        
        # Simulate ai_chat.py fallback logic
        if not results:
            print("AI search returned nothing (as expected for precise roll number). Triggering fallback...")
            keywords = roll.lower().split()
            query = Student.query
            for keyword in keywords:
                query = query.filter(
                    (Student.name.ilike(f'%{keyword}%')) |
                    (Student.roll_no.ilike(f'%{keyword}%')) |
                    (Student.department.ilike(f'%{keyword}%')) |
                    (Student._skills.ilike(f'%{keyword}%'))
                )
            fallback_results = query.limit(5).all()
            print(f"Fallback results count: {len(fallback_results)}")
            for i, s in enumerate(fallback_results):
                print(f"  {i+1}: {s.name} ({s.roll_no})")
            if any(s.roll_no == roll for s in fallback_results):
                print("  SUCCESS: Roll number found via fallback search.")
            else:
                print("  FAILURE: Roll number not found in fallback search.")

if __name__ == "__main__":
    verify()
