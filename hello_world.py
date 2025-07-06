# hello_world.py
# pip install tk openai-whisper sounddevice numpy openai

import tkinter as tk
from agentic_code_generator import ACG

acg = ACG()

print("\n\rHello world!!!\n")
acg.request_change(__file__, use_voice=False)
