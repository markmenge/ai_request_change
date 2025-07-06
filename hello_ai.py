# hello_ai.py
# pip install tk openai-whisper sounddevice numpy

import tkinter as tk
from agentic_code_generator import ACG

acg = ACG()

def type_input():
    acg.request_change(__file__, use_voice=False)

def speech_input():
    acg.request_change(__file__, use_voice=True)

def main():
    root = tk.Tk()
    root.title(f"File: {__file__}")
    root.geometry("800x600")
    tk.Label(root, text="Hello, World!", font=("Arial", 16)).pack(pady=10)

    # Typed input button
    tk.Button(
        root,
        text="📝 Type Request",
        command=type_input
    ).pack(pady=5)

    # Speech input button
    tk.Button(
        root,
        text="🎙 Speech Input",
        command=speech_input
    ).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
