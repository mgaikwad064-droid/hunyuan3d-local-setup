import os
import subprocess
import sys

def encode_adaptive_hls(
    input_video_path: str,
    output_dir: str = "./hls_stream",
    segment_duration: int = 6
):
    """
    Encodes a master video into an adaptive multi-bitrate HLS package (.m3u8)
    containing 1080p, 720p, and 480p variant streams with a master playlist.
    """
    if not os.path.exists(input_video_path):
        print(f"[ERROR] Input video not found: {input_video_path}")
        sys.exit(1)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎬 Starting multi-bitrate HLS packaging...")
    print(f"   - Input File  : {os.path.abspath(input_video_path)}")
    print(f"   - Output Dir  : {os.path.abspath(output_dir)}")

    # Define path for the master playlist
    master_playlist = os.path.join(output_dir, "master.m3u8")

    # Construct the advanced single-pass FFmpeg HLS command
    # -filter_complex : Scales input video into 3 distinct resolutions (1080p, 720p, 480p)
    # -var_stream_map : Maps video renditions and audio streams to respective variant playlists
    # -hls_time       : Duration of each media segment in seconds (default: 6s)
    # -hls_playlist_type vod : Video on Demand configuration for static archives
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video_path,
        "-filter_complex",
        (
            "[0:v]scale=w=1920:h=1080:flags=bicubic[v1080];"
            "[0:v]scale=w=1280:h=720:flags=bicubic[v720];"
            "[0:v]scale=w=854:h=480:flags=bicubic[v480]"
        ),
        # 1080p Stream Mapping & Encoding Settings
        "-map", "[v1080]", "-c:v:0", "libx264", "-b:v:0", "5000k", "-maxrate:v:0", "5350k", "-bufsize:v:0", "7500k", "-preset", "slow",
        # 720p Stream Mapping & Encoding Settings
        "-map", "[v720]", "-c:v:1", "libx264", "-b:v:1", "2800k", "-maxrate:v:1", "2996k", "-bufsize:v:1", "4200k", "-preset", "slow",
        # 480p Stream Mapping & Encoding Settings
        "-map", "[v480]", "-c:v:2", "libx264", "-b:v:2", "1400k", "-maxrate:v:2", "1498k", "-bufsize:v:2", "2100k", "-preset", "slow",
        # Audio Stream Mapping & Encoding Settings (duplicated across variants)
        "-map", "0:a", "-c:a:0", "aac", "-b:a:0", "192k", "-ac", "2",
        "-map", "0:a", "-c:a:1", "aac", "-b:a:1", "128k", "-ac", "2",
        "-map", "0:a", "-c:a:2", "aac", "-b:a:2", "96k", "-ac", "2",
        # HLS Multiplexer Settings
        "-f", "hls",
        "-hls_time", str(segment_duration),
        "-hls_playlist_type", "vod",
        "-hls_flags", "independent_segments",
        "-master_pl_name", "master.m3u8",
        "-var_stream_map", "v:0,a:0 v:1,a:1 v:2,a:2",
        os.path.join(output_dir, "stream_%v.m3u8")
    ]

    print("🚀 Executing FFmpeg adaptive HLS encoding command...")
    print("--------------------------------------------------")

    try:
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        for line in process.stdout:
            print(line, end='')

        process.wait()

        if process.returncode == 0:
            print("--------------------------------------------------")
            print(f"🎉 Success! Adaptive HLS package generated successfully.")
            print(f"📂 Master Playlist: {os.path.abspath(master_playlist)}")
        else:
            print(f"[ERROR] FFmpeg failed with exit code {process.returncode}")

    except FileNotFoundError:
        print("[ERROR] FFmpeg is not installed or not found in your system PATH.")

if __name__ == "__main__":
    # Point to your master video file (ProRes or high-res MP4)
    INPUT_MASTER = "./output_master_tagged_4k.mov"
    HLS_OUTPUT_DIRECTORY = "./hls_streaming_package"

    encode_adaptive_hls(
        input_video_path=INPUT_MASTER,
        output_dir=HLS_OUTPUT_DIRECTORY,
        segment_duration=6  # 6-second chunk duration standard for web streaming
    )
