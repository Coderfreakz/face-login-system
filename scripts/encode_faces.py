import face_recognition
import os
import sqlite3
import faiss
import numpy as np

image_folder = "images_clean/"
db_path = "data/metadata.db"
index_path = "data/index.faiss"

os.makedirs("data", exist_ok=True)
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS riders (id INTEGER PRIMARY KEY, filename TEXT, name TEXT, phone TEXT)")

d = 128
index = faiss.IndexFlatL2(d)

for i, file in enumerate(sorted(os.listdir(image_folder))):
    path = os.path.join(image_folder, file)
    try:
        img = face_recognition.load_image_file(path)
        enc = face_recognition.face_encodings(img)
        if enc:
            index.add(np.array([enc[0]], dtype=np.float32))
            cur.execute("INSERT INTO riders (filename, name, phone) VALUES (?, ?, ?)", (
                file, f"Rider {i+1}", f"+91-98765{i:05d}"
            ))
            print(f"[{i+1}] Encoded: {file}")
    except Exception as e:
        print(f"[!] Error with {file}: {e}")

faiss.write_index(index, index_path)
conn.commit()
conn.close()
