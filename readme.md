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
    - Whisper model for TTS is loaded only when needed

