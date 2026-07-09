import time
from picarx import Picarx
from core.motor_drive import MotorDrive
from robot_hat import Music, TTS
from rich import print

def run_voice_prompts(px_instance=None):
    """
    Voice Prompt Feature. Performs a simple driving sequence,
    announcing each action in English before executing it.
    """
    print("Starting Voice Prompt Feature...")
    
    # Initialize Picarx, MotorDrive, Music and TTS exactly like the working example
    if px_instance is None:
        px_instance = Picarx()
        
    drive = MotorDrive(px_instance)
    music = Music()
    tts = TTS()
    
    # Configure audio settings
    music.music_set_volume(100)
    tts.lang("es-ES")
    
    # Constants
    POWER = 60
    
    def speak_and_wait(text, wait_time=2.5):
        """
        Helper to speak text and sleep to allow the background process
        to finish playing before writing to /tmp/tts.wav again.
        """
        print(f"[VOICE] Saying: '[bold green]{text}[/bold green]'")
        tts.say(text)
        time.sleep(wait_time)
        
    manual = """
===================================================
             VOICE PROMPT FEATURE
===================================================
 The robot will run a driving sequence and announce
 each step in Spanish using the text-to-speech engine.
 
 Exit:
   [Ctrl + C] : Interrupt sequence and return to Menu
===================================================
"""
    print(manual)
    
    try:
        # 1. Greeting
        speak_and_wait("Sistema listo. Iniciando secuencia de voz y movimiento.")
        
        # 2. Forward
        speak_and_wait("Avanzando hacia adelante.")
        drive.set_steering(0)
        drive.forward(POWER)
        time.sleep(2.0)
        drive.stop()
        time.sleep(0.5)
        
        # 3. Backward
        speak_and_wait("Retrocediendo.")
        drive.set_steering(0)
        drive.backward(POWER)
        time.sleep(2.0)
        drive.stop()
        time.sleep(0.5)
        
        # 4. Turn Left
        speak_and_wait("Girando a la izquierda.")
        drive.set_steering(-30)
        drive.forward(POWER)
        time.sleep(2.0)
        drive.stop()
        drive.set_steering(0)
        time.sleep(0.5)
        
        # 5. Turn Right
        speak_and_wait("Girando a la derecha.")
        drive.set_steering(30)
        drive.forward(POWER)
        time.sleep(2.0)
        drive.stop()
        drive.set_steering(0)
        time.sleep(0.5)
        
        # 6. Finish
        speak_and_wait("Secuencia finalizada con éxito.")
        
    except KeyboardInterrupt:
        speak_and_wait("Secuencia cancelada por el usuario.")
    finally:
        # Reset hardware to safe state
        drive.stop()
        drive.set_steering(0)
        print("Hardware reset completed.")

if __name__ == "__main__":
    run_voice_prompts()
