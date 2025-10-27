import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, json, session
from flask_socketio import SocketIO, emit
from datetime import datetime
import time
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, generate_csrf, CSRFError
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from pathlib import Path
import sys
import uuid

# Add the engine directory to the path
sys.path.append(str(Path(__file__).parent.parent / 'engine'))
from synthesizer import Synthesizer

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forj.db'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get('CSRF_SECRET_KEY') or 'another-secret-key-please-change'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'datasets'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', [validators.DataRequired(), validators.Length(min=2, max=100)])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match'),
        validators.Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise validators.ValidationError('Email already registered.')

class DatasetForm(FlaskForm):
    description = TextAreaField('Description', [validators.DataRequired(), validators.Length(min=10, max=1000)])
    columns = TextAreaField('Columns', [validators.DataRequired()])
    row_count = IntegerField('Number of Rows', [validators.NumberRange(min=1, max=10000)], default=100)
    submit = SubmitField('Generate Dataset')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    datasets = db.relationship('Dataset', backref='owner', lazy=True)

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    columns = db.Column(db.Text, nullable=False)  # JSON string of columns
    schema = db.Column(db.Text, nullable=True)  # JSON string of schema
    data = db.Column(db.Text, nullable=True)  # JSON string of data
    row_count = db.Column(db.Integer, nullable=False, default=100)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Float, default=0.0)
    logs = db.Column(db.Text, default='[]')  # JSON array of log entries
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)
    
    def add_log(self, message, log_type='info'):
        """Add a log entry to the dataset."""
        logs = json.loads(self.logs or '[]')
        log_entry = {
            'id': str(time.time() * 1000),  # Unique ID based on timestamp
            'timestamp': datetime.utcnow().isoformat(),
            'type': log_type,
            'message': message
        }
        logs.append(log_entry)
        self.logs = json.dumps(logs)
        db.session.commit()
        
        # Emit socket.io event for real-time updates
        socketio.emit('log_update', {
            'dataset_id': self.id,
            'log': log_entry
        })
        
    def update_progress(self, progress):
        """Update the progress of dataset generation."""
        self.progress = min(100.0, max(0.0, float(progress)))
        db.session.commit()
        
        # Emit socket.io event for progress updates
        socketio.emit('progress_update', {
            'dataset_id': self.id,
            'progress': self.progress
        })

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize Synthesizer
synthesizer = Synthesizer()

# In-memory storage for feedback sessions (in production, use Redis or database)
feedback_sessions = {}

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get all datasets for the current user, ordered by creation date (newest first)
    datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(Dataset.created_at.desc()).all()
    return render_template('dashboard.html', datasets=datasets)

@app.route('/create-dataset', methods=['GET', 'POST'])
@login_required
def create_dataset():
    form = DatasetForm()
    
    if form.validate_on_submit():
        try:
            # Process the form data
            description = form.description.data
            columns = [col.strip() for col in form.columns.data.split(',') if col.strip()]
            row_count = form.row_count.data
            
            if not columns:
                flash('Please enter at least one column name.', 'error')
                return render_template('create_dataset.html', form=form)
            
            # Create a name from the first few words of the description
            name = ' '.join(description.split()[:5])[:50]  # First 5 words, max 50 chars
            
            # Create a new dataset record
            dataset = Dataset(
                name=name,
                description=description,
                user_id=current_user.id,
                row_count=row_count,
                columns=json.dumps(columns),
                schema=json.dumps([{'name': col, 'type': 'text'} for col in columns]),
                data='[]',  # Will be generated by the background task
                status='pending',
                file_path=None  # Will be set when the dataset is generated
            )
            
            db.session.add(dataset)
            db.session.commit()
            
            # Start the background task
            from threading import Thread
            
            def generate_dataset_task(dataset_id, description, columns, row_count):
                with app.app_context():
                    try:
                        from synthesizer import Synthesizer
                        import os
                        from datetime import datetime
                        
                        dataset = Dataset.query.get(dataset_id)
                        if not dataset:
                            app.logger.error('Dataset {} not found'.format(dataset_id))
                            return
                        
                        # Update status to processing
                        dataset.status = 'processing'
                        dataset.add_log('Starting dataset generation...')
                        db.session.commit()
                        
                        # Initialize the synthesizer with progress callback
                        def progress_callback(progress, message):
                            dataset = Dataset.query.get(dataset_id)
                            if dataset:
                                dataset.update_progress(progress)
                                if message:
                                    dataset.add_log(message)
                        
                        synthesizer = Synthesizer()
                        
                        # Generate the dataset
                        dataset.add_log('Initializing data generation...')
                        dataset.update_progress(10)
                        
                        try:
                            dataset_data, log_path = synthesizer.create_dataset(
                                description=description,
                                columns=columns,
                                num_rows=row_count
                            )
                        except Exception as e:
                            dataset.status = 'failed'
                            dataset.add_log(f'Error during dataset generation: {str(e)}', 'error')
                            db.session.commit()
                            return
                        
                        dataset.add_log('Dataset generated successfully')
                        dataset.update_progress(70)
                        
                        # Save the dataset to a file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        safe_name = "".join(c if c.isalnum() else "_" for c in dataset.name)[:50]
                        filename = "dataset_{}_{}.csv".format(safe_name, timestamp)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        
                        # Ensure upload directory exists
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        
                        try:
                            # Write the dataset to a CSV file
                            with open(filepath, 'w', encoding='utf-8') as f:
                                # Write header
                                f.write(','.join(columns) + '\n')
                                # Write data
                                for i, row in enumerate(dataset_data):
                                    row_data = []
                                    for cell in row:
                                        cell_str = str(cell)
                                        if ',' in cell_str or '"' in cell_str or '\n' in cell_str:
                                            # Escape quotes by doubling them and wrap in quotes
                                            cell_str = '"' + cell_str.replace('"', '""') + '"'
                                        row_data.append(cell_str)
                                    f.write(','.join(row_data) + '\n')
                                    
                                    # Update progress every 10%
                                    if (i + 1) % max(1, len(dataset_data) // 10) == 0:
                                        progress = 70 + int(25 * (i + 1) / len(dataset_data))
                                        dataset.update_progress(progress)
                                        dataset.add_log(f'Processed {i + 1}/{len(dataset_data)} rows')
                            
                            # Update dataset with file path and status
                            dataset.file_path = filepath
                            dataset.status = 'completed'
                            dataset.update_progress(100)
                            dataset.add_log(f'Dataset saved to {filepath}')
                            db.session.commit()
                            
                            app.logger.info('Successfully generated dataset {}'.format(dataset_id))
                            
                        except Exception as e:
                            dataset.status = 'failed'
                            dataset.add_log(f'Error saving dataset: {str(e)}', 'error')
                            db.session.commit()
                            
                    except Exception as e:
                        app.logger.error('Error in background task: {}'.format(str(e)))
                        if 'dataset' in locals():
                            dataset.status = 'failed'
                            dataset.add_log(f'Unexpected error: {str(e)}', 'error')
                            db.session.commit()
            
            # Start the background task
            thread = Thread(target=generate_dataset_task, args=(dataset.id, description, columns, row_count))
            thread.daemon = True
            thread.start()
            
            # Redirect to the dataset status page
            return redirect(url_for('dataset_status', dataset_id=dataset.id))
            
        except Exception as e:
            app.logger.error('Error creating dataset: {}'.format(str(e)))
            flash('An error occurred while creating the dataset. Please try again.', 'error')
    
    return render_template('create_dataset.html', form=form)

@app.route('/datasets/<int:dataset_id>/status')
@login_required
def dataset_status(dataset_id):
    """Endpoint to check the status of a dataset generation."""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Ensure the user owns this dataset
    if dataset.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': dataset.id,
        'status': dataset.status,
        'progress': dataset.progress,
        'logs': json.loads(dataset.logs or '[]'),
        'file_path': dataset.file_path,
        'created_at': dataset.created_at.isoformat(),
        'updated_at': dataset.updated_at.isoformat()
    })

@app.route('/datasets/<int:dataset_id>')
@login_required
def view_dataset(dataset_id):
    """View a dataset's details and status."""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Ensure the user owns this dataset
    if dataset.user_id != current_user.id:
        flash('You do not have permission to view this dataset.', 'error')
        return redirect(url_for('dashboard'))
    
    # Load the dataset data
    try:
        data = []
        if dataset.file_path and os.path.exists(dataset.file_path):
            with open(dataset.file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                columns = next(reader)  # Get header
                # Get first 10 rows for preview
                for i, row in enumerate(reader):
                    if i >= 10:
                        break
                    data.append(row)
        else:
            columns = json.loads(dataset.columns)
            
        return render_template('view_dataset.html', 
                           dataset=dataset, 
                           columns=columns,
                           data=data,
                           row_count=len(data))
    except Exception as e:
        app.logger.error(f'Error loading dataset: {str(e)}')
        flash('An error occurred while loading the dataset.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/start-generation', methods=['POST'])
@login_required
def start_generation():
    """Start a new dataset generation session with feedback loop."""
    try:
        data = request.get_json()
        description = data.get('description')
        columns = data.get('columns', [])
        row_count = int(data.get('row_count', 10))
        
        if not description or not columns:
            return jsonify({'error': 'Description and columns are required'}), 400
        
        # Create a new session for this generation
        session_id = str(uuid.uuid4())
        feedback_sessions[session_id] = {
            'description': description,
            'columns': columns,
            'row_count': row_count,
            'feedback_round': 0,
            'feedback': [],
            'all_samples': [],
            'status': 'generating_samples',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Generate initial samples
        return _generate_samples(session_id)
        
    except Exception as e:
        app.logger.error(f'Error starting generation: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500

def _generate_samples(session_id):
    """Generate samples for a given session."""
    try:
        session_data = feedback_sessions[session_id]
        synthesizer = Synthesizer()
        
        # Update generation prompt with feedback if any
        generation_prompt = session_data['description']
        if session_data['feedback']:
            feedback_text = "\n".join(
                f"Feedback: {fb['text']} (Approved: {fb['approved']})" 
                for fb in session_data['feedback'][-3:]  # Include last 3 feedback items
            )
            generation_prompt += f"\n\nPrevious feedback to consider:\n{feedback_text}"
        
        # Generate samples (5 at a time)
        sample_size = 5
        sample_data, _ = synthesizer.create_dataset(
            generation_prompt,
            session_data['columns'],
            sample_size,
            interactive=False
        )
        
        # Convert samples to dict format
        formatted_samples = []
        for i, sample in enumerate(sample_data):
            sample_id = f"{session_id}_sample_{len(session_data['all_samples']) + i + 1}"
            formatted_samples.append({
                'id': sample_id,
                'data': sample,
                'feedback': None,
                'approved': None
            })
        
        # Update session data
        session_data['current_samples'] = formatted_samples
        session_data['status'] = 'awaiting_feedback'
        session_data['feedback_round'] += 1
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'samples': formatted_samples,
            'feedback_round': session_data['feedback_round'],
            'status': session_data['status']
        })
        
    except Exception as e:
        app.logger.error(f'Error generating samples: {str(e)}', exc_info=True)
        feedback_sessions[session_id]['status'] = 'error'
        return jsonify({'error': str(e), 'session_id': session_id}), 500

@app.route('/api/submit-feedback', methods=['POST'])
@login_required
def submit_feedback():
    """Submit feedback for generated samples."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        feedback_items = data.get('feedback', [])
        
        if not session_id or session_id not in feedback_sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
            
        session_data = feedback_sessions[session_id]
        
        # Update feedback for each sample
        for fb in feedback_items:
            sample_id = fb.get('sample_id')
            approved = fb.get('approved', False)
            text = fb.get('text', '')
            
            # Find the sample in current samples
            for sample in session_data['current_samples']:
                if sample['id'] == sample_id:
                    sample['feedback'] = text
                    sample['approved'] = approved
                    break
        
        # Add to all samples
        session_data['all_samples'].extend(session_data['current_samples'])
        
        # Check if all samples were approved
        all_approved = all(sample.get('approved', False) for sample in session_data['current_samples'])
        
        if all_approved or session_data['feedback_round'] >= 3:  # Max 3 feedback rounds
            # Generate full dataset
            return _generate_final_dataset(session_id)
        else:
            # Generate new samples with feedback
            return _generate_samples(session_id)
            
    except Exception as e:
        app.logger.error(f'Error submitting feedback: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500

def _generate_final_dataset(session_id):
    """Generate the final dataset after feedback is complete."""
    try:
        session_data = feedback_sessions[session_id]
        synthesizer = Synthesizer()
        
        # Generate final dataset
        final_data, _ = synthesizer.create_dataset(
            session_data['description'],
            session_data['columns'],
            session_data['row_count'],
            interactive=False
        )
        
        # Save the dataset (implement your saving logic here)
        # For now, just return the data
        
        session_data['status'] = 'completed'
        session_data['final_dataset'] = final_data
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'status': 'completed',
            'dataset': final_data[:10],  # Return first 10 rows as preview
            'total_rows': len(final_data)
        })
        
    except Exception as e:
        app.logger.error(f'Error generating final dataset: {str(e)}', exc_info=True)
        feedback_sessions[session_id]['status'] = 'error'
        return jsonify({'error': str(e), 'session_id': session_id}), 500

@app.route('/api/finalize-dataset', methods=['POST'])
@login_required
def finalize_dataset():
    """Create the final dataset with the full number of rows."""
    try:
        data = request.get_json()
        description = data.get('description')
        columns = data.get('columns', [])
        row_count = int(data.get('row_count', 100))
        feedback = data.get('feedback', '')
        
        if not description:
            return jsonify({'error': 'Description is required'}), 400
            
        if not columns:
            return jsonify({'error': 'At least one column is required'}), 400
        
        # Create a name from the first few words of the description
        name = ' '.join(description.split()[:5])[:50]
        
        # Create a new dataset record
        dataset = Dataset(
            name=name,
            description=description,
            user_id=current_user.id,
            row_count=row_count,
            columns=json.dumps(columns),
            schema=json.dumps([{'name': col, 'type': 'text'} for col in columns]),
            status='processing',
            progress=0
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        # Start background task to generate the full dataset
        from threading import Thread
        
        def generate_dataset_task(dataset_id, description, columns, row_count, feedback):
            with app.app_context():
                try:
                    dataset = Dataset.query.get(dataset_id)
                    if not dataset:
                        app.logger.error(f'Dataset {dataset_id} not found')
                        return
                    
                    # Update status
                    dataset.status = 'processing'
                    dataset.add_log('Starting dataset generation...')
                    db.session.commit()
                    
                    # Initialize the synthesizer
                    synthesizer = Synthesizer()
                    
                    # Include any feedback in the generation
                    generation_prompt = description
                    if feedback:
                        generation_prompt += f"\n\nPrevious feedback to incorporate: {feedback}"
                    
                    # Generate the dataset
                    dataset.add_log('Generating data...')
                    dataset.update_progress(10)
                    
                    dataset_data, log_path = synthesizer.create_dataset(
                        description=generation_prompt,
                        columns=columns,
                        num_rows=row_count
                    )
                    
                    dataset.add_log('Data generation complete. Saving to file...')
                    dataset.update_progress(70)
                    
                    # Save the dataset to a file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_name = "".join(c if c.isalnum() else "_" for c in dataset.name)[:50]
                    filename = f"dataset_{safe_name}_{timestamp}.csv"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    # Ensure upload directory exists
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Write the dataset to a CSV file
                    with open(filepath, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(columns)
                        
                        for i, row in enumerate(dataset_data):
                            writer.writerow(row)
                            
                            # Update progress every 5%
                            if (i + 1) % max(1, row_count // 20) == 0:
                                progress = 70 + int(25 * (i + 1) / row_count)
                                dataset.update_progress(min(progress, 95))
                    
                    # Update dataset with file path and status
                    dataset.file_path = filepath
                    dataset.status = 'completed'
                    dataset.update_progress(100)
                    dataset.add_log(f'Dataset saved to {filepath}')
                    db.session.commit()
                    
                    app.logger.info(f'Successfully generated dataset {dataset_id}')
                    
                except Exception as e:
                    app.logger.error(f'Error in background task: {str(e)}')
                    if 'dataset' in locals():
                        dataset.status = 'failed'
                        dataset.add_log(f'Error: {str(e)}', 'error')
                        db.session.commit()
        
        # Start the background task
        thread = Thread(
            target=generate_dataset_task,
            args=(dataset.id, description, columns, row_count, feedback)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'dataset_id': dataset.id
        })
        
    except Exception as e:
        app.logger.error(f'Error finalizing dataset: {str(e)}')
        return jsonify({'error': str(e)}), 500



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Successfully logged in!', 'success')
            return redirect(next_page or url_for('dashboard'))
            
        flash('Invalid email or password', 'error')
        
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                name=form.name.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data, method='pbkdf2:sha256')
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error during registration: {str(e)}')
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('register.html', form=form)

# Custom Jinja2 filter to parse JSON strings
def from_json(value):
    """Convert a JSON string to a Python object."""
    if not value:
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}

def number_format(value, format=",d"):
    """Format a number with thousands separators."""
    if value is None:
        return ""
    try:
        return f"{value:,}"
    except (ValueError, TypeError):
        return str(value)

def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    if dt is None:
        return default
    
    now = datetime.utcnow()
    diff = now - dt
    
    periods = [
        ('year', 60*60*24*365),
        ('month', 60*60*24*30),
        ('day', 60*60*24),
        ('hour', 60*60),
        ('minute', 60),
        ('second', 1)
    ]
    
    for period, seconds in periods:
        value = diff.total_seconds() // seconds
        if value > 0:
            if value > 1:
                period += 's'
            return f"{int(value)} {period} ago"
    return default

# Register custom filters
app.jinja_env.filters['from_json'] = from_json
app.jinja_env.filters['number_format'] = number_format
app.jinja_env.filters['timesince'] = timesince

@app.route('/api/datasets/<int:dataset_id>', methods=['GET'])
@login_required
def get_dataset(dataset_id):
    try:
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first()
        if not dataset:
            return jsonify({
                'status': 'error',
                'message': 'Dataset not found or access denied'
            }), 404
            
        return jsonify({
            'id': dataset.id,
            'name': dataset.name,
            'description': dataset.description,
            'columns': json.loads(dataset.columns) if dataset.columns else [],
            'data': json.loads(dataset.data) if dataset.data else [],
            'row_count': dataset.row_count,
            'status': dataset.status,
            'created_at': dataset.created_at.isoformat(),
            'updated_at': dataset.updated_at.isoformat()
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error getting dataset {dataset_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/save-dataset', methods=['POST'])
@login_required
def save_dataset():
    try:
        data = request.get_json()
        
        # Create a new dataset record
        dataset = Dataset(
            name=f"Generated Dataset {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            description="AI-generated dataset",
            columns=json.dumps(data.get('columns', [])),
            data=json.dumps(data.get('dataset', [])),
            row_count=data.get('row_count', 0),
            status='completed',
            user_id=current_user.id,
            file_path=None
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Dataset saved successfully',
            'dataset_id': dataset.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error saving dataset: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/documentation')
def documentation():
    """Documentation page"""
    return render_template('documentation.html')

@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page"""
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    """Terms of Service page"""
    return render_template('terms_of_service.html')

# Error handler for CSRF errors
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('The form has expired. Please try again.', 'error')
    return redirect(request.referrer or url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/dataset-info/<session_id>')
@login_required
def get_dataset_info(session_id):
    """Get dataset information by session ID."""
    try:
        dataset = Dataset.query.filter_by(id=session_id).first()
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
            
        if dataset.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        return jsonify({
            'dataset_id': dataset.id,
            'name': dataset.name,
            'status': dataset.status,
            'created_at': dataset.created_at.isoformat(),
            'row_count': dataset.row_count
        })
    except Exception as e:
        app.logger.error(f'Error getting dataset info: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/download/dataset/<int:dataset_id>')
@login_required
def download_dataset(dataset_id):
    """Download a dataset file."""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Ensure the user owns this dataset
    if dataset.user_id != current_user.id:
        return 'Unauthorized', 403
    
    if not dataset.file_path or not os.path.exists(dataset.file_path):
        return 'File not found', 404
    
    # Get a safe filename
    safe_name = "".join(c if c.isalnum() else "_" for c in dataset.name)[:50]
    extension = os.path.splitext(dataset.file_path)[1] or '.csv'
    filename = f"{safe_name}{extension}"
    
    return send_from_directory(
        os.path.dirname(dataset.file_path),
        os.path.basename(dataset.file_path),
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
