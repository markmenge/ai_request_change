# Self-Modifying Program via ACG

### Purpose  
Allow the user to ask the program to change itself.

### Requirements
You need a ChatGPT OpenAI key

### Demo (GUI Version)
```
python.exe hello_world.py
```
- Click the **Type Change** button.  
- Enter: `"add a button to 3d plot z = sine of x plus cosine of y."`  
- A new file with a version number will be created and run. For example: `hello_world_v1.py`. The next version will be `hello_world_v2.py`, and so on.
- If you like an older version, then close the newer versions, and improve upon that old version.

### Example API Usage
```python
import agentic_code_generator
acg = ACG()
acg.request_change(__file__, use_voice=False)  # User types the changes they want for this program
acg.request_change(__file__, use_voice=True)   # User speaks into the microphone to request changes
```

### Notes
- The Whisper model (for speech-to-text) is loaded only when needed.

### Setup
```
1. Set the OPENAI_API_KEY environment variable. Example:
SET OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
2. pip install tk openai-whisper sounddevice numpy
3. winget install ffmpeg
```
