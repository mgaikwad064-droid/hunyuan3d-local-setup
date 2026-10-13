import os
import subprocess
import sys
import glob

def stitch_exr_with_fades_and_audio(
    input_dir: str, 
    output_video_path: str, 
    audio_path: str = None,
    fps: int = 24, 
    prores_profile: int = 3,
    fade_in_sec: float = 2.0,
    fade_out_sec: float = 2.0
):
    
    if not os.path.exists(input_dir):
        print(f"[ERROR] Input directory '{input_dir}' does not exist.")
        sys.exit(1)
        
    exr_files = sorted(glob.glob(os.path.join(input_dir, "*.exr")))
    if not exr_files:
        print(f"[ERROR] No .exr files found in '{input_dir}'.")
        sys.exit(1)
        
    total_frames = len(exr_files)
    total_duration = total_frames / fps
    print(f"📁 Found {total_frames} EXR frames. Total duration at {fps} fps: {total_duration:.2f} seconds.")
    
    first_file = os.path.basename(exr_files[0])
    base_name, _ = os.path.splitext(first_file)
    
    if base_name.isdigit():
        padding_len = len(base_name)
        input_pattern = os.path.join(input_dir, f"%0{padding_len}d.exr")
        start_number = int(base_name)
    else:
        prefix = ''.join([c for c in base_name if not c.isdigit()])
        input_pattern = os.path.join(input_dir, f"{prefix}%04d.exr")
        start_number = 1

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-framerate", str(fps),
        "-start_number", str(start_number),
        "-i", input_pattern
    ]

    has_audio = False
    if audio_path and os.path.exists(audio_path):
        print(f"🎵 Merging audio track: {audio_path}")
        ffmpeg_cmd.extend(["-i", audio_path])
        has_audio = True
    elif audio_path:
        print(f"[WARNING] Audio file '{audio_path}' not found. Proceeding with video only.")

    ffmpeg_cmd.extend([
        "-vf", "colorspace=iall=bt709:all=bt709,format=yuv422p10le",
        "-c:v", "prores_ks",
        "-profile:v", str(prores_profile),
        "-pix_fmt", "yuv422p10le"
    ])

    if has_audio:
        fade_out_start = max(0.0, total_duration - fade_out_sec)
        audio_filter = f"afade=t=in:st=0:d={fade_in_sec},afade=t=out:st={fade_out_start}:d={fade_out_sec}"
        
        print(f"🎚️ Applying Audio Fades -> Fade-in: {fade_in_sec}s | Fade-out starts at: {fade_out_start:.2f}s (Duration: {fade_out_sec}s)")
        
        ffmpeg_cmd.extend([
            "-af", audio_filter,
            "-c:a", "pcm_s24le",
            "-shortest"
        ])

    ffmpeg_cmd.append(output_video_path)

    print("🚀 Executing FFmpeg command...")
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
            print(f"🎉 Success! Final master saved to: {output_video_path}")
        else:
            print(f"[ERROR] FFmpeg failed with exit code {process.returncode}")
            
    except FileNotFoundError:
        print("[ERROR] FFmpeg is not installed or not found in your system PATH.")


if __name__ == "__main__":
    RENDER_DIR = "./render_checkpoints/"
    AUDIO_FILE = "./assets/background_score.wav"
    OUTPUT_FILE = "./output_master_4k_faded.mov"
    
    stitch_exr_with_fades_and_audio(
        input_dir=RENDER_DIR,
        output_video_path=OUTPUT_FILE,
        audio_path=AUDIO_FILE,
        fps=24,
        prores_profile=3,
        fade_in_sec=2.0,
        fade_out_sec=3.0
    )
