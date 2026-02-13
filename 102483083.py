import os
import shutil
import sys
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import tempfile
import subprocess

ffmpeg_path = r"C:\Program Files\Softdeluxe\Free Download Manager\ffmpeg.exe"
if os.path.exists(ffmpeg_path):
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path
    os.environ['PATH'] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ.get('PATH', '')


def convert_webm(webm_path, wav_path):
    if not os.path.exists(ffmpeg_path):
        raise Exception("ffmpeg not found")
    
    try:
        subprocess.run(
            [ffmpeg_path, "-i", webm_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", wav_path, "-y"],
            capture_output=True,
            timeout=60
        )
        return os.path.exists(wav_path)
    except:
        return False


def create_test_files(temp_dir, count):
    for i in range(count):
        audio = AudioSegment.silent(duration=60000)
        audio_path = os.path.join(temp_dir, f"test_{i}.wav")
        audio.export(audio_path, format="wav")
    print(f"✓ Created {count} test audio files")


def validate_args(args):
    if len(args) != 5:
        print("Usage: python mashup.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        print("       python mashup.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName> --test")
        return False
    
    try:
        num_videos = int(args[2])
        if num_videos <= 10:
            print("✗ Number of videos must be > 10")
            return False
    except ValueError:
        print("✗ Invalid number of videos")
        return False
    
    try:
        duration = int(args[3])
        if duration <= 20:
            print("✗ Duration must be > 20 seconds")
            return False
    except ValueError:
        print("✗ Invalid duration")
        return False
    
    return True


def download_videos(singer, count, temp_dir):
    print(f"⬇ Downloading {count} videos for '{singer}'...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'socket_timeout': 30,
        'fragment_retries': 5,
        'retries': 5,
        'skip_unavailable_fragments': True,
    }
    
    downloaded = 0
    with YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch{count}:{singer} songs", download=True)
            if results and 'entries' in results:
                downloaded = len(results['entries'])
        except Exception as e:
            print(f"Download warning: {e}")
    
    if downloaded < 3:
        raise Exception(f"Only downloaded {downloaded} videos (need at least 3)")
    
    print(f"✓ Downloaded {downloaded} videos")


def process_audios(temp_dir, duration):
    print(f"✂ Cutting audio to {duration}s...")
    
    audio_files = [f for f in os.listdir(temp_dir) if f.endswith(('.mp3', '.m4a', '.wav', '.webm', '.opus'))]
    if not audio_files:
        raise Exception("No audio files found")
    
    cut_files = []
    for audio_file in audio_files:
        try:
            audio_path = os.path.join(temp_dir, audio_file)
            ext = os.path.splitext(audio_file)[1][1:]
            
            if not ext:
                continue
            
            if ext == 'webm':
                temp_wav = os.path.join(temp_dir, f"temp_{os.path.splitext(audio_file)[0]}.wav")
                if not convert_webm(audio_path, temp_wav):
                    continue
                audio_path = temp_wav
                ext = 'wav'
            
            audio = AudioSegment.from_file(audio_path, format=ext)
            cut_audio = audio[:duration * 1000]
            
            cut_path = os.path.join(temp_dir, f"cut_{os.path.splitext(audio_file)[0]}.wav")
            cut_audio.export(cut_path, format="wav")
            cut_files.append(cut_path)
        except:
            continue
    
    if not cut_files:
        raise Exception("Failed to process any audio files")
    
    print(f"✓ Processed {len(cut_files)} files")
    return cut_files


def merge_files(files, output):
    print(f"🔗 Merging {len(files)} files...")
    
    merged = AudioSegment.from_wav(files[0])
    for audio_file in files[1:]:
        merged += AudioSegment.from_wav(audio_file)
    
    wav_output = output.replace('.mp3', '.wav')
    merged.export(wav_output, format="wav")
    
    if output.endswith('.mp3') and output != wav_output:
        try:
            wav_audio = AudioSegment.from_wav(wav_output)
            wav_audio.export(output, format="mp3")
            os.remove(wav_output)
            print(f"✓ Created {output}")
        except:
            print(f"✓ Created {wav_output}")
    else:
        print(f"✓ Created {wav_output}")


def main():
    test_mode = '--test' in sys.argv
    if test_mode:
        sys.argv.remove('--test')
    
    if not validate_args(sys.argv):
        sys.exit(1)
    
    singer = sys.argv[1]
    count = int(sys.argv[2])
    duration = int(sys.argv[3])
    output = sys.argv[4]
    
    if not output.endswith('.mp3'):
        output += '.mp3'
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        if test_mode:
            create_test_files(temp_dir, count)
        else:
            download_videos(singer, count, temp_dir)
        
        cut_files = process_audios(temp_dir, duration)
        merge_files(cut_files, output)
        print("\n✓ Done!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
