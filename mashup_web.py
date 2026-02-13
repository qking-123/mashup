from flask import Flask, render_template, request, jsonify
import os
import shutil
import tempfile
import zipfile
import threading
import re
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

app = Flask(__name__)


def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None


def download_videos(singer, count, temp_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch{count}:{singer} songs", download=True)
        if not results or 'entries' not in results:
            raise Exception("No videos found")


def cut_audios(temp_dir, duration):
    audio_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3')]
    if not audio_files:
        raise Exception("No audio files found")
    
    cut_files = []
    for audio_file in audio_files:
        try:
            audio = AudioSegment.from_mp3(os.path.join(temp_dir, audio_file))
            cut_audio = audio[:duration * 1000]
            cut_path = os.path.join(temp_dir, f"cut_{audio_file}")
            cut_audio.export(cut_path, format="mp3")
            cut_files.append(cut_path)
        except:
            continue
    
    if not cut_files:
        raise Exception("Failed to process audio")
    return cut_files


def merge_audios(files, output):
    merged = AudioSegment.from_mp3(files[0])
    for audio_file in files[1:]:
        merged += AudioSegment.from_mp3(audio_file)
    merged.export(output, format="mp3")


def create_zip(mp3_file, zip_file):
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(mp3_file, os.path.basename(mp3_file))


def send_email(recipient, zip_file, singer):
    sender = "simantasaha792@gmail.com"
    password = "jduzwbxlwxxfrdzb"
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = f"Your {singer} Mashup"
    
    body = f"Hey!\n\nYour mashup for {singer} is ready. Check the attachment.\n\nEnjoy!"
    msg.attach(MIMEText(body, 'plain'))
    
    with open(zip_file, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(zip_file)}"')
        msg.attach(part)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False


def process_mashup(singer, count, duration, email):
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        
        download_videos(singer, count, temp_dir)
        cut_files = cut_audios(temp_dir, duration)
        
        output_mp3 = os.path.join(temp_dir, f"{singer.replace(' ', '_')}_mashup.mp3")
        merge_audios(cut_files, output_mp3)
        
        output_zip = os.path.join(temp_dir, f"{singer.replace(' ', '_')}_mashup.zip")
        create_zip(output_mp3, output_zip)
        
        send_email(email, output_zip, singer)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    try:
        singer = request.form.get('singer_name', '').strip()
        num_videos = request.form.get('num_videos', '').strip()
        duration = request.form.get('duration', '').strip()
        email = request.form.get('email', '').strip()
        
        if not singer:
            return jsonify({'success': False, 'message': 'Singer name required'})
        
        if not email or not is_valid_email(email):
            return jsonify({'success': False, 'message': 'Valid email required'})
        
        try:
            num_videos = int(num_videos)
            if num_videos <= 10:
                return jsonify({'success': False, 'message': 'Videos must be > 10'})
        except:
            return jsonify({'success': False, 'message': 'Invalid video count'})
        
        try:
            duration = int(duration)
            if duration <= 20:
                return jsonify({'success': False, 'message': 'Duration must be > 20s'})
        except:
            return jsonify({'success': False, 'message': 'Invalid duration'})
        
        thread = threading.Thread(target=process_mashup, args=(singer, num_videos, duration, email))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': f'Creating your mashup! Check {email} soon.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {e}'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
