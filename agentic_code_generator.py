# agentic_code_generator.py
# pip install openai tk openai-whisper sounddevice numpy scipy
import os
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import simpledialog
from openai import OpenAI
import ast

import sounddevice as sd
import numpy as np
import whisper
import scipy.io.wavfile
import importlib.metadata as md, shutil, sys, os
import importlib.metadata as _imd
import re  # stdlib; no pip install required

if tuple(map(int, md.version("openai").split(".")[:2])) < (1, 0):
    sys.exit("OpenAI client < 1.0 detected. Run: pip install -U 'openai>=1.3.0'")
if shutil.which("ffmpeg") is None:
    sys.exit("FFmpeg not found. Install it or add to PATH before running.")

'''
# Agentic Code Generator (ACG) - Overview
# --------------------------------------

Purpose:
    Allow the user to tell the program to change itself.
    
Demo
    - python.exe hello_world.py
    - Push Type Change button. Enter "add a button to 3d plot z = sine of x plus cosine of y."
    - Launches hello_world_v1.py. The next file name will be hello_world_v2.py etc.

Usage Example:
    acg = ACG()
    acg.request_change(__file__, use_voice=False)   # type the change you want
    acg.request_change(__file__, use_voice=True)    # speak the change you want

Notes:
    - Whisper model is loaded only when needed
    - Code is safe for use inside self-modifying tools
    - Logs and changelogs can be added easily
'''

class ACG:
    def __init__(self, api_key=None, model="gpt-4", whisper_model="base"):
        """
        Initialize the Agentic Code Generator.

        :param api_key: Optional OpenAI API key. Uses OPENAI_API_KEY env var if None.
        :param model: GPT model name.
        :param whisper_model: Whisper model name ("tiny", "base", "small", etc.).
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.whisper = whisper.load_model(whisper_model)

    def request_change(self, caller_script: str, use_voice=False, record_time=10):
        """
        Request a code change from GPT-4 based on user input.

        :param caller_script: The current script file path.
        :param use_voice: Whether to use Whisper voice input.
        :param record_time: Duration (in seconds) for the Whisper voice recording. Default is 10 seconds.
        """
        request_text = (
            self._record_and_transcribe(record_time=record_time) if use_voice else self._get_user_request()
        )
        if not request_text:
            return

        original_code = self._read_code(caller_script)
        modified_code = self._generate_modified_code(original_code, request_text)
        if not modified_code:
            return

        new_script_path = self._save_new_version(caller_script, modified_code)
        self._launch_new_script(new_script_path)

    def _get_user_request(self) -> str:
        """
        Prompt user for a change request via a popup text box.
        """
        root = tk.Tk()
        root.withdraw()
        request = simpledialog.askstring("ACG Request", "Describe the code change:")
        root.destroy()
        return request.strip() if request else ""

    def _record_and_transcribe(self, record_time=10, samplerate=16000) -> str:
        """
        Record user's voice and transcribe it using Whisper.

        :param seconds: Duration of recording.
        :param samplerate: Audio sample rate.
        :return: Transcribed string.
        """
        print(f"🎙️ Recording {record_time} seconds...")
        audio = sd.rec(int(record_time * samplerate), samplerate=samplerate, channels=1, dtype="float32")
        sd.wait()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            path = tmp.name
            scipy.io.wavfile.write(path, samplerate, (audio * 32767).astype(np.int16))

        print("🧠 Transcribing with Whisper...")
        result = self.whisper.transcribe(path)
        print(f"📝 Transcribed: {result['text']}")
        return result["text"]

    def _read_code(self, filepath: str) -> str:
        """
        Read the full contents of a code file and verify it is valid Python syntax.

        :param filepath: Path to the script file.
        :raises SyntaxError: If the code is not valid Python.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        try:
            ast.parse(code, filename=filepath)
        except SyntaxError as e:
            print(f"Syntax error in {filepath}: {e}")
            raise
        return code

    def _generate_modified_code(self, original_code: str, request: str) -> str:
        """
        Call OpenAI to modify the code according to the request.

        :param original_code: The source Python code.
        :param request: User's natural language request.
        :return: New modified code.
        """
        prompt = f"""You are an expert Python developer. A user provided the following code and wants it changed.

--- ORIGINAL CODE ---
{original_code}

--- USER REQUEST ---
{request}

--- INSTRUCTIONS ---
Rewrite the full Python script to reflect the request. Return code only — no comments or markdown. Keep the Type Request and Speech Input buttons if possible.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI request failed: {e}")
            return None

    @staticmethod                    # ⬅️  add this line
    def next_version(fname: str) -> str:
        """
        Return fname with its _v<number> incremented, or _v1 added.
        Examples:
            hello_world.py     -> hello_world_v1.py
            hello_world_v2.py  -> hello_world_v3.py
            hello_world_v99.py -> hello_world_v100.py
        """
        base, dot, ext = fname.partition(".")
        match = re.search(r"_v(\d+)$", base)
        if match:
            num = int(match.group(1)) + 1
            new_base = f"{base[:match.start(1)]}{num}"
        else:
            new_base = f"{base}_v1"
        return f"{new_base}{dot}{ext}"
    
    def _save_new_version(self, base_path: str, modified_code: str) -> str:
        """
        Save a modified version of the script to a new versioned filename.

        :param base_path: Original script path.
        :param modified_code: The updated code from GPT.
        :return: Path to the new versioned file.
        """
        candidate = self.next_version(base_path)
        with open(candidate, "w", encoding="utf-8") as f:
            f.write(modified_code)
        print(f"✅ Saved new version: {candidate}")
        return candidate

    def _launch_new_script(self, path: str):
        """
        Launch a new Python script as a detached process that runs independently.
        Works reliably from CLI or GUI, and survives parent exit.
        """
        kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
            "close_fds": True
        }

        if sys.platform == "win32":
            # DETACHED_PROCESS = 0x00000008
            kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            # On Unix, start new session
            kwargs["start_new_session"] = True

        subprocess.Popen([sys.executable, path], **kwargs)
