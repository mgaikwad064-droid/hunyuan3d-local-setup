import os
import bpy

def render_animation_with_checkpoints(file_format='OPENEXR', color_depth='32'):
    scene = bpy.context.scene
    
    # 1. Resolve and ensure output directory exists
    output_dir = bpy.path.abspath(scene.render.filepath)
    if not output_dir or output_dir == '//' or output_dir == '':
        output_dir = bpy.path.abspath("//render_checkpoints/")
        
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. Configure Multi-Pass EXR or PNG Settings
    scene.render.image_settings.file_format = file_format
    
    if file_format in ['OPENEXR', 'MULTILAYER']:
        scene.render.image_settings.color_depth = color_depth
        scene.render.image_settings.exr_codec = 'DWAA'  # High-efficiency lossy compression for EXR
        
        # Enable essential multi-passes for post-production compositing
        view_layer = bpy.context.view_layer
        view_layer.use_pass_combined = True
        view_layer.use_pass_z = True          # Depth / Z-pass for depth of field
        view_layer.use_pass_normal = True     # Normals for relighting
        view_layer.use_pass_diffuse_color = True
        view_layer.use_pass_glossy_color = True
    elif file_format == 'PNG':
        scene.render.image_settings.color_depth = '16'
        scene.render.image_settings.compression = 15
        
    start_frame = scene.frame_start
    end_frame = scene.frame_end
    
    print("==================================================")
    print(f"🎬 Starting Checkpoint-Resumed Render Pipeline")
    print(f"📁 Output Directory : {output_dir}")
    print(f"🎞️ Frame Range     : {start_frame} to {end_frame}")
    print(f"📦 Format          : {file_format} ({color_depth}-bit)")
    print("==================================================")
    
    # 3. Frame-by-frame loop with state checking
    for frame in range(start_frame, end_frame + 1):
        scene.frame_set(frame)
        
        # Determine standard frame filename (e.g., 0001.exr, 0001.png)
        ext = "exr" if file_format in ['OPENEXR', 'MULTILAYER'] else "png"
        frame_filename = f"{frame:04d}.{ext}"
        file_path = os.path.join(output_dir, frame_filename)
        
        # Checkpoint Validation: Skip if file already exists and is non-empty
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
            print(f"[RESUME] Frame {frame:04d} already rendered. Skipping...")
            continue
            
        print(f"[RENDER] Processing Frame {frame:04d} / {end_frame}...")
        
        # Temporarily override render filepath to point directly to the individual frame file
        scene.render.filepath = file_path
        
        # Render and save the single frame
        bpy.ops.render.render(write_still=True)
        
    print("==================================================")
    print("🎉 Render Complete! All missing frames processed.")
    print("==================================================")

# Execute the checkpoint renderer (Defaults to OpenEXR 32-bit Float Multi-Pass)
if __name__ == '__main__':
    render_animation_with_checkpoints(file_format='OPENEXR', color_depth='32')
