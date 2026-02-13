# How I Built the Mashup Application

## What Does This Do?

Takes multiple songs from YouTube, cuts the first few seconds from each, and combines them into one audio file.

## Step-by-Step Process

### 1. Chose the Right Tools

I needed libraries that could:
- Download videos from YouTube
- Work with audio files
- Create a web interface
- Send emails

**Selected:**
- `yt-dlp` for YouTube downloads
- `pydub` for audio editing
- `flask` for the website
- `smtplib` (built-in) for emails

### 2. Built the Command-Line Version First

Started simple with a script that:
1. Takes 4 inputs: singer name, number of videos, duration, output file
2. Validates the inputs
3. Does the work
4. Saves the result

**Why CLI first?** Easier to test and debug without dealing with web stuff.

### 3. Downloading Videos

Used yt-dlp to search YouTube and download:
```python
ydl_opts = {
    'format': 'bestaudio/best',  # Get best audio quality
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',  # Convert to audio
        'preferredcodec': 'mp3',
    }],
}
```

This searches for "{singer} songs" and downloads N videos.

### 4. Cutting Audio

Used pydub to cut the first Y seconds:
```python
audio = AudioSegment.from_mp3(file)
cut_audio = audio[:duration * 1000]  # Pydub uses milliseconds
cut_audio.export(output_file, format="mp3")
```

Looped through all downloaded files and cut each one.

### 5. Merging Everything

Combined all cut audio files:
```python
merged = AudioSegment.from_mp3(first_file)
for audio_file in remaining_files:
    merged += AudioSegment.from_mp3(audio_file)  # Just add them
merged.export(final_output, format="mp3")
```

### 6. Added Error Handling

Made sure to handle:
- Wrong number of arguments
- Invalid numbers (negative, too small)
- Network errors during download
- Corrupted audio files

Used try-except blocks everywhere important.

### 7. Managed Temporary Files

Created a temp folder for downloads, then deleted it after:
```python
temp_dir = tempfile.mkdtemp()
try:
    # Do all the work
finally:
    shutil.rmtree(temp_dir)  # Always cleanup
```

### 8. Built the Web Interface

Created Flask app with two routes:
- `/` - Shows the form
- `/process` - Handles form submission

Made an HTML form with:
- Singer name input
- Number of videos (with validation: > 10)
- Duration (with validation: > 20)
- Email address

Added CSS for nice styling (gradient background, rounded corners).

### 9. Made It Non-Blocking

Problem: Creating mashup takes 2-5 minutes. Server would freeze.

Solution: Use threading
```python
thread = threading.Thread(target=process_mashup, args=(...))
thread.start()
return "Processing!" immediately
```

This lets the server respond right away while work happens in background.

### 10. Added Email Delivery

Used Python's email libraries:
1. Create ZIP file with the mashup
2. Build email with attachment
3. Send via Gmail's SMTP server

**Important:** Had to use "app password" not regular password.

## How the Workflow Works

```
User enters: Singer, Videos, Duration
         ↓
Search YouTube for videos
         ↓
Download N videos
         ↓
Convert each to MP3
         ↓
Cut first Y seconds from each
         ↓
Merge all segments
         ↓
Create ZIP file
         ↓
Email to user
```

## Challenges I Faced

### 1. FFmpeg Not Installed
**Problem:** Pydub needs FFmpeg to work
**Solution:** Added installation instructions in README

### 2. YouTube Keeps Changing
**Problem:** Old youtube-dl library stopped working
**Solution:** Switched to yt-dlp (actively maintained)

### 3. Email Authentication
**Problem:** Gmail blocks normal passwords
**Solution:** Created app-specific password guide

### 4. Template Not Found Error
**Problem:** Forgot Flask needs templates in specific folder
**Solution:** Created `templates/` folder, added index.html

### 5. Server Hanging
**Problem:** Long downloads blocked web server
**Solution:** Used background threads

## What I Learned

1. **Breaking down problems** - Started with CLI, then added web interface
2. **Library research** - Found right tools for each task
3. **Error handling** - Things fail, need to handle gracefully
4. **User experience** - Loading indicators, error messages matter
5. **Documentation** - Good docs save time answering questions

## Testing Process

Started small and built up:
```
Test 1: Download 1 video → Works?
Test 2: Convert to audio → Works?
Test 3: Cut audio → Works?
Test 4: Merge 2 files → Works?
Test 5: Try with 15 videos → Works?
Test 6: Add web interface → Works?
Test 7: Add email → Works?
```

## Files Created

**Main Programs:**
- `mashup.py` - Command line version (came first)
- `mashup_web.py` - Web version (built second)

**Supporting Files:**
- `templates/index.html` - Web interface
- `requirements.txt` - Dependencies list
- `verify_setup.py` - Check if everything installed
- Various README files - Instructions

## Time Breakdown

- Research & planning: 1 hour
- CLI version: 2 hours
- Web version: 2 hours
- Email setup: 1 hour
- Testing & debugging: 2 hours
- Documentation: 1 hour
- **Total: ~9 hours**

## If I Did This Again

Would do differently:
1. Set up virtual environment first
2. Write tests alongside code
3. Use environment variables from start for credentials
4. Add progress bar for downloads
5. Better error messages

Would keep same:
1. Building CLI before web
2. Using yt-dlp and pydub
3. Background threading approach

## Running the Final Product

**Command Line:**
```bash
python mashup.py "Arijit Singh" 15 30 output.mp3
```

**Web Interface:**
```bash
python mashup_web.py
# Go to http://localhost:5000
```

That's it! From concept to working product.