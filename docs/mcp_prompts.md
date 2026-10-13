# Blender MCP Prompts and Examples

This file collects production-ready prompts you can paste into Claude Desktop while the Blender MCP server is running. They assume the BlenderMCP addon is enabled and the MCP server is active.

## 1) Cinematic Side-Tracking Shot (Dolly Tracking Track)

Prompt:

"Create a 120-frame cinematic tracking shot focused on the selected object (or target 'HunyuanModel'). Perform the following steps via Blender Python API:

Add a curved NURBS path extending horizontally along the X-axis in front of the target to serve as a camera track.

Add an Anamorphic 50mm Camera with Depth of Field enabled, targeting the subject directly.

Attach the camera to the curve using a Follow Path constraint and set it to animate smoothly from Frame 1 to 120 using Bezier interpolation.

Add a Track To constraint so the camera rotates automatically to keep the subject framed during the side-sweeping motion.

Enable Motion Blur in render settings with a 0.5 shutter angle." 


## 2) Three-Point High-Contrast Studio Lighting Setup

Prompt:

"Build a dramatic Hollywood-style 3-point studio lighting setup around the center object at origin (0,0,0):

Key Light: Warm Area Light (5500K / #FFD1A4) placed 45° off-camera, power 1000W, size 2m for soft shadows.

Fill Light: Cool Area Light (7500K / #A4C8FF) on the opposite side, power 250W, size 4m to fill deep shadows gently.

Rim/Hair Light: Strong Spot Light ( power 1500W) placed behind the subject aimed at its back edge to create a bright outline separating it from the background.

Set render engine to Cycles, turn on GPU Compute, and enable Color Management with AgX / Medium High Contrast film look."


## 3) 360-Degree Orbital Reveal with Dynamic Side Motion

Prompt:

"Create an orbital camera animation around the main subject across 180 frames:

Add an Empty at coordinates (0, 0, 1) and name it 'Cam_Pivot'.

Add a 85mm Camera positioned at (0, -5, 1.5) facing the subject.

Parent the Camera to 'Cam_Pivot'.

Animate the Z-rotation of 'Cam_Pivot' from 0° at Frame 1 to 360° at Frame 180.

Animate the Z-location of 'Cam_Pivot' slightly upward from 1.0m to 2.2m to create a dynamic spiraling side-view effect.

Set keyframe interpolation to Linear for a seamless looping render."


## Cinematic Principles to include in prompts

- Camera Physics: focal length, depth of field, explicit focus target
- Side Motion Rigging: NURBS/Bezier path or Dolly rig + FOLLOW_PATH + TRACK_TO
- Lighting Proportions: 3-point ratio-based lighting, color temperatures, volumetric fog
- Rendering: choose Cycles for final-quality, EEVEE Next for real-time preview
