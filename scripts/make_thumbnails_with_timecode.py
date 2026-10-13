import os
import subprocess
import sys
import json

def get_video_duration(video_path: str) -> float:
    """Uses ffprobe to extract the exact duration of the video in seconds."""
    ffprobe_cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        video_path
    ]
    try:
        result = subprocess.run(
            ffprobe_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True, 
            check=True
        )
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception as e:
        print(f"[ERROR] Could not retrieve video duration: {e}")
        sys.exit(1)

def generate_contact_sheet_with_timecode(
    video_path: str,
    output_image_path: str = "video_contact_sheet_tc.jpg",
    grid_cols: int = 4,
    grid_rows: int = 4,
    thumb_width: int = 480
):
    """
    Generates a grid contact sheet image with burned-in timecode labels on each tile.
    """
    if not os.path.exists(video_path):
        print(f"[ERROR] Video file not found: {video_path}")
        sys.exit(1)

    print(f"🎬 Analyzing video for timecode-stamped extraction: {video_path}")
    duration = get_video_duration(video_path)
    
    total_frames_in_grid = grid_cols * grid_rows
    print(f"   - Video Duration : {duration:.2f} seconds")
    print(f"   - Grid Layout    : {grid_cols}x{grid_rows} ({total_frames_in_grid} total tiles)")

    # Calculate exact sampling frame rate to spread thumbnails evenly across duration
    sampling_fps = total_frames_in_grid / duration

    # Construct the advanced FFmpeg video filter chain:
    # 1. fps=...           : Samples frames at calculated intervals
    # 2. scale=W:-1        : Resizes each thumbnail maintaining aspect ratio
    # 3. drawtext=...      : Burns the presentation timestamp (pts) as HH:MM:SS onto each tile
    # 4. tile=COLSxROWS    : Stitches stamped frames into a grid
    # NOTE: Double curly braces {{ and }} are used to escape Python f-string syntax for FFmpeg.
    
    video_filter_chain = (
        f"fps={sampling_fps},"
        f"scale={thumb_width}:-1,"
        f"drawtext=text='{{{{pts\\:hms}}}}':fontcolor=white:fontsize=24:"
        f"box=1:boxcolor=black@0.65:boxborderw=6:x=15:y=15,"
        f"tile={grid_cols}x{grid_rows}"
    )

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", video_filter_chain,
        "-frames:v", "1",  # Output a single combined image frame
        output_image_path
    ]

    print("🚀 Generating timecode contact sheet image...")
    print("--------------------------------------------------")

    try:
        process = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if process.returncode == 0:
            print("--------------------------------------------------")
            print(f"🎉 Success! Timecode contact sheet saved to: {os.path.abspath(output_image_path)}")
        else:
            print(f"[ERROR] FFmpeg failed: {process.stderr}")
            
    except FileNotFoundError:
        print("[ERROR] FFmpeg is not installed or not found in your system PATH.")

if __name__ == "__main__":
    # Point to your rendered master file
    TARGET_VIDEO = "./output_master_tagged_4k.mov"
    OUTPUT_SHEET = "./video_contact_sheet_timecode.jpg"
    
    generate_contact_sheet_with_timecode(
        video_path=TARGET_VIDEO,
        output_image_path=OUTPUT_SHEET,
        grid_cols=4,      # 4 columns
        grid_rows=4,      # 4 rows (Total 16 timecode-labeled tiles)
        thumb_width=480   # Thumbnail width in pixels
    )
