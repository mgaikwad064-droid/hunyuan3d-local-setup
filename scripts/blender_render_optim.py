import bpy

scene = bpy.context.scene

# 1. 4K Resolution & Framerate Setup
scene.render.resolution_x = 3840
scene.render.resolution_y = 2160
scene.render.resolution_percentage = 100
scene.render.fps = 24

# 2. Output Encoding (FFmpeg MP4 / H.264)
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'

# 3. Modern Cinematic Color Management (AgX)
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'High Contrast'

# 4. CYCLES ENGINE OPTIMIZATIONS (For Ray-Traced Realism + Speed)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'

# Smart Sampling & AI Denoising
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.08  # Stops tracing pixels once clean
scene.cycles.samples = 150              # Low sample ceiling balanced by denoiser
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'         # Use 'OPENIMAGEDENOISE' for non-NVIDIA GPUs

# Animation Acceleration
scene.render.use_persistent_data = True  # Caches geometry/textures between frames to slash prep time

# Light Path Trimming (Saves render time with minimal visual difference)
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4
scene.cycles.transmission_bounces = 8
