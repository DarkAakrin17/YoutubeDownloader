import os
import streamlit as st
from yt_dlp import YoutubeDL

# ------------------- Setup -------------------
st.set_page_config(page_title="🎬 YouTube Downloader",
                   page_icon="🎧", layout="centered")
st.title("🎥 YouTube Downloader with Progress Bar")
st.write("Download YouTube **audio**, **video**, or **entire playlists** easily with automatic merging and progress tracking.")

# Downloads folder
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ------------------- Progress Hook -------------------


def progress_hook(d):
    """Update Streamlit progress bar."""
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)
        if total_bytes:
            percent = downloaded_bytes / total_bytes
            progress_bar.progress(percent)
            percent_text.text(
                f"⏳ Downloading: {percent * 100:.1f}% "
                f"({downloaded_bytes / (1024 * 1024):.2f}MB / {total_bytes / (1024 * 1024):.2f}MB)"
            )
    elif d['status'] == 'finished':
        progress_bar.progress(1.0)
        percent_text.text("✅ Download complete! Processing file...")

# ------------------- Download Function -------------------


def download_youtube_content(url, choice, is_playlist):
    try:
        outtmpl = os.path.join(
            DOWNLOAD_DIR,
            '%(playlist_title)s/%(title)s.%(ext)s' if is_playlist else '%(title)s.%(ext)s'
        )

        ydl_opts = {
            'outtmpl': outtmpl,
            'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # Adjust if needed
            'ignoreerrors': True,
            'merge_output_format': 'mp4',  # Merge video+audio
            'noprogress': False,
            'continuedl': True,
            'nopart': True,                 # ✅ Prevent leftover .part files
            'windowsfilenames': True,
            'progress_hooks': [progress_hook],
            'concurrent_fragment_downloads': 5,
            'quiet': False
        }

        if choice == "Audio (MP3)":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif choice == "Video Only (no audio)":
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]',
            })
        elif choice == "Video with Audio (MP4)":
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',
            })

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        st.success(f"✅ Download completed!\nFiles saved in: `{DOWNLOAD_DIR}`")

    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")


# ------------------- Streamlit UI -------------------
youtube_url = st.text_input("🔗 Enter YouTube video or playlist URL:")

col1, col2 = st.columns(2)
with col1:
    choice = st.selectbox(
        "🎧 Select download type:",
        ["Audio (MP3)", "Video Only (no audio)", "Video with Audio (MP4)"]
    )
with col2:
    is_playlist = st.checkbox("📜 Is this a playlist?", value=False)

st.write("---")

if st.button("⬇️ Start Download"):
    if not youtube_url.strip():
        st.warning("⚠️ Please enter a valid YouTube URL.")
    else:
        progress_bar = st.progress(0)
        percent_text = st.empty()
        download_youtube_content(youtube_url.strip(), choice, is_playlist)
