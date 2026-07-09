import os
import json
import time
import pyaudio
from vosk import Model, KaldiRecognizer
from picarx import Picarx
from core.motor_drive import MotorDrive
from robot_hat import Music, TTS
from rich import print

# Local helper to play voice responses cleanly
tts = None
music = None
horn_sound_path = ""

def speak(text):
    """
    Helper to speak using the robot_hat TTS.
    """
    if tts is not None:
        print(f"[ROBOT] '{text}'")
        try:
            tts.say(text)
            # Sleep to let the background speech finish
            time.sleep(2.0)
        except Exception as e:
            print(f"[bold red]TTS error: {e}[/bold red]")

def run_vosk_voice_control(px_instance=None):
    """
    Vosk Offline Voice Control Feature.
    Listens to the USB microphone, converts Spanish speech to text locally using Vosk,
    and drives the robot based on commands.
    """
    global tts, music, horn_sound_path
    
    print("[bold green]Starting Vosk Local Voice Control...[/bold green]")
    
    # Initialize Picarx and MotorDrive
    if px_instance is None:
        px_instance = Picarx()
        
    drive = MotorDrive(px_instance)
    
    # Initialize Audio and TTS
    music = Music()
    music.music_set_volume(100)
    
    tts = TTS()
    tts.lang("es-ES")
    
    # Resolve the local path to the sound file dynamically
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    horn_sound_path = os.path.join(project_root, "assets", "car-double-horn.wav")
    
    # Load Vosk Spanish model
    print("[yellow]Loading Vosk Spanish Model (offline)...[/yellow]")
    try:
        model = Model(lang="es")
        # Recognizer will be initialized once we know the working sample rate
        recognizer = None
    except Exception as e:
        print(f"[bold red]Failed to load Vosk model: {e}[/bold red]")
        print("[yellow]Ensure your Raspberry Pi is connected to the internet for the first run download.[/yellow]")
        return
        
    # Open PyAudio Stream and probe correct device/sample rate
    p = pyaudio.PyAudio()
    
    # 1. Try to find the USB Microphone index
    device_index = None
    print("[AUDIO] Scanning input devices...")
    for i in range(p.get_device_count()):
        try:
            dev_info = p.get_device_info_by_index(i)
            name = str(dev_info.get("name", ""))
            max_inputs = int(dev_info.get("maxInputChannels", 0))
            print(f"   Index {i}: {name} (inputs: {max_inputs})")
            if max_inputs > 0 and ("usb" in name.lower() or "pnp" in name.lower()):
                device_index = i
        except Exception as scan_err:
            pass
            
    if device_index is not None:
        print(f"[bold green][AUDIO] Selected USB Microphone at index {device_index}[/bold green]")
    else:
        print("[yellow][AUDIO] USB Microphone not explicitly identified. Using system default.[/yellow]")
        
    # 2. Try different sample rates until one succeeds (e.g. 16000, 44100, 48000, 8000)
    rates_to_try = [16000, 44100, 48000, 8000]
    stream = None
    actual_rate = 16000
    
    for r in rates_to_try:
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=r,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=4096
            )
            actual_rate = r
            break
        except Exception as rate_err:
            continue
            
    if stream is None:
        print("[bold red]Failed to open microphone. No supported sample rate found.[/bold red]")
        p.terminate()
        return
        
    try:
        # Restrict vocabulary to allowed words (grammar) to increase accuracy to ~100%
        # and reduce CPU consumption/latency to near zero.
        vocab = [
            "robot", "avanza", "adelante", "retrocede", "atras", 
            "izquierda", "derecha", "detente", "para", "stop", 
            "bocina", "claxon", "pita", "dormir", "silencio", "[unk]"
        ]
        recognizer = KaldiRecognizer(model, actual_rate, json.dumps(vocab))
        stream.start_stream()
        print(f"[bold green]Microphone initialized successfully at {actual_rate} Hz (with grammar).[/bold green]")
    except Exception as e:
        print(f"[bold red]Failed to start audio stream or recognizer: {e}[/bold red]")
        if stream is not None:
            stream.close()
        p.terminate()
        return
        
    manual = """
===================================================
             VOSK OFFLINE VOICE CONTROL
===================================================
 1. Di la palabra de activación "[bold cyan]robot[/bold cyan]".
 2. Cuando el coche responda, di un comando:
    - "[bold green]adelante[/bold green]" o "[bold green]avanza[/bold green]"
    - "[bold green]atras[/bold green]" o "[bold green]retrocede[/bold green]"
    - "[bold green]izquierda[/bold green]"
    - "[bold green]derecha[/bold green]"
    - "[bold green]bocina[/bold green]" o "[bold green]claxon[/bold green]"
    - "[bold green]detente[/bold green]" o "[bold green]para[/bold green]"
    - "[bold green]dormir[/bold green]" (vuelve al modo espera)
 
 Exit:
   [Ctrl + C] : Return to Menu
===================================================
"""
    print(manual)
    
    # Settings
    POWER = 60
    
    speak("Sistema de voz listo")
    print("\n[cyan]>>> Listo para recibir comandos directos...[/cyan]")
    
    try:
        while True:
            # Read chunk of audio data from microphone
            try:
                data = stream.read(2048, exception_on_overflow=False)
            except IOError:
                # Buffer overflow, ignore and continue
                continue
                
            if len(data) == 0:
                continue
                
            # Process chunk with Vosk
            if recognizer.AcceptWaveform(data):
                result_json = json.loads(recognizer.Result())
                text = result_json.get("text", "").lower().strip()
                if not text:
                    continue
                    
                print(f"[OÍDO] '{text}'")
                
                # Fun acknowledgment if wake word is said, but not required to drive
                if "robot" in text:
                    speak("sí")
                    
                if "avanza" in text or "adelante" in text:
                    print("Acción: Avanzar")
                    drive.set_steering(0)
                    drive.forward(POWER)
                    time.sleep(1.5)
                    drive.stop()
                    
                elif "retrocede" in text or "atras" in text:
                    print("Acción: Retroceder")
                    drive.set_steering(0)
                    drive.backward(POWER)
                    time.sleep(1.5)
                    drive.stop()
                    
                elif "izquierda" in text:
                    print("Acción: Girar Izquierda")
                    drive.set_steering(-30)
                    drive.forward(POWER)
                    time.sleep(1.5)
                    drive.stop()
                    drive.set_steering(0)
                    
                elif "derecha" in text:
                    print("Acción: Girar Dera")
                    drive.set_steering(30)
                    drive.forward(POWER)
                    time.sleep(1.5)
                    drive.stop()
                    drive.set_steering(0)
                    
                elif "detente" in text or "para" in text or "stop" in text:
                    print("Acción: Detenerse")
                    drive.stop()
                    drive.set_steering(0)
                    
                elif "bocina" in text or "claxon" in text or "pita" in text:
                    print("Acción: Bocina")
                    music.sound_play_threading(horn_sound_path)
                    
                elif "dormir" in text or "silencio" in text:
                    speak("hasta luego")
                    time.sleep(1.0)
                
    except KeyboardInterrupt:
        print("\nStopping Vosk Voice Control...")
    finally:
        # Stop and close audio stream
        if stream is not None:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
        p.terminate()
        
        # Stop and reset motors
        drive.stop()
        drive.set_steering(0)
        print("Vosk Voice Control closed cleanly.")

if __name__ == "__main__":
    run_vosk_voice_control()
