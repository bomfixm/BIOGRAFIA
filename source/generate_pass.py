"""Compatibility entry point for the current pastel pass renderer.

Requires Node.js, @napi-rs/canvas and FFmpeg. The approved artwork is in pass-art.png.
"""
import os
from pathlib import Path
import subprocess

if __name__ == '__main__':
    node = os.environ.get('CODEX_PRIMARY_RUNTIME_NODE', 'node')
    subprocess.run([node, str(Path(__file__).with_name('render_pass.mjs'))], check=True)
