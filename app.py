from flask import Flask, render_template, request, redirect
import face_recognition
import numpy as np
import faiss
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title="KEW | Home")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        file = request.files['face_image']
        path = os.path.join("images", "temp.jpg")
        file.save(path)

        query_img = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(query_img)
        if not encoding:
            return "❌ No face detected."

        index = faiss.read_index("data/index.faiss")
        conn = sqlite3.connect("data/metadata.db")
        cur = conn.cursor()
        D, I = index.search(np.array([encoding[0]], dtype=np.float32), k=1)
        rider_id = I[0][0]
        cur.execute("SELECT * FROM riders WHERE id=?", (rider_id+1,))
        rider = cur.fetchone()
        conn.close()

        return render_template("result.html", title="Result", rider=rider)
    return render_template('login.html', title="Login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        file = request.files['face_image']
        name = request.form['name']
        phone = request.form['phone']
        save_path = os.path.join("images", file.filename)
        file.save(save_path)

        image = face_recognition.load_image_file(save_path)
        encoding = face_recognition.face_encodings(image)
        if not encoding:
            return "❌ No face found."

        index = faiss.read_index("data/index.faiss")
        conn = sqlite3.connect("data/metadata.db")
        cur = conn.cursor()
        index.add(np.array([encoding[0]], dtype=np.float32))
        cur.execute("INSERT INTO riders (filename, name, phone) VALUES (?, ?, ?)", (file.filename, name, phone))
        faiss.write_index(index, "data/index.faiss")
        conn.commit()
        conn.close()

        return redirect("/")
    return render_template('register.html', title="Register")
