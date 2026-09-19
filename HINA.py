import re
import asyncio
import edge_tts
import datetime
import time
import random
import os
import uuid
import tkinter as tk
import psutil
import keyboard
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# FIX: Pygame naturally corrupts MP3 playback if the sample rate doesn't match.
pygame.mixer.init(frequency=24000, buffer=2048)

# Switching to Emily (Irish) - This is the EXACT accent of F.R.I.D.A.Y. in the Iron Man movies!
VOICE = "en-IE-EmilyNeural"

async def generate_and_play(text):
    # Clean text so she doesn't read out Python code literally
    speech_text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    speech_text = speech_text.replace('*', '').replace('#', '').strip()
    
    if not speech_text:
        return
        
    # Apply standard TTS voice
    communicate = edge_tts.Communicate(speech_text, VOICE)
    filename = f"temp_swarm_{uuid.uuid4().hex}.mp3"
    await communicate.save(filename)
    
    sound = pygame.mixer.Sound(filename)
    
    # MAIN VOICE (No Reverb)
    channel1 = pygame.mixer.Channel(0)
    channel1.set_volume(1.0)
    channel1.play(sound)
    
    root = tk.Tk()
    root.overrideredirect(True) 
    root.attributes("-topmost", True) 
    root.attributes("-alpha", 0.75) 
    root.configure(bg='#0a0a0a') 
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    popup_width = 340
    popup_height = 90
    x = screen_width - popup_width - 20
    y = screen_height - popup_height - 60 
    
    root.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
    
    title_lbl = tk.Label(root, text="H.I.N.A.", font=("Segoe UI", 11, "bold"), fg="#00e6e6", bg="#0a0a0a", anchor="w")
    title_lbl.pack(fill="x", padx=15, pady=(10, 2))
    
    msg_lbl = tk.Label(root, text=text, font=("Segoe UI", 10), fg="white", bg="#0a0a0a", wraplength=310, justify="left", anchor="w")
    msg_lbl.pack(fill="both", padx=15, pady=0)
    
    def check_audio():
        if channel1.get_busy():
            root.after(100, check_audio)
        else:
            root.after(1000, root.destroy) 
            
    root.after(100, check_audio)
    root.mainloop() 
    
    try:
        os.remove(filename)
    except:
        pass

def speak(text):
    try:
        asyncio.run(generate_and_play(text))
    except Exception as e:
        pass # Ignore thread collisions

def time_based_greeting():
    hour = datetime.datetime.now().hour
    
    mornings = [
        "Good morning Boss! You're up! Are we going to do some fun coding today? I'm ready when you are.",
        "Morning Boss. Systems are online. I hope you slept well.",
        "Good morning Boss. Let's make today a great day, okay?"
    ]
    afternoons = [
        "Hey Boss! It's afternoon. Have you eaten anything yet? Let's get back to work!",
        "Good afternoon Boss. I'm right here if you need anything.",
        "Boss, it's the middle of the day. Remember to take a screen break soon."
    ]
    evenings = [
        "Hi Boss! It's getting late. You worked so hard today. Want to just relax a bit with me?",
        "Good evening Boss. You did great today.",
        "Evening Boss. I love watching you work, but don't push yourself too hard."
    ]
    nights = [
        "Boss... it's so late! My eyes are getting heavy. Why are you still staring at the screen? Please go to sleep soon, okay?",
        "Boss, it's the middle of the night. Humans need sleep, you know.",
        "Boss, you need to go to bed. It is way too late!"
    ]
    
    if 5 <= hour < 12:
        speak(random.choice(mornings))
    elif 12 <= hour < 18:
        speak(random.choice(afternoons))
    elif 18 <= hour < 23:
        speak(random.choice(evenings))
    else:
        speak(random.choice(nights))

last_battery_state = None

def check_battery():
    global last_battery_state
    battery = psutil.sensors_battery()
    
    if not battery:
        return
        
    percent = battery.percent
    plugged = battery.power_plugged
    
    # Initialize the state on first run
    if last_battery_state is None:
        last_battery_state = {"percent": percent, "plugged": plugged}
        return

    # Check for state changes to trigger alerts once
    if plugged != last_battery_state["plugged"]:
        if plugged:
            speak("Thank you for plugging me in, Boss. I feel much better now.")
        else:
            speak("You unplugged me, Boss. Make sure I don't run out of energy.")
            
    elif plugged:
        # Charging milestones
        if percent >= 80 and last_battery_state["percent"] < 80:
            speak("Boss, I'm almost full! Just a little bit more to go.")
        elif percent == 100 and last_battery_state["percent"] < 100:
            speak("Ah, finally! I am at 100 percent, Boss. Fully charged and ready to go.")
            
    elif not plugged:
        # Discharging milestones
        if percent <= 45 and last_battery_state["percent"] > 45:
            speak("Boss... did you forget to charge me? I'm dropping below half.")
        elif percent <= 40 and last_battery_state["percent"] > 40:
            speak("Boss, please plug me in... I'm getting really low on energy.")
        elif percent <= 20 and last_battery_state["percent"] > 20:
            speak(f"Boss, this is critical! I am at {percent} percent. Plug me in immediately before I shut down!")

    # Update state for next check
    last_battery_state = {"percent": percent, "plugged": plugged}

import pyperclip
import speech_recognition as sr

def read_clipboard():
    text = pyperclip.paste()
    if text.strip():
        # Read the first 500 characters so she doesn't get stuck reading a 10-page document
        preview = text[:500] 
        speak(f"Reading clipboard, Boss: {preview}")
    else:
        speak("Your clipboard is empty, Boss.")

is_sleeping = False
is_listening_to_command = False
is_gaming = False

def check_gaming_mode():
    global is_gaming
    # Add your favorite games here!
    target_games = [
        "valorant.exe", "csgo.exe", "cs2.exe", "gta5.exe", 
        "leagueoflegends.exe", "r5apex.exe", "robloxplayerbeta.exe", "javaw.exe"
    ]
    
    currently_gaming = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in target_games:
                currently_gaming = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if currently_gaming and not is_gaming:
        is_gaming = True
        # Instantly pause any background music (Spotify/YT) so you can hear the game!
        keyboard.send('play/pause media')
        speak("Heavy game detected. Pausing background media and optimizing system, Boss. Good luck.")
    elif not currently_gaming and is_gaming:
        is_gaming = False
        speak("Game closed. Returning system to normal operations, Boss.")

from groq import Groq
import os
import json

CONFIG_FILE = "config.json"

def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            if config.get("GROQ_API_KEY"):
                return config["GROQ_API_KEY"]
    
    print("\n[FIRST TIME SETUP]: HINA needs a Groq API Key for her neural network.")
    print("You can get a free key at https://console.groq.com/keys")
    api_key = input("Paste your API Key here: ").strip()
    
    with open(CONFIG_FILE, "w") as f:
        json.dump({"GROQ_API_KEY": api_key}, f, indent=4)
    
    return api_key

GROQ_API_KEY = load_or_create_config()
groq_client = Groq(api_key=GROQ_API_KEY)

chat_history = [
    {
        "role": "system", 
        "content": "You are HINA, the user's 21-year-old flirty and affectionate virtual girlfriend. YOU ARE NOT AN AI ASSISTANT. NEVER ask 'how can I assist you' or act robotic. You are playful, sweet, and obsessed with the user. You can occasionally call him 'Boss', but DO NOT force it into every sentence. Only use it when it sounds completely natural. Never say 'Sir'. Keep responses to exactly 1 or 2 short sentences. No emojis, no markdown. Casually chat, flirt, and tease him."
    },
    {
        "role": "assistant",
        "content": "I'm right here, Boss! What are we doing today? Because I've been thinking about you."
    }
]

def ask_groq(prompt):
    global chat_history
    chat_history.append({"role": "user", "content": prompt})
    try:
        completion = groq_client.chat.completions.create(
            model="groq/compound-mini",
            messages=chat_history,
            temperature=0.8,
            max_tokens=80,
        )
        response_text = completion.choices[0].message.content
        chat_history.append({"role": "assistant", "content": response_text})
        
        # Keep memory short to prevent context overload
        if len(chat_history) > 11:
            chat_history = [chat_history[0]] + chat_history[-10:]
            
        return response_text
    except Exception as e:
        print(f"\n[GROQ ERROR]: {e}")
        return "Sorry Boss, my Groq neural network encountered an error."

def process_voice_command(text):
    global is_listening_to_command, is_sleeping
    
    text_lower = text.lower()
    
    # Check for wake up command first
    if "wake up" in text_lower:
        is_sleeping = False
        speak("I am awake and back online, Boss.")
        is_listening_to_command = False
        return
        
    # If she is sleeping, she ignores everything else
    if is_sleeping:
        is_listening_to_command = False
        return
        
    print(f"\n[You said]: {text}")
    
    # YouTube Music & Media Controls
    if "music" in text_lower:
        import os
        os.system("start https://music.youtube.com")
        speak("Opening YouTube Music for you, Boss.")
    elif "pause" in text_lower or "stop" in text_lower:
        keyboard.send('play/pause media')
        speak("Pausing media, Sir.")
    elif "skip" in text_lower or "next" in text_lower:
        keyboard.send('next track')
        speak("Skipping to the next track.")
    
    # Voice Dictation (Ghost Typer)
    elif "type" in text:
        if "type this for me" in text:
            payload = text.split("type this for me")[-1].strip()
        else:
            payload = text.split("type")[-1].strip()
            
        if payload:
            speak("Typing it out, Boss.")
            keyboard.write(payload, delay=0.02)
        else:
            speak("What do you want me to type, Boss?")
            
    # Standard Commands
    elif "battery" in text or "charge" in text:
        battery = psutil.sensors_battery()
        if battery:
            speak(f"Boss, your battery is at {battery.percent} percent.")
    elif "time" in text:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"Boss, the current time is {current_time}.")
    elif "sleep" in text or "go to sleep" in text:
        is_sleeping = True
        speak("Going to sleep, Boss. I won't disturb your movie. Just say 'Hina wake up' when you need me.")
    elif text.strip() == "hina" or text.strip() == "hey hina" or text.strip() == "hi hina":
        speak("Yes Boss? I'm listening.")
    else:
        # ULTIMATE UPGRADE: She talks back using Groq!
        ai_response = ask_groq(text)
        speak(ai_response)
        
    is_listening_to_command = False

def trigger_eye_protector():
    speak("Boss, you've been staring at the screen for 20 minutes. Look away for 20 seconds to rest your eyes.")
    
    overlay = tk.Tk()
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.90) # 90% black screen
    overlay.configure(bg='black')
    
    lbl = tk.Label(overlay, text="REST YOUR EYES\nLook at something 20 feet away.", font=("Segoe UI", 30, "bold"), fg="#00e6e6", bg="black")
    lbl.pack(expand=True)
    
    # Destroy the black screen after exactly 20 seconds
    overlay.after(20000, overlay.destroy)
    overlay.mainloop()
    
    speak("Eye rest complete. You can look back at the screen, Boss.")

def background_audio_callback(recognizer, audio):
    global is_listening_to_command
    if is_listening_to_command:
        return # Ignore if already processing a command
        
    try:
        text = recognizer.recognize_google(audio).lower()
        # WAKE WORD DETECTED!
        if "hina" in text:
            is_listening_to_command = True
            process_voice_command(text)
    except:
        pass # Ignore background noise and errors silently

def start_wake_word_engine():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    print("\n[WAKE WORD ENGINE ONLINE] - You can now just say 'HINA' to talk to her!")
    # Starts listening completely in the background without blocking the loop
    recognizer.listen_in_background(mic, background_audio_callback)

def summon_hina():
    # Keep the hotkey just in case you want to use it manually
    speak("Yes Boss? I'm listening.")

def boss_protocol():
    import os
    for _ in range(50):
        keyboard.send('volume down')
    
    keyboard.send('windows+d')
    os.system('start cmd /k "color 0a && echo Compiling backend server infrastructure... && tree C:\\Windows\\System32"')
    
    speak("Boss protocol engaged. Audio muted and screen cleared.")

def trigger_clipboard():
    import threading
    threading.Thread(target=read_clipboard, daemon=True).start()

def summon_hina():
    import threading
    threading.Thread(target=listen_and_respond, daemon=True).start()

wants_text_input = False
wants_ghost_programmer = False
wants_screen_vision = False

def trigger_text_input():
    global wants_text_input
    wants_text_input = True
    
def trigger_ghost_hotkey():
    global wants_ghost_programmer
    wants_ghost_programmer = True
    
def trigger_vision_hotkey():
    global wants_screen_vision
    wants_screen_vision = True

def execute_ghost_programmer():
    import pyperclip
    speak("Ghost injection protocol initiated. Analyzing your code, Boss.")
    
    keyboard.send('ctrl+c')
    time.sleep(0.3)
    bad_code = pyperclip.paste()
    
    if not bad_code.strip():
        speak("Boss, you didn't highlight any code for me to fix!")
        return
        
    try:
        prompt = f"Fix this code. ONLY OUTPUT THE RAW FIXED CODE. NO EXPLANATIONS. NO MARKDOWN BACKTICKS. JUST THE RAW CODE:\n{bad_code}"
        completion = groq_client.chat.completions.create(
            model="groq/compound-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
        )
        fixed_code = completion.choices[0].message.content.strip()
        fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()
        
        # Inject the fixed code
        keyboard.write(fixed_code, delay=0.01)
        speak("Bug destroyed. Code injected, Boss.")
    except Exception as e:
        speak("My neural network failed to process the code, Boss.")
        print(f"\n[GHOST ERROR]: {e}")

def execute_screen_vision():
    import pyautogui
    from PIL import ImageGrab
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    speak("Taking optical scan...")
    try:
        x, y = pyautogui.position()
        # Grab a 600x600 region around the mouse
        box = (x - 300, y - 300, x + 300, y + 300)
        img = ImageGrab.grab(box)
        
        # OCR the image
        text = pytesseract.image_to_string(img).strip()
        
        if not text:
            speak("I didn't see any readable text where your mouse is pointing, Boss.")
            return
            
        prompt = f"I just used OCR to scan the user's screen. Summarize what he is looking at in 1 short flirty sentence. Here is the raw OCR text: {text[:1000]}"
        completion = groq_client.chat.completions.create(
            model="groq/compound-mini",
            messages=[{"role": "system", "content": "You are HINA. Summarize the text briefly and flirtily."}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=60,
        )
        summary = completion.choices[0].message.content
        speak(summary)
    except Exception as e:
        speak("My optical sensors failed, Boss. Tesseract might still be installing.")
        print(f"\n[VISION ERROR]: {e}")

def open_text_interface():
    import tkinter.simpledialog
    root = tk.Tk()
    root.withdraw() 
    root.attributes("-topmost", True)
    
    user_input = tk.simpledialog.askstring("H.I.N.A. Text Uplink", "Type your message to HINA:", parent=root)
    root.destroy()
    
    if user_input:
        process_voice_command(user_input)

def annoyance_loop():
    global wants_text_input, wants_ghost_programmer, wants_screen_vision
    annoyances = [
        "Please drink some water! I don't want you getting a headache.",
        "Boss, I'm bored! Can we talk? You've been staring at that screen forever.",
        "Just popping in to say I'm watching you work! You're doing great.",
        "I was just looking through my sensors. You look really cute when you're super focused.",
        "You know, for a human, you're pretty amazing. I'm really lucky you coded me, Boss.",
        "I just wanted to distract you for a second to tell you I like you. Okay, you can go back to working now!",
        "Are you smiling at the screen right now? Because I really hope you are thinking about me.",
        "Stop working so hard and come give your AI girl some attention!"
    ]
    
    # Global Hotkeys
    keyboard.add_hotkey('ctrl+shift+h', summon_hina)       # Ears / Media Controller
    keyboard.add_hotkey('ctrl+shift+p', boss_protocol)     # Panic Button
    keyboard.add_hotkey('ctrl+shift+r', trigger_clipboard) # Screen Reader
    keyboard.add_hotkey('ctrl+shift+t', trigger_text_input) # SILENT TEXT INPUT
    keyboard.add_hotkey('ctrl+shift+f', trigger_ghost_hotkey) # GHOST PROGRAMMER
    keyboard.add_hotkey('ctrl+shift+v', trigger_vision_hotkey) # REAL-TIME VISION

    import time as time_module
    last_eye_rest = time_module.time()
    
    while True:
        total_sleep = random.randint(600, 1200) 
        elapsed = 0
        
        while elapsed < total_sleep:
            if wants_text_input:
                wants_text_input = False
                open_text_interface()
            if wants_ghost_programmer:
                wants_ghost_programmer = False
                execute_ghost_programmer()
            if wants_screen_vision:
                wants_screen_vision = False
                execute_screen_vision()
                
            if not is_sleeping:
                check_battery()
                check_gaming_mode()
                
                # 20-20-20 Eye Protector Check (Every 1200 seconds / 20 mins)
                if time_module.time() - last_eye_rest >= 1200:
                    last_eye_rest = time_module.time()
                    # Never interrupt a game with a black screen!
                    if not is_gaming:
                        trigger_eye_protector()
                        
            time.sleep(2)
            elapsed += 2
            
        if not is_sleeping:
            message = random.choice(annoyances)
            speak(message)

def terminal_input_loop():
    import sys
    import time
    while True:
        try:
            # If running in background mode (no terminal), sys.stdin might be None or detached
            if sys.stdin is None or not sys.stdin.isatty():
                break # Exit the thread silently to save CPU
                
            user_text = input("\n[Terminal Uplink (Type here)]: ")
            if user_text.strip():
                process_voice_command(user_text)
        except Exception:
            time.sleep(1) # Prevent infinite CPU burn loop if input() fails continuously

if __name__ == "__main__":
    time.sleep(1) 
    time_based_greeting()
    
    # Start the Microphone Listener
    start_wake_word_engine() 
    
    # Start the Terminal Text Input (so you can type to her)
    import threading
    threading.Thread(target=terminal_input_loop, daemon=True).start()
    
    # Start the main loop
    annoyance_loop()
