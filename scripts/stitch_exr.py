import os
import subprocess
import sys
import glob

def stitch_exr_sequence_to_prores(
    input_dir: str, 
    output_video_path: str, 
    fps: int = 24, 
    prores_profile: int = 3
):
    """
    Stitches a folder of EXR frames into a 4K Apple ProRes video file using FFmpeg.
    """
    
    if not os.path.exists(input_dir):
        print(f"[ERROR] Input directory '{input_dir}' does not exist.")
        sys.exit(1)
        
    exr_files = sorted(glob.glob(os.path.join(input_dir, "*.exr")))
    if not exr_files:
        print(f"[ERROR] No .exr files found in '{input_dir}'.")
        sys.exit(1)
        
    print(f"📁 Found {len(exr_files)} EXR frames in {input_dir}.")
    
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
        "-i", input_pattern,
        "-vf", "colorspace=iall=bt709:all=bt709,format=yuv422p10le",
        "-c:v", "prores_ks",
        "-profile:v", str(prores_profile),
        "-pix_fmt", "yuv422p10le",
        output_video_path
    ]

    print("🚀 Executing FFmpeg encoding command...")
    print(" ".join(ffmpeg_cmd))
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
            print(f"🎉 Success! Video exported to: {output_video_path}")
        else:
            print(f"[ERROR] FFmpeg failed with exit code {process.returncode}")
            
    except FileNotFoundError:
        print("[ERROR] FFmpeg is not installed or not found in your system PATH.")


if __name__ == "__main__":
    RENDER_DIR = "./render_checkpoints/"
    OUTPUT_FILE = "./output_master_4k.mov"
    
    stitch_exr_sequence_to_prores(
        input_dir=RENDER_DIR,
        output_video_path=OUTPUT_FILE,
        fps=24,
        prores_profile=3  # 3 = ProRes 422 HQ
    )
