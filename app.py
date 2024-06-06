# from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory
# from flask_bootstrap import Bootstrap
# import mysql.connector
# import os
# from werkzeug.utils import secure_filename
# import cv2
# import base64
# import numpy as np
# import requests
# import random
# import matplotlib.pyplot as plt

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'
# Bootstrap(app)

# UPLOAD_FOLDER = 'static/uploads'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # API configuration
# API_URL = "https://outline.roboflow.com/aurora-seg/1"
# API_KEY = "B045orWaaQ6IYhjERfWi"

# # Database configuration
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="aurora"
# )
# cursor = db.cursor(dictionary=True)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def encode_image_to_base64(image_path):
#     with open(image_path, "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
#     return encoded_string

# def send_image_to_roboflow(api_url, api_key, image_base64):
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     response = requests.post(f"{api_url}?api_key={api_key}", data=image_base64, headers=headers)
#     return response.json()

# def get_unique_color(label):
#     random.seed(hash(label) % 2**32)
#     return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# def draw_segmentations(image, segmentations):
#     overlay = image.copy()
#     for segmentation in segmentations:
#         points = segmentation['points']
#         label = segmentation.get('class', 'unknown')
        
#         # Handle the case where points might be a list of dicts
#         if isinstance(points, list) and isinstance(points[0], dict):
#             points = [(point['x'], point['y']) for point in points]
        
#         points = np.array(points, dtype=np.int32)
#         color = get_unique_color(label)
        
#         cv2.fillPoly(overlay, [points], color)
        
#         # Calculate the centroid for placing the label
#         M = cv2.moments(points)
#         if M["m00"] != 0:
#             cX = int(M["m10"] / M["m00"])
#             cY = int(M["m01"] / M["m00"])
#         else:
#             cX, cY = points[0][0], points[0][1]
        
#         cv2.putText(image, label, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)
    
#     # Blend the overlay with the original image
#     alpha = 0.4  # Transparency factor
#     image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
#     return image

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
#         user = cursor.fetchone()
#         if user:
#             session['user_id'] = user['id']
#             session['username'] = user['username']
#             session['user_type'] = user['user_type']
#             if user['user_type'] == 'admin':
#                 return redirect(url_for('admin_dashboard'))
#             else:
#                 return redirect(url_for('user_dashboard'))
#     return render_template('login.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user_type = 'user'  # Default user type
#         cursor.execute('INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)', (username, password, user_type))
#         db.commit()
#         return redirect(url_for('login'))
#     return render_template('register.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('home'))

# @app.route('/admin/dashboard')
# def admin_dashboard():
#     if 'user_type' in session and session['user_type'] == 'admin':
#         cursor.execute('SELECT * FROM laws')
#         laws = cursor.fetchall()
#         cursor.execute('SELECT * FROM maps')
#         maps = cursor.fetchall()
#         return render_template('admin_dashboard.html', laws=laws, maps=maps)
#     return redirect(url_for('login'))

# @app.route('/admin/add_law', methods=['GET', 'POST'])
# def add_law():
#     if 'user_type' in session and session['user_type'] == 'admin':
#         if request.method == 'POST':
#             title = request.form['title']
#             description = request.form['description']
#             cursor.execute('INSERT INTO laws (title, description) VALUES (%s, %s)', (title, description))
#             db.commit()
#             return redirect(url_for('admin_dashboard'))
#         return render_template('add_law.html')
#     return redirect(url_for('login'))

# @app.route('/admin/upload_map', methods=['GET', 'POST'])
# def upload_map():
#     if 'user_type' in session and session['user_type'] == 'admin':
#         if request.method == 'POST':
#             map_name = request.form['map_name']
#             if 'map_image' not in request.files:
#                 flash('No file part')
#                 return redirect(request.url)
#             file = request.files['map_image']
#             if file.filename == '':
#                 flash('No selected file')
#                 return redirect(request.url)
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#                 file.save(file_path)

#                 # Detect objects
#                 image_base64 = encode_image_to_base64(file_path)
#                 result = send_image_to_roboflow(API_URL, API_KEY, image_base64)

#                 # Store map info in the database
#                 cursor.execute('INSERT INTO maps (name, filename) VALUES (%s, %s)', (map_name, filename))
#                 db.commit()
#                 map_id = cursor.lastrowid  # Get the last inserted id

#                 if 'predictions' in result:
#                     for obj in result['predictions']:
#                         if 'points' in obj:
#                             points = obj['points']
#                             mask = base64.b64encode(str(points).encode()).decode()

#                             x1 = min(point['x'] for point in points)
#                             y1 = min(point['y'] for point in points)
#                             x2 = max(point['x'] for point in points)
#                             y2 = max(point['y'] for point in points)
#                             area = cv2.contourArea(np.array([(point['x'], point['y']) for point in points], dtype=np.int32))

#                             cursor.execute(
#                                 'INSERT INTO detected_objects (map_id, class_name, mask, x1, y1, x2, y2, area) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
#                                 (map_id, obj['class'], mask, x1, y1, x2, y2, area)
#                             )
#                             db.commit()

#                 return redirect(url_for('admin_dashboard'))
#         return render_template('upload_map.html')
#     return redirect(url_for('login'))

# @app.route('/admin/mark_area/<int:map_id>', methods=['GET', 'POST'])
# def mark_area(map_id):
#     if 'user_type' in session and session['user_type'] == 'admin':
#         if request.method == 'POST':
#             area_name = request.form['area_name']
#             x1 = request.form['x1']
#             y1 = request.form['y1']
#             x2 = request.form['x2']
#             y2 = request.form['y2']
#             feature_type = request.form['feature_type']
#             feature_value = request.form['feature_value']

#             cursor.execute('INSERT INTO areas (name, map_id, x1, y1, x2, y2) VALUES (%s, %s, %s, %s, %s, %s)', (area_name, map_id, x1, y1, x2, y2))
#             db.commit()

#             area_id = cursor.lastrowid
#             cursor.execute('INSERT INTO area_features (area_id, feature_type, feature_value) VALUES (%s, %s, %s)', (area_id, feature_type, feature_value))
#             db.commit()

#             # Stay on the same page to mark another area
#             return redirect(url_for('mark_area', map_id=map_id))
        
#         cursor.execute('SELECT filename FROM maps WHERE id=%s', (map_id,))
#         map_info = cursor.fetchone()
#         return render_template('mark_area.html', map_info=map_info)
#     return redirect(url_for('login'))

# @app.route('/admin/view_map/<int:map_id>')
# def admin_view_map(map_id):
#     if 'user_type' in session and session['user_type'] == 'admin':
#         cursor.execute('SELECT * FROM maps WHERE id=%s', (map_id,))
#         map_info = cursor.fetchone()
#         cursor.execute('SELECT * FROM areas WHERE map_id=%s', (map_id,))
#         areas = cursor.fetchall()
#         for area in areas:
#             cursor.execute('SELECT * FROM area_features WHERE area_id=%s', (area['id'],))
#             area['features'] = cursor.fetchall()
#         return render_template('admin_view_map.html', map_info=map_info, areas=areas)
#     return redirect(url_for('login'))

# @app.route('/admin/delete_map/<int:map_id>', methods=['POST'])
# def delete_map(map_id):
#     if 'user_type' in session and session['user_type'] == 'admin':
#         cursor.execute('SELECT filename FROM maps WHERE id=%s', (map_id,))
#         map_info = cursor.fetchone()
#         if map_info:
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], map_info['filename'])
#             # Check if the file exists before attempting to delete it
#             if os.path.exists(file_path):
#                 try:
#                     os.remove(file_path)
#                 except Exception as e:
#                     print(f"Error removing file: {e}")
            
#             # Delete the detected objects, areas, and associated features before deleting the map
#             cursor.execute('DELETE FROM detected_objects WHERE map_id=%s', (map_id,))
#             cursor.execute('DELETE FROM area_features WHERE area_id IN (SELECT id FROM areas WHERE map_id=%s)', (map_id,))
#             cursor.execute('DELETE FROM areas WHERE map_id=%s', (map_id,))
#             cursor.execute('DELETE FROM maps WHERE id=%s', (map_id,))
#             db.commit()
        
#         return redirect(url_for('admin_dashboard'))
#     return redirect(url_for('login'))

# @app.route('/admin/view_detected_objects/<int:map_id>')
# def view_detected_objects(map_id):
#     if 'user_type' in session and session['user_type'] == 'admin':
#         cursor.execute('SELECT * FROM detected_objects WHERE map_id=%s', (map_id,))
#         detected_objects = cursor.fetchall()
#         cursor.execute('SELECT * FROM maps WHERE id=%s', (map_id,))
#         map_info = cursor.fetchone()
        
#         # Load the map image
#         map_image_path = os.path.join(app.config['UPLOAD_FOLDER'], map_info['filename'])
#         map_image = cv2.imread(map_image_path)
        
#         # Draw the segmentation masks on the map image
#         segmentations = []
#         for obj in detected_objects:
#             mask = base64.b64decode(obj['mask'])
#             mask = eval(mask.decode())  # Convert the string back to list of points
#             segmentations.append({
#                 'points': mask,
#                 'class': obj['class_name']
#             })
        
#         segmented_image = draw_segmentations(map_image, segmentations)
#         segmented_image_filename = f"segmented_{map_info['filename']}"
#         segmented_image_path = os.path.join(app.config['UPLOAD_FOLDER'], segmented_image_filename)
#         cv2.imwrite(segmented_image_path, segmented_image)
        
#         return render_template('view_detected_objects.html', detected_objects=detected_objects, map_info=map_info, segmented_image=segmented_image_filename)
#     return redirect(url_for('login'))

# @app.route('/user/dashboard')
# def user_dashboard():
#     if 'user_type' in session and session['user_type'] == 'user':
#         cursor.execute('SELECT * FROM maps')
#         maps = cursor.fetchall()
#         return render_template('user_dashboard.html', maps=maps)
#     return redirect(url_for('login'))

# @app.route('/user/view_map/<int:map_id>')
# def user_view_map(map_id):
#     if 'user_type' in session and session['user_type'] == 'user':
#         cursor.execute('SELECT * FROM maps WHERE id=%s', (map_id,))
#         map_info = cursor.fetchone()
#         cursor.execute('SELECT * FROM areas WHERE map_id=%s', (map_id,))
#         areas = cursor.fetchall()
#         for area in areas:
#             cursor.execute('SELECT * FROM area_features WHERE area_id=%s', (area['id'],))
#             area['features'] = cursor.fetchall()
#         cursor.execute('SELECT * FROM detected_objects WHERE map_id=%s', (map_id,))
#         detected_objects = cursor.fetchall()
        
#         map_image_path = os.path.join(app.config['UPLOAD_FOLDER'], map_info['filename'])
#         map_image = cv2.imread(map_image_path)

#         segmentations = []
#         for obj in detected_objects:
#             mask = base64.b64decode(obj['mask'])
#             mask = eval(mask.decode())
#             segmentations.append({
#                 'points': mask,
#                 'class': obj['class_name']
#             })

#         segmented_image = draw_segmentations(map_image, segmentations)
#         segmented_image_filename = f"segmented_{map_info['filename']}"
#         segmented_image_path = os.path.join(app.config['UPLOAD_FOLDER'], segmented_image_filename)
#         cv2.imwrite(segmented_image_path, segmented_image)

#         return render_template('view_map.html', map_info=map_info, areas=areas, segmented_image=segmented_image_filename)
#     return redirect(url_for('login'))

# @app.route('/user/select_building_type/<int:map_id>/<int:area_id>', methods=['POST'])
# def select_building_type(map_id, area_id):
#     if 'user_type' in session and session['user_type'] == 'user':
#         x1 = request.form['x1']
#         y1 = request.form['y1']
#         x2 = request.form['x2']
#         y2 = request.form['y2']
#         return redirect(url_for('building_form', map_id=map_id, area_id=area_id, building_type='', x1=x1, y1=y1, x2=x2, y2=y2))
#     return redirect(url_for('login'))

# @app.route('/user/building_form/<int:map_id>/<int:area_id>', methods=['GET', 'POST'])
# def building_form(map_id, area_id):
#     if 'user_type' in session and session['user_type'] == 'user':
#         if request.method == 'POST':
#             user_id = session['user_id']
#             building_type = request.form['building_type']
#             subcategory = request.form['subcategory']
#             x1 = request.args['x1']
#             y1 = request.args['y1']
#             x2 = request.args['x2']
#             y2 = request.args['y2']
            
#             prompt_details = []
#             for key, value in request.form.items():
#                 if key not in ['building_type', 'subcategory']:
#                     prompt_details.append(f"{key}: {value}")
#             prompt = ", ".join(prompt_details)

#             cursor.execute('INSERT INTO prompts (user_id, map_id, area_id, building_type, subcategory, prompt, x1, y1, x2, y2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
#                            (user_id, map_id, area_id, building_type, subcategory, prompt, x1, y1, x2, y2))
#             db.commit()

#             return redirect(url_for('user_dashboard'))
        
#         building_type = request.args.get('building_type', '')
#         return render_template('building_form.html', map_id=map_id, area_id=area_id, building_type=building_type)
#     return redirect(url_for('login'))

# @app.route('/predict_areas', methods=['POST'])
# def predict_areas():
#     if 'user_type' in session and session['user_type'] == 'user':
#         requirement_type = request.form['requirement_type']
#         requirement_value = request.form['requirement_value']
#         cursor.execute('SELECT * FROM areas')
#         areas = cursor.fetchall()
#         predictions = []
#         for area in areas:
#             cursor.execute('SELECT * FROM area_features WHERE area_id=%s', (area['id'],))
#             features = cursor.fetchall()
#             match = True
#             for feature in features:
#                 if feature['feature_type'] == requirement_type and feature['feature_value'] == requirement_value:
#                     match = True
#                 else:
#                     match = False
#                     break
#             if match:
#                 predictions.append(area)
#         return render_template('predict_areas.html', predictions=predictions)
#     return redirect(url_for('login'))

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# @app.route('/view_prompts')
# def view_prompts():
#     if 'user_type' in session and session['user_type'] == 'user':
#         cursor.execute('SELECT * FROM prompts WHERE user_id = %s', (session['user_id'],))
#         prompts = cursor.fetchall()
#         return render_template('view_prompts.html', prompts=prompts)
#     return redirect(url_for('login'))


# if __name__ == '__main__':
#     app.run(debug=True, port=5001)



from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory,send_file
from flask_bootstrap import Bootstrap
import mysql.connector
import os
from werkzeug.utils import secure_filename
import cv2
import base64
import random
import numpy as np
import requests
import io
import time
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key'
Bootstrap(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# API for object detection
API_URL = "https://outline.roboflow.com/aurora-seg/1"
API_KEY = "B045orWaaQ6IYhjERfWi"

# API for generating images
GEN_API_URL = "https://api-inference.huggingface.co/models/stablediffusionapi/architecture-tuned-model"
HEADERS = {"Authorization": "Bearer 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"}

# Database configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="aurora"
)
cursor = db.cursor(dictionary=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def query(payload):
    response = requests.post(f"{API_URL}?api_key={API_KEY}", json=payload)
    try:
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response content: {response.content}")
    return response

def generate_image(prompt):
    payload = {"inputs": prompt}
    while True:
        response = query_image(payload)
        
        # Check if the response indicates the model is still loading
        if response.status_code == 503 and "loading" in response.json().get("error", "").lower():
            estimated_time = response.json().get("estimated_time", 60)
            print(f"Model is loading. Estimated time: {estimated_time} seconds.")
            time.sleep(min(estimated_time, 60))  # Wait before retrying
        else:
            return response

def query_image(payload):
    response = requests.post(GEN_API_URL, headers=HEADERS, json=payload)
    try:
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response content: {response.content}")
    return response

def get_unique_color(label):
    random.seed(hash(label) % 2**32)
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def draw_segmentations(image, segmentations):
    overlay = image.copy()
    for segmentation in segmentations:
        points = segmentation['points']
        label = segmentation.get('class', 'unknown')
        
        # Handle the case where points might be a list of dicts
        if isinstance(points, list) and isinstance(points[0], dict):
            points = [(point['x'], point['y']) for point in points]
        
        points = np.array(points, dtype=np.int32)
        color = get_unique_color(label)
        
        cv2.fillPoly(overlay, [points], color)
        
        # Calculate the centroid for placing the label
        M = cv2.moments(points)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = points[0][0], points[0][1]
        
        cv2.putText(image, label, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)
    
    # Blend the overlay with the original image
    alpha = 0.4  # Transparency factor
    image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
    return image

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            if user['user_type'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = 'user'  # Default user type
        cursor.execute('INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)', (username, password, user_type))
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_type' in session and session['user_type'] == 'admin':
        cursor.execute('SELECT * FROM laws')
        laws = cursor.fetchall()
        cursor.execute('SELECT * FROM maps')
        maps = cursor.fetchall()
        return render_template('admin_dashboard.html', laws=laws, maps=maps)
    return redirect(url_for('login'))

@app.route('/admin/add_law', methods=['GET', 'POST'])
def add_law():
    if 'user_type' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            cursor.execute('INSERT INTO laws (title, description) VALUES (%s, %s)', (title, description))
            db.commit()
            return redirect(url_for('admin_dashboard'))
        return render_template('add_law.html')
    return redirect(url_for('login'))

@app.route('/admin/upload_map', methods=['GET', 'POST'])
def upload_map():
    if 'user_type' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            map_name = request.form['map_name']
            if 'map_image' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['map_image']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Detect objects
                image_base64 = encode_image_to_base64(file_path)
                result = query({"base64": image_base64})

                # Store map info in the database
                cursor.execute('INSERT INTO maps (name, filename) VALUES (%s, %s)', (map_name, filename))
                db.commit()
                map_id = cursor.lastrowid  # Get the last inserted id

                if 'predictions' in result:
                    for obj in result['predictions']:
                        if 'points' in obj:
                            points = obj['points']
                            mask = base64.b64encode(str(points).encode()).decode()

                            x1 = min(point['x'] for point in points)
                            y1 = min(point['y'] for point in points)
                            x2 = max(point['x'] for point in points)
                            y2 = max(point['y'] for point in points)
                            area = cv2.contourArea(np.array([(point['x'], point['y']) for point in points], dtype=np.int32))

                            cursor.execute(
                                'INSERT INTO detected_objects (map_id, class_name, mask, x1, y1, x2, y2, area) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                                (map_id, obj['class'], mask, x1, y1, x2, y2, area)
                            )
                            db.commit()

                return redirect(url_for('admin_dashboard'))
        return render_template('upload_map.html')
    return redirect(url_for('login'))

@app.route('/admin/mark_area/<int:map_id>', methods=['GET', 'POST'])
def mark_area(map_id):
    if 'user_type' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            area_name = request.form['area_name']
            x1 = request.form['x1']
            y1 = request.form['y1']
            x2 = request.form['x2']
            y2 = request.form['y2']
            feature_type = request.form['feature_type']
            feature_value = request.form['feature_value']

            cursor.execute('INSERT INTO areas (name, map_id, x1, y1, x2, y2) VALUES (%s, %s, %s, %s, %s, %s)', (area_name, map_id, x1, y1, x2, y2))
            db.commit()

            area_id = cursor.lastrowid
            cursor.execute('INSERT INTO area_features (area_id, feature_type, feature_value) VALUES (%s, %s, %s)', (area_id, feature_type, feature_value))
            db.commit()

            # Stay on the same page to mark another area
            return redirect(url_for('mark_area', map_id=map_id))
        
        cursor.execute('SELECT filename FROM maps WHERE id=%s', (map_id,))
        map_info = cursor.fetchone()
        return render_template('mark_area.html', map_info=map_info)
    return redirect(url_for('login'))

@app.route('/admin/view_map/<int:map_id>')
def admin_view_map(map_id):
    if 'user_type' in session and session['user_type'] == 'admin':
        cursor.execute('SELECT * FROM maps WHERE id=%s', (map_id,))
        map_info = cursor.fetchone()
        cursor.execute('SELECT * FROM areas WHERE map_id=%s', (map_id,))
        areas = cursor.fetchall()
        for area in areas:
            cursor.execute('SELECT * FROM area_features WHERE area_id=%s', (area['id'],))
            area['features'] = cursor.fetchall()
        return render_template('admin_view_map.html', map_info=map_info, areas=areas)
    return redirect(url_for('login'))

@app.route('/admin/delete_map/<int:map_id>', methods=['POST'])
def delete_map(map_id):
    if 'user_type' in session and session['user_type'] == 'admin':
        cursor.execute('SELECT filename FROM maps WHERE id=%s', (map_id,))
        map_info = cursor.fetchone()
        if map_info:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], map_info['filename'])
            # Check if the file exists before attempting to delete it
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing file: {e}")
            
            # Delete the detected objects, areas, and associated features before deleting the map
            cursor.execute('DELETE FROM detected_objects WHERE map_id=%s', (map_id,))
            cursor.execute('DELETE FROM area_features WHERE area_id IN (SELECT id FROM areas WHERE map_id=%s)', (map_id,))
            cursor.execute('DELETE FROM areas WHERE map_id=%s', (map_id,))
            cursor.execute('DELETE FROM maps WHERE id=%s', (map_id,))
            db.commit()
        
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route('/admin/view_detected_objects/<int:map_id>')
def view_detected_objects(map_id):
    if 'user_type' in session and session['user_type'] == 'admin':
        cursor.execute('SELECT * FROM detected_objects WHERE map_id=%s', (map_id,))
        detected_objects = cursor.fetchall()
        cursor.execute('SELECT * FROM maps WHERE id=%s', (map_id,))
        map_info = cursor.fetchone()
        
        # Load the map image
        map_image_path = os.path.join(app.config['UPLOAD_FOLDER'], map_info['filename'])
        map_image = cv2.imread(map_image_path)
        
        # Draw the segmentation masks on the map image
        segmentations = []
        for obj in detected_objects:
            mask = base64.b64decode(obj['mask'])
            mask = eval(mask.decode())  # Convert the string back to list of points
            segmentations.append({
                'points': mask,
                'class': obj['class_name']
            })
        
        segmented_image = draw_segmentations(map_image, segmentations)
        segmented_image_filename = f"segmented_{map_info['filename']}"
        segmented_image_path = os.path.join(app.config['UPLOAD_FOLDER'], segmented_image_filename)
        cv2.imwrite(segmented_image_path, segmented_image)
        
        return render_template('view_detected_objects.html', detected_objects=detected_objects, map_info=map_info, segmented_image=segmented_image_filename)
    return redirect(url_for('login'))

@app.route('/user/dashboard')
def user_dashboard():
    if 'user_type' in session and session['user_type'] == 'user':
        cursor.execute('SELECT * FROM maps')
        maps = cursor.fetchall()
        return render_template('user_dashboard.html', maps=maps)
    return redirect(url_for('login'))

@app.route('/user/view_map/<int:map_id>')
def user_view_map(map_id):
    if 'user_type' in session and session['user_type'] == 'user':
        cursor.execute('SELECT * FROM maps WHERE id=%s', (map_id,))
        map_info = cursor.fetchone()
        cursor.execute('SELECT * FROM areas WHERE map_id=%s', (map_id,))
        areas = cursor.fetchall()
        for area in areas:
            cursor.execute('SELECT * FROM area_features WHERE area_id=%s', (area['id'],))
            area['features'] = cursor.fetchall()
        cursor.execute('SELECT * FROM detected_objects WHERE map_id=%s', (map_id,))
        detected_objects = cursor.fetchall()
        
        map_image_path = os.path.join(app.config['UPLOAD_FOLDER'], map_info['filename'])
        map_image = cv2.imread(map_image_path)

        segmentations = []
        for obj in detected_objects:
            mask = base64.b64decode(obj['mask'])
            mask = eval(mask.decode())
            segmentations.append({
                'points': mask,
                'class': obj['class_name']
            })

        segmented_image = draw_segmentations(map_image, segmentations)
        segmented_image_filename = f"segmented_{map_info['filename']}"
        segmented_image_path = os.path.join(app.config['UPLOAD_FOLDER'], segmented_image_filename)
        cv2.imwrite(segmented_image_path, segmented_image)

        return render_template('view_map.html', map_info=map_info, areas=areas, segmented_image=segmented_image_filename)
    return redirect(url_for('login'))

@app.route('/user/select_building_type/<int:map_id>/<int:area_id>', methods=['POST'])
def select_building_type(map_id, area_id):
    if 'user_type' in session and session['user_type'] == 'user':
        x1 = request.form['x1']
        y1 = request.form['y1']
        x2 = request.form['x2']
        y2 = request.form['y2']
        return redirect(url_for('building_form', map_id=map_id, area_id=area_id, building_type='', x1=x1, y1=y1, x2=x2, y2=y2))
    return redirect(url_for('login'))

@app.route('/user/building_form/<int:map_id>/<int:area_id>', methods=['GET', 'POST'])
def building_form(map_id, area_id):
    if 'user_type' in session and session['user_type'] == 'user':
        if request.method == 'POST':
            user_id = session['user_id']
            building_type = request.form['building_type']
            subcategory = request.form['subcategory']
            x1 = request.args['x1']
            y1 = request.args['y1']
            x2 = request.args['x2']
            y2 = request.args['y2']
            
            prompt_details = []
            for key, value in request.form.items():
                if key not in ['building_type', 'subcategory']:
                    prompt_details.append(f"{key}: {value}")
            prompt = ", ".join(prompt_details)

            cursor.execute('INSERT INTO prompts (user_id, map_id, area_id, building_type, subcategory, prompt, x1, y1, x2, y2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                           (user_id, map_id, area_id, building_type, subcategory, prompt, x1, y1, x2, y2))
            db.commit()

            return redirect(url_for('user_dashboard'))
        
        building_type = request.args.get('building_type', '')
        return render_template('building_form.html', map_id=map_id, area_id=area_id, building_type=building_type)
    return redirect(url_for('login'))

@app.route('/predict_areas', methods=['POST'])
def predict_areas():
    if 'user_type' in session and session['user_type'] == 'user':
        requirement_type = request.form['requirement_type']
        requirement_value = request.form['requirement_value']
        cursor.execute('SELECT * FROM areas')
        areas = cursor.fetchall()
        predictions = []
        for area in areas:
            cursor.execute('SELECT * FROM area_features WHERE area_id=%s', (area['id'],))
            features = cursor.fetchall()
            match = True
            for feature in features:
                if feature['feature_type'] == requirement_type and feature['feature_value'] == requirement_value:
                    match = True
                else:
                    match = False
                    break
            if match:
                predictions.append(area)
        return render_template('predict_areas.html', predictions=predictions)
    return redirect(url_for('login'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/view_prompts')
def view_prompts():
    if 'user_type' in session and session['user_type'] == 'user':
        cursor.execute('SELECT * FROM prompts WHERE user_id = %s', (session['user_id'],))
        prompts = cursor.fetchall()
        return render_template('view_prompts.html', prompts=prompts)
    return redirect(url_for('login'))

@app.route('/generate_image/<int:prompt_id>')
def generate_image_route(prompt_id):
    cursor.execute('SELECT prompt FROM prompts WHERE id=%s', (prompt_id,))
    prompt = cursor.fetchone()
    if prompt:
        response = generate_image(prompt['prompt'])
        
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            image_bytes = response.content
            image = Image.open(io.BytesIO(image_bytes))
            image_filename = f"generated_{prompt_id}.png"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)
            
            # Store the generated image filename in the database
            cursor.execute('UPDATE prompts SET generated_image=%s WHERE id=%s', (image_filename, prompt_id))
            db.commit()

            return redirect(url_for('view_generated_image', image_filename=image_filename))
        else:
            flash('Failed to generate image.')
            return redirect(url_for('view_prompts'))
    else:
        flash('Invalid prompt ID.')
        return redirect(url_for('view_prompts'))

@app.route('/view_generated_image/<string:image_filename>')
def view_generated_image(image_filename):
    return render_template('view_generated_prompt_image.html', image_filename=image_filename)

@app.route('/generated_image/<string:filename>')
def serve_generated_image(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
