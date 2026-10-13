# Hunyuan3D Local Setup + Blender MCP Integration

This repository collects local setup instructions, Blender MCP integration tips, MCP prompts for cinematic shots, and production-ready utility scripts for rendering, resumption, and post-processing (EXR -> ProRes, audio processing, loudness normalization).

Contents
- README.md — this overview
- docs/mcp_prompts.md — curated MCP prompts for camera rigs, lighting, and rendering
- scripts/blender_render_optim.py — Blender Cycles / EEVEE optimization script
- scripts/checkpoint_renderer.py — checkpoint-resumed frame-by-frame renderer for Blender
- scripts/stitch_exr.py — stitch EXR sequence into 4K ProRes using FFmpeg
- scripts/stitch_exr_with_audio.py — stitch EXR + merge audio track
- scripts/stitch_exr_with_fades_and_audio.py — audio fades + stitch
- scripts/stitch_exr_with_master_audio.py — audio looping + loudness normalization
- scripts/stitch_exr_broadcast_loudnorm.py — two-pass loudnorm broadcast-compliant workflow

Usage
Read the docs and inspect the scripts in `scripts/`. Each script includes a `__main__` example and is intended to be run from the project root. Adjust paths and parameters to your environment.

License
MIT
