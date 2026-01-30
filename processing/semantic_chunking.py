import pandas as pd
from database.db import get_connection
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())
try:
    from app.vector.chroma_store import add_documents
except ImportError:
    print("Warning: Could not import add_documents from app.vector.chroma_store")

# Paths
DB_PATH = "database/lab_results.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_patient_chunks(subject_id, gender, patient_df):
    """
    Creates multiple semantic chunks for a patient, grouping their labs.
    Prioritizes CRITICAL and ABNORMAL results.
    """
    # Sort: CRITICAL (0), ABNORMAL (1), NORMAL (2)
    status_order = {'CRITICAL': 0, 'ABNORMAL': 1, 'NORMAL': 2}
    patient_df = patient_df.copy()
    patient_df['sort_priority'] = patient_df['status'].map(lambda x: status_order.get(x, 3))
    patient_df = patient_df.sort_values(by=['sort_priority', 'processed_time'], ascending=[True, False])
    
    chunks = []
    chunk_size = 50  # Group 50 labs together for rich context
    
    for i in range(0, len(patient_df), chunk_size):
        batch = patient_df.iloc[i : i + chunk_size]
        
        # Build the descriptive text
        lines = [f"Clinical Report for Patient {subject_id} ({gender}):"]
        
        critical_count = len(batch[batch['status'] == 'CRITICAL'])
        abnormal_count = len(batch[batch['status'] == 'ABNORMAL'])
        
        lines.append(f"Summary of this section: {critical_count} CRITICAL, {abnormal_count} ABNORMAL results.")
        lines.append("-" * 30)
        
        for _, row in batch.iterrows():
            lines.append(f"- {row['test_name']}: {row['value']} {row['unit']} ({row['status']}) - Reason: {row['reason']}")
        
        text = "\n".join(lines)
        
        chunks.append({
            "text": text,
            "metadata": {
                "subject_id": str(subject_id),
                "type": "patient_clinical_summary",
                "critical_count": critical_count,
                "abnormal_count": abnormal_count,
                "chunk_index": i // chunk_size
            }
        })
        
    return chunks

def run_chunking():
    print("Starting Optimized Semantic Chunking...")
    
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return []

    conn = get_connection()
    
    try:
        print("Fetching data from lab_interpretations...")
        df = pd.read_sql_query("SELECT * FROM lab_interpretations", conn)
        
        all_chunks = []
        
        # Group by subject_id to create context-rich summaries
        print("Grouping labs by patient and generating semantic chunks...")
        for subject_id, group in df.groupby('subject_id'):
            gender = group.iloc[0]['gender']
            patient_chunks = create_patient_chunks(subject_id, gender, group)
            all_chunks.extend(patient_chunks)
            
        print(f"Created {len(all_chunks)} total semantic chunks (optimized from {len(df)}).")
        return all_chunks
        
    except Exception as e:
        print(f"Error during chunking: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        conn.close()

def populate_chroma(chunks):
    if not chunks:
        return
    print(f"Populating ChromaDB with {len(chunks)} chunks...")
    texts = [c['text'] for c in chunks]
    metadatas = [c['metadata'] for c in chunks]
    
    # Process in batches
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_metadatas = metadatas[i:i + batch_size]
        add_documents(batch_texts, batch_metadatas)
        print(f"  Added batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

if __name__ == "__main__":
    chunks = run_chunking()
    if chunks:
        populate_chroma(chunks)
        print("Finalized ChromaDB population.")
