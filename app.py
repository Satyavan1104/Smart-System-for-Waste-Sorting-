from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import torch
from datetime import datetime
import subprocess
process=None
from geopy.geocoders import Nominatim

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_BINDS'] = {}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and bcrypt
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# YOLOv5 model path
model_path = "C:/Users/Monica/Desktop/projects/w/waste.v3i.yolov5pytorch/yolov5/waste-sorte/exp/weights/best.pt"
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)

# Database model for User
class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Admin field to distinguish between admins and regular users

class WasteLocation(db.Model):
    __tablename__ = 'waste_location'
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    is_completed = db.Column(db.Boolean, default=False)  # New column

    user = db.relationship('User', backref=db.backref('locations', lazy=True))  # Define relationship

    def __init__(self, location_name,latitude, longitude,user_id):
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
        self.user_id = user_id

# Initialize the database
with app.app_context():
    db.create_all()

# File upload configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('smart_waste.html')

@app.route('/index', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect(url_for('detect_waste'))  # Redirect to detect_waste if logged in
    return render_template('index.html')

@app.route('/rindex', methods=['GET'])
def rindex():
    if 'user_id' not in session:
        flash('Please log in to access this page!', 'warning')
        return redirect(url_for('login'))
    return render_template('index.html')

# Route: Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')  # Get the selected role (admin or user)

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user and set the role
        new_user = User(username=username, password=hashed_password)
        
        if role == 'admin':
            new_user.is_admin = True  # Set is_admin to True if the role is admin

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_as = request.form.get('login_as')  # Get which button was clicked

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # Check if user is trying to login as admin but doesn't have admin privileges
            if login_as == 'admin' and not user.is_admin:
                flash('You do not have admin privileges!', 'danger')
                return redirect(url_for('login'))
            
            # Check if user is trying to login as user but has admin account
            if login_as == 'user' and user.is_admin:
                flash('Please use Admin Login for admin accounts!', 'warning')
                return redirect(url_for('login'))
            
            session.permanent = True  # Make session permanent
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin  # Store the user's admin status in the session
            
            if user.is_admin:  # Check if the user is an admin
                flash(f'Welcome Admin {username}!', 'success')
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            else:
                flash(f'Welcome {username}!', 'success')
                return redirect(url_for('detect_waste'))  # Redirect to user page (waste detection)
        
        flash('Invalid username or password!', 'danger')
        return redirect(url_for('login'))  # Return to login if authentication fails

    return render_template('login.html')

# Route: Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

# Route: Detect Waste
@app.route('/detect', methods=['GET', 'POST'])
def detect_waste():
    if 'user_id' not in session:
        flash('Please log in to access this page!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded!', 'danger')
            return redirect(url_for('detect_waste'))

        file = request.files['file']
        if file:
            # Save the uploaded file
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Run the YOLOv5 model
            results = model(file_path)
            predictions = results.pandas().xyxy[0]

            # Process predictions
            if not predictions.empty:
                output = []
                for _, row in predictions.iterrows():
                    classification = row['name']
                    confidence = row['confidence'] * 100
                    disposal = "This item should go into the general waste bin."
                    if classification == "Recyclable":
                        disposal = "Please place this item in the recycling bin."
                    elif classification == "Compostable":
                        disposal = "This item can be composted; please add it to your compost bin."
                    output.append({
                        "classification": classification,
                        "confidence": f"{confidence:.2f}%",
                        "disposal": disposal
                    })

                # Pass image and predictions to the result page
                image_url = url_for('static', filename=f'uploads/{file.filename}')
                return render_template('result.html', image_url=image_url, predictions=output)
            
            flash('No waste detected!', 'info')
            return render_template('result.html', image_url=None, predictions=[])

    return render_template('index.html')

@app.route('/save_location', methods=['POST'])
def save_location():
    data = request.get_json()
    location_name = data.get('location')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude and longitude:
        new_location = WasteLocation(location_name=location_name, latitude=latitude, longitude=longitude, user_id=session['user_id'])
        db.session.add(new_location)
        db.session.commit()
        return jsonify({'message': 'Location saved successfully!'})
    else:
        return jsonify({'error': 'Invalid location data!'}), 400

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))  # Redirect to login if not an admin
    locations = WasteLocation.query.all()
    locations = [
        {
            "id": loc.id,
            "location_name":loc.location_name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "username": loc.user.username,
            'is_completed': loc.is_completed, 
        }
        for loc in locations
    ]
    locations = locations if locations else []
    return render_template('admin_dashboard.html', locations=locations)

@app.route('/submit-location', methods=['POST'])
def submit_location():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to submit a location!', 'warning')
        return redirect(url_for('login'))
    
    # Get the location from the form input
    location_name = request.form.get('location')
    
    if not location_name:
        flash('Location name is required!', 'danger')
        return redirect(url_for('detect_waste'))

    # Geocode the location to get latitude and longitude
    geolocator = Nominatim(user_agent="smart-waste-app")
    try:
        location = geolocator.geocode(location_name)
        if location:
            latitude = location.latitude
            longitude = location.longitude
            user_id = session['user_id']

            # Save the location in the database
            new_location = WasteLocation(location_name=location_name, latitude=latitude, longitude=longitude, user_id=session['user_id'])
            db.session.add(new_location)
            db.session.commit()

            flash(f"Location '{location_name}' submitted successfully!", 'success')
        else:
            flash(f"Could not find location: {location_name}", 'danger')
    except Exception as e:
        flash(f"Error processing location: {str(e)}", 'danger')
    return redirect(url_for('detect_waste'))


@app.route('/real')
def real_time_processing():
    global process
    try:
        # Start the real-time processing script using absolute path
        script_path = os.path.join(BASE_DIR, 'waste.v3i.yolov5pytorch', 'yolov5', 'waste-sorte', 'r.py')
        
        # Check if file exists
        if not os.path.exists(script_path):
            flash(f'Real-time processing script not found at: {script_path}', 'danger')
            return redirect(url_for('detect_waste'))
        
        # Start the process
        process = subprocess.Popen(['python', script_path], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        flash('Real-time processing started successfully!', 'success')
        return redirect(url_for('detect_waste'))
    except Exception as e:
        flash(f'Error starting real-time processing: {str(e)}', 'danger')
        return redirect(url_for('detect_waste'))

@app.route('/stop_processing', methods=['POST'])
def stop_processing():
    global process
    try:
        if process and process.poll() is None:  # Check if the process is running
            process.terminate()  # Send termination signal
            process.wait(timeout=5)
            process = None
            flash('Real-time processing stopped successfully!', 'success')
        else:
            flash('No active real-time processing to stop.', 'info')
        return redirect(url_for('detect_waste'))
    except Exception as e:
        flash(f'Error stopping real-time processing: {str(e)}', 'danger')
        return redirect(url_for('detect_waste'))


@app.route('/delete_location/<int:location_id>', methods=['POST'])
def delete_location(location_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied! Admins only.', 'danger')
        return redirect(url_for('login'))  # Redirect to login if not an admin

    location = WasteLocation.query.get(location_id)
    if location:
        db.session.delete(location)
        db.session.commit()
        flash(f"Location '{location.location_name}' deleted successfully.", 'success')
    else:
        flash('Location not found!', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/update_completion/<int:location_id>', methods=['POST'])
def update_completion(location_id):
    data = request.get_json()
    is_completed = data.get('is_completed', False)

    location = WasteLocation.query.get_or_404(location_id)
    location.is_completed = is_completed
    db.session.commit()

    return jsonify({"success": True})


@app.route('/update_status/<int:location_id>', methods=['POST'])
def update_status(location_id):
    location = WasteLocation.query.get_or_404(location_id)
    location.is_completed = not location.is_completed  # Toggle status
    db.session.commit()
    return jsonify({"success": True, "is_completed": location.is_completed})

@app.route('/location_history')
def location_history():
    if 'user_id' not in session:
        flash('Please log in to view location history!', 'warning')
        return redirect(url_for('login'))

    # Fetch locations added by the logged-in user
    user_id = session['user_id']
    locations = WasteLocation.query.filter_by(user_id=user_id).all()

    # Pass the locations to the template
    return render_template('location_history.html', locations=locations)

if __name__ == '__main__':
    app.run(debug=True)