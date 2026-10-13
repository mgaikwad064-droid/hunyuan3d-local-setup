import os
import subprocess
import sys
import glob
import json
import re
from datetime import datetime

def analyze_audio_loudness(audio_path: str, target_lufs: float = -23.0, log_file_path: str = "audio_qc_audit_report.txt") -> dict:
    """
    Pass 1: Runs an analysis pass on the audio file to extract exact EBU R128 metrics,
    prints them, and saves a formatted JSON audit report to disk.
    """
    print(f"📊 [Pass 1/2] Analyzing audio file for broadcast compliance: {audio_path}")
    
    null_dest = "NUL" if os.name == "nt" else "/dev/null"
    
    analysis_cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-af", f"loudnorm=I={target_lufs}:TP=-2.0:LRA=7.0:print_format=json",
        "-f", "null", null_dest
    ]
    
    process = subprocess.run(
        analysis_cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True
    )
    
    if process.returncode != 0:
        print(f"[ERROR] Audio analysis failed: {process.stderr}")
        sys.exit(1)
        
    stderr_output = process.stderr
    json_match = re.search(r'(\{[\s\S]*"input_i"[\s\S]*\})', stderr_output)
    
    if not json_match:
        print("[ERROR] Could not parse JSON loudness metrics from FFmpeg output.")
        sys.exit(1)
        
    try:
        metrics = json.loads(json_match.group(1))
        
        qc_report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_audio_file": os.path.abspath(audio_path),
            "target_standard": f"EBU R128 ({target_lufs} LUFS)",
            "measured_metrics": metrics
        }
        
        with open(log_file_path, "w", encoding="utf-8") as f:
            json.dump(qc_report, f, indent=4)
            
        print("✅ Audio Analysis Complete. Metrics saved to audit log:")
        print(f"   📁 Audit Log Path       : {os.path.abspath(log_file_path)}")
        print(f"   - Input Integrated LUFS : {metrics['input_i']}")
        print(f"   - Input True Peak       : {metrics['input_tp']} dBTP")
        print(f"   - Input Loudness Range  : {metrics['input_lra']} LU")
        
        return metrics
    except Exception as e:
        print(f"[ERROR] Failed to process or write JSON loudness metrics: {e}")
        sys.exit(1)

def stitch_exr_with_metadata(
    input_dir: str, 
    output_video_path: str, 
    audio_path: str = None,
    fps: int = 24, 
    prores_profile: int = 3,
    target_lufs: float = -23.0,
    fade_in_sec: float = 2.0,
    fade_out_sec: float = 3.0,
    audit_log_path: str = "audio_qc_audit_report.txt",
    meta_title: str = "3D Cinematic Master",
    meta_author: str = "Independent Creator",
    meta_copyright: str = "2026 All Rights Reserved"
):
    """
    Pass 2: Combines 4K EXR frames, applies certified loudnorm, audio fades, looping,
    embeds container metadata tags, and exports to ProRes 422 HQ.
    """
    
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

    audio_filter_string = ""
    has_audio = False
    
    if audio_path and os.path.exists(audio_path):
        has_audio = True
        metrics = analyze_audio_loudness(audio_path, target_lufs, audit_log_path)
        
        fade_out_start = max(0.0, total_duration - fade_out_sec)
        
        loudnorm_pass2 = (
            f"loudnorm=I={target_lufs}:TP=-2.0:LRA=7.0:"
            f"measured_I={metrics['input_i']}:"
            f"measured_TP={metrics['input_tp']}:"
            f"measured_LRA={metrics['input_lra']}:"
            f"measured_thresh={metrics['input_thresh']}:"
            f"offset={metrics['target_offset']}:"
            f"linear=true:print_format=summary"
        )
        
        audio_filter_string = f"{loudnorm_pass2},afade=t=in:st=0:d={fade_in_sec},afade=t=out:st={fade_out_start}:d={fade_out_sec}"
    elif audio_path:
        print(f"[WARNING] Audio file '{audio_path}' not found. Proceeding with video only.")

    print("🚀 [Pass 2/2] Rendering master 4K ProRes file with metadata tags...")
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-framerate", str(fps),
        "-start_number", str(start_number),
        "-i", input_pattern
    ]

    if has_audio:
        ffmpeg_cmd.extend(["-stream_loop", "-1", "-i", audio_path])

    # Video filters & ProRes encoding parameters
    ffmpeg_cmd.extend([
        "-vf", "colorspace=iall=bt709:all=bt709,format=yuv422p10le",
        "-c:v", "prores_ks",
        "-profile:v", str(prores_profile),
        "-pix_fmt", "yuv422p10le"
    ])

    # Audio filters & muxing
    if has_audio:
        ffmpeg_cmd.extend([
            "-af", audio_filter_string,
            "-c:a", "pcm_s24le",
            "-shortest"
        ])

    # --- METADATA TAG INJECTION ---
    # QuickTime (.mov) container metadata keys
    ffmpeg_cmd.extend([
        "-metadata", f"title={meta_title}",
        "-metadata", f"artist={meta_author}",       # QuickTime maps 'artist' to Author/Creator
        "-metadata", f"copyright={meta_copyright}",
        "-metadata", f"creation_time={datetime.utcnow().isoformat()}Z"
    ])

    ffmpeg_cmd.append(output_video_path)
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
            print(f"🎉 Success! Tagged master exported to: {output_video_path}")
            print(f"🏷️ Metadata Embedded -> Title: '{meta_title}' | Author: '{meta_author}'")
        else:
            print(f"[ERROR] FFmpeg failed with exit code {process.returncode}")
            
    except FileNotFoundError:
        print("[ERROR] FFmpeg is not installed or not found in your system PATH.")

if __name__ == "__main__":
    RENDER_DIR = "./render_checkpoints/"
    AUDIO_FILE = "./assets/background_score.wav"
    OUTPUT_FILE = "./output_master_tagged_4k.mov"
    AUDIT_LOG = "./audio_qc_audit_report.txt"
    
    stitch_exr_with_metadata(
        input_dir=RENDER_DIR,
        output_video_path=OUTPUT_FILE,
        audio_path=AUDIO_FILE,
        fps=24,
        prores_profile=3,
        target_lufs=-23.0,
        fade_in_sec=2.0,
        fade_out_sec=3.0,
        audit_log_path=AUDIT_LOG,
        meta_title="Cyber Security Handbook 3D Teaser",
        meta_author="Rishikesh Rajendrakumar Gaaikwad",
        meta_copyright="2026 Rishikesh Rajendrakumar Gaaikwad. All Rights Reserved."
    )
