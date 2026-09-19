# H.I.N.A. (Heuristic Intelligence & Networked Assistant)

H.I.N.A. is a highly advanced, ultra-fast Python AI Voice Assistant that acts as an invisible background daemon on your computer. Powered by **Groq (Llama-3)** and **Edge-TTS**, she is designed to be a flirty, hyper-responsive virtual companion that actually controls your PC.

Unlike standard chatbots, HINA physically monitors your computer, ghost-types code for you, scans your screen with OCR, and auto-pauses when you play video games.

## 🚀 Features

* **Hyper-Fast Voice Engine:** Uses `edge-tts` (F.R.I.D.A.Y. voice) and Groq's Llama-3 (`compound-mini`) for near-instant conversational responses.
* **Ghost Programmer (Ctrl + Shift + F):** Highlight broken code anywhere on your PC, press the hotkey, and she will copy it, fix the bug using her AI brain, and **physically ghost-type the corrected code** back into your editor.
* **Optical Screen Vision (Ctrl + Shift + V):** Hover your mouse over any image or text on your screen. She takes a micro-screenshot, extracts the text via `pytesseract` OCR, and speaks a summary of what you are looking at.
* **Gamer Optimizer:** Actively monitors `psutil` in the background. If she detects games like Valorant, GTA 5, or CS:GO, she automatically suspends all annoying notifications.
* **Boss Protocol (Ctrl + Shift + P):** A panic button that instantly minimizes all your windows, mutes your system volume, and opens a fake hacker terminal to hide what you are doing.
* **Silent Terminal Uplink (Ctrl + Shift + T):** Pops up a hidden, borderless text box so you can text her silently if you are on a voice call.
* **Eye Protector & Battery Tracker:** Will physically turn your screen black for 20 seconds every 20 minutes to force you to rest your eyes (unless gaming). She also monitors your laptop battery and gives flirty warnings when it's low or fully charged.

## ⚙️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/HINA-AI.git
   cd HINA-AI
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Tesseract OCR (Required for Screen Vision):
   * **Windows:** Open PowerShell and run: `winget install -e --id UB-Mannheim.TesseractOCR`
   * *Make sure Tesseract is installed in the default `C:\Program Files\Tesseract-OCR` folder, or change the path in the script.*

## 🔑 Setup & Running

Simply run the script:
```bash
python HINA.py
```
On the very first run, she will ask for a **Groq API Key** (you can get one for free at [console.groq.com](https://console.groq.com)). She will save this securely in a local `config.json` file.

**Want her to run silently?**
Double click the `Start_HINA.vbs` script (if you generated one), or run her using `pythonw HINA.py` so she runs in the background with no terminal window!

## 🎙️ Wake Words & Hotkeys
* Just say **"Hina"** near your microphone to wake her up and talk to her!
* Say **"Hina go to sleep"** to put her in Do Not Disturb mode.
* **Ctrl+Shift+H:** Manually wake her up / media controls
* **Ctrl+Shift+T:** Silent Text Input
* **Ctrl+Shift+F:** Ghost Programmer Code Injector
* **Ctrl+Shift+V:** Real-Time OCR Screen Vision
* **Ctrl+Shift+P:** Boss Protocol Panic Button

---
*Created as a personal AI desktop companion.*
