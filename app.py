from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

mongo = PyMongo(app)

# Routes

@app.route('/')
def index():
    return render_template('directories/index.html')

@app.route('/submit', methods=['POST'])
def submit():
    patient_data = {
        'patient_name': request.form['patient_name'],
        'clinic': request.form['clinic'],
        'reason': request.form['reason'],
        'status': 'Pending'
    }
    mongo.db.transfers.insert_one(patient_data)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'hospital' and request.form['password'] == 'pass':
            session['hospital'] = True
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('hospital'):
        return redirect(url_for('login'))
    transfers = mongo.db.transfers.find()
    return render_template('dashboard.html', transfers=transfers)

@app.route('/update/<id>/<status>')
def update_status(id, status):
    if not session.get('hospital'):
        return redirect(url_for('login'))
    mongo.db.transfers.update_one({'_id': ObjectId(id)}, {'$set': {'status': status}})
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
