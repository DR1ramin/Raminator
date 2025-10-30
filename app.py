# Gemini ===>
import google.generativeai as genai
# from google.genai import types

# Gemini ===<
from flask import Flask, request, jsonify
from base64 import b64decode
from pathlib import Path

from flask import Flask, render_template,jsonify,request, redirect, url_for, flash, session,send_from_directory
from models import  db,User,bcrypt
import os
import time
from datetime import datetime
import threading
import requests
import markdown
from bs4 import BeautifulSoup
from PIL import Image
import re
from pytube import YouTube
from moviepy.editor import VideoFileClip

app = Flask(__name__)

# Gemini ===>
genai.configure(api_key="AIzaSyCVI_2GQSVSr4mJUkmObt38Xp53Q8RJS88")

# Gemini ===<
# speek to text ====>
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
UPLOAD_FOLDER = 'uploads'
# speek to text ====<

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'

# Initialize the database to Flask
db.init_app(app)
bcrypt.init_app(app)
# Create database
with app.app_context():
    db.create_all()
# speek to text ====>




# speek to text ====<

# Define the directory to save images (ensure this folder exists or create it dynamically)
IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
def extract_images_from_url(url):
    try:
        # ارسال درخواست GET به URL
        response = requests.get(url)
        response.raise_for_status()  # بررسی خطا در درخواست

        # تحلیل HTML با BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # پیدا کردن تمام تگ‌های <img>
        image_tags = soup.find_all("img")
        image_urls = []

        for img in image_tags:
            if "src" in img.attrs:
                src = img["src"]
                # اگر لینک تصویر نسبی باشد، آن را به لینک مطلق تبدیل می‌کنیم
                if not src.startswith("http"):
                    from urllib.parse import urljoin
                    src = urljoin(url, src)
                image_urls.append(src)

        return image_urls
    except Exception as e:
        print(f"Error extracting images: {e}")
        return []


@app.route('/generate_image', methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        paragraph_id = data.get('paragraph_id')
        search_text = data.get('text')
        
        # جستجوی تصاویر بر اساس متن
        images = extract_images_from_url(f"https://www.google.com/search?q={search_text}&tbm=isch")
        
        return jsonify({
            'status': 'success',
            'paragraph_id': paragraph_id,
            'images': images,
            'search_text': search_text
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500



@app.route('/generate_image_ai', methods=['POST'])
def generate_image_ai():
  
    #This route accepts a POST request with a JSON payload containing a 'prompt'.
    #It sends the prompt to an external API, retrieves the image data, and saves it locally.
  
    try:
        # Extract the 'prompt' from the POST request's JSON body
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
        prompt = data['text']
        
        # Generate a timestamp for the filename
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # Format: Year-Month-Day_Hour-Minute-Second
        
        # Send the request to the external API
        api_url = "https://api.imagepig.com/flux"
        headers = {"Api-Key": "8953d0b0-be71-4b23-b476-d86ca40f3aab"}
        payload = {
            "prompt":"Create picture According to this text : " + prompt,
            "proportion": "landscape"  # You can make this configurable if needed
        }
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Check if the API request was successful
        if response.ok:
            # Decode the base64 image data and save it to a file
            image_data = response.json().get("image_data")
            if not image_data:
                return jsonify({"error": "No image data received from the API"}), 500
            
            # Save the image with a timestamped filename
            file_path = IMAGE_DIR / f"image-{timestamp}.jpeg"
            with file_path.open("wb") as f:
                f.write(b64decode(image_data))
            
            # Return the path to the saved image
            resize_image_pillow(file_path,file_path,608,416)
            return jsonify({
                "message": "Image generated successfully",
                "image_path": str(file_path)
            }), 200
        else:
            # Raise an error if the API request failed
            response.raise_for_status()
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"error": str(e)}), 500

def resize_image_pillow(input_path, output_path, new_width, new_height):
    """
    Resizing an image using Pillow
    :param input_path: Input file path (original image)
    :param output_path: Output file path (resized image)
    :param new_width: New image width
    :param new_height: New image height   
    
    """
    # Open image
    image = Image.open(input_path)
    
    # Change image size
    resized_image = image.resize((new_width, new_height))
    
    # Save the modified image
    resized_image.save(output_path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/exam')
def exam():
    return render_template('exam.html')

@app.route('/success')
def success():
    return render_template('success.html')


# Gemini ===>
@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        # Get the name of the audio file from the request
        filename = request.json.get('filename')
        Language = request.json.get('Language')
        
        # Configure the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Read the audio file
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as audio_file:
            audio_content = audio_file.read()
        
        # Create the prompt
        prompt = f"""Analyze this audio content and provide a detailed transcription in {Language}.
        Follow these instructions:
        1. Transcribe everything that was said
        2. Use engaging emojis and relevant symbols
        3. Structure the content as a lesson
        4. Explain key concepts and ideas
        5. Highlight important points
        6. Provide a clear conclusion
        7. Create 6 multiple-choice questions with answers
        8. End with 'Produced by RaminAtor'"""
        
        # Generate content
        response = model.generate_content([prompt, audio_content])
        
        if not response.text:
            return jsonify({'error': 'No response from the model'}), 500
            
        # Convert to HTML
        html_output = markdown.markdown(response.text)
        
        # Process HTML with BeautifulSoup
        soup = BeautifulSoup(html_output, 'html.parser')
        
        # Add IDs to elements
        for idx, element in enumerate(soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li'])):
            element['id'] = f'element-{idx}'
            img_tag = soup.new_tag('img', id=f'image-{idx}')
            element.insert_after(img_tag)
        
        # Remove content after "Produced by RaminAtor"
        target = "Produced by RaminAtor"
        for element in soup.descendants:
            if isinstance(element, str) and target in element:
                found = True
                current = element.find_parent()
                while current:
                    for sibling in list(current.next_siblings):
                        sibling.decompose()
                    current = current.parent
        
        return jsonify({'text': str(soup)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def is_markdown(text):
    """
    Detects whether the input text is written in Markdown format or not.
    :param text: Input text
    :return: True if the text contains Markdown format, False otherwise
    """
    # Common patterns in Markdown
    markdown_patterns = [
        r'^\s*#\s+',  # Headlines (like # Title)
        r'\*\*.*?\*\*', # Bold text (**text**)
        r'__.*?__',  # Bold text (__text__)
        r'\*.*?\*',  # Italic text (*text*)
        r'_.*?_',  # Italic text (_text_)
        r'!\[.*?\]\(.*?\)',  # Images (![alt](url))
        r'\[.*?\]\(.*?\)',  # Links ([text](url))
        r'```.*?```',  # Code blocks (```code```)
        r'^\s*[-*]\s+',  # Unordered lists (- item or * item)
        r'^\s*\d+\.\s+', # Numeric lists (1. item)
    ]

    # بررسی هر الگو
    for pattern in markdown_patterns:
        if re.search(pattern, text, re.MULTILINE | re.DOTALL):
            return True

    return False
# Gemini ===<


@app.route('/speek',methods=['GET', 'POST'])
def speek():
    return render_template('speek.html')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/examform')
def examcreate():
    return render_template('exam_create_form.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("✅ Login was successful!", "success")
            return redirect(url_for('success'))
        else:
            flash("❌ Incorrect email or password!", "danger")

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register_():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

       # Check if the email is not already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("❌ This email has already been registered!", "danger")
            return redirect(url_for('register'))

        # Save to database
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # We hash the password

        db.session.add(new_user)
        db.session.commit()

        flash("✅ Registration was successful!", "success")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash("✅ You have been logged out!", "success")
    return redirect(url_for('login'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    return jsonify(users_list)

# speek to text ====>
@app.route("/record", methods=["POST"])
def record():
    audio = request.files.get("audio")
    if audio:
        filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".wav"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        audio.save(filepath)
        clean_old_files()
        return jsonify({"message": "Audio recorded successfully!", "filename": filename})
    return jsonify({"message": "Error in recording audio!"}), 400


# speek to text ====<
EXPIRATION_TIME = 30 * 60  # 30 minutes in seconds
def clean_old_files():
    """حذف فایل‌های قدیمی"""
    current_time = time.time()

    if not os.path.exists(UPLOAD_FOLDER):
        print("The upload folder does not exist.")
        return

    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.isfile(file_path):
            file_creation_time = os.path.getmtime(file_path) # Change getctime to getmtime

            if current_time - file_creation_time > EXPIRATION_TIME:
                try:
                    os.remove(file_path)
                    print(f"Deleted old file: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")

@app.route('/fileupload', methods=['GET', 'POST'])
def fileupload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            clean_old_files()
            return render_template('speek.html', filename=file.filename)
    
    return render_template('speek.html')
def replace_words(text, replacements):
    """
    Replaces words in a given text based on a dictionary of replacements.
    
    :param text: str, input text
    :param replacements: dict, mapping of words to replace (keys) with their replacements (values)
    :return: str, modified text
    """
    for old_word, new_word in replacements.items():
        text = text.replace(old_word, new_word)
    return text

@app.route('/download_youtube', methods=['POST'])
def download_youtube():
    try:
        data = request.get_json()
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({'error': 'URL non fournie'}), 400
            
        # Vérifier si l'URL est valide
        if not re.match(r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+', youtube_url):
            return jsonify({'error': 'URL YouTube invalide'}), 400
            
        # Télécharger la vidéo
        yt = YouTube(youtube_url)
        video = yt.streams.filter(only_audio=True).first()
        
        # Générer un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"youtube_{timestamp}.mp4"
        mp3_filename = f"youtube_{timestamp}.mp3"
        
        # Télécharger la vidéo
        video_path = video.download(output_path=app.config['UPLOAD_FOLDER'], filename=video_filename)
        
        # Convertir en MP3
        video_clip = VideoFileClip(video_path)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], mp3_filename)
        video_clip.audio.write_audiofile(audio_path)
        
        # Nettoyer les fichiers temporaires
        video_clip.close()
        os.remove(video_path)
        
        return jsonify({
            'success': True,
            'filename': mp3_filename,
            'title': yt.title
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
