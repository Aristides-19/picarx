import sys
import os
import select
import termios
import tty
import time
from picarx import Picarx
from core.motor_drive import MotorDrive
from robot_hat import Music
from rich import print

def get_key_non_blocking():
    """
    Reads a single character from standard input without blocking.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if rlist:
            key = sys.stdin.read(1)
            return key
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def run_keyboard_control(px_instance=None):
    """
    Main loop to control the PiCar-X using keyboard inputs.
    Integrates motor driving with camera pan/tilt control.
    """
    print("Starting Keyboard Control Feature...")
    
    # Initialize Picarx and MotorDrive
    if px_instance is None:
        px_instance = Picarx()
        
    drive = MotorDrive(px_instance)
    music = Music()
    music.music_set_volume(100)
    
    # Resolve the path to the assets directory dynamically
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    horn_sound_path = os.path.join(project_root, "assets", "car-double-horn.wav")
    print(f"Loaded horn sound path: {horn_sound_path}")
    
    # Initialize hardware to neutral/stop state
    drive.stop()
    drive.set_steering(0)
    px_instance.set_cam_pan_angle(0)
    px_instance.set_cam_tilt_angle(0)
    
    pan_angle = 0
    tilt_angle = 0
    
    last_w_time = 0
    last_s_time = 0
    last_a_time = 0
    last_d_time = 0
    
    # Time window (in seconds) to keep keypresses active between repeats
    TIMEOUT = 0.5
    speed = 60
    
    manual = """
===================================================
             KEYBOARD DRIVING FEATURE
===================================================
 Controls (Hold to move/turn, release to stop):
   [W] : Drive Forward
   [S] : Drive Backward
   [A] : Steer Left
   [D] : Steer Right

 Camera Controls (Taps):
   [I] : Camera Tilt Up
   [K] : Camera Tilt Down
   [J] : Camera Pan Left
   [L] : Camera Pan Right

 Car Horn (Tap):
   [C] : Play Car Horn (Threaded)

 Exit:
   [Ctrl + C] : Exit to Main Menu
===================================================
"""
    print(manual)
    
    prev_state = None
    
    try:
        while True:
            key = get_key_non_blocking()
            now = time.time()
            
            if key is not None:
                if key == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                
                key_lower = key.lower()
                if key_lower == 'w':
                    last_w_time = now
                    last_s_time = 0
                    # Mutual extension to support simultaneous steering and driving
                    if now - last_a_time < TIMEOUT:
                        last_a_time = now
                    elif now - last_d_time < TIMEOUT:
                        last_d_time = now
                elif key_lower == 's':
                    last_s_time = now
                    last_w_time = 0
                    # Mutual extension to support simultaneous steering and driving
                    if now - last_a_time < TIMEOUT:
                        last_a_time = now
                    elif now - last_d_time < TIMEOUT:
                        last_d_time = now
                elif key_lower == 'a':
                    last_a_time = now
                    last_d_time = 0
                    # Mutual extension to support simultaneous steering and driving
                    if now - last_w_time < TIMEOUT:
                        last_w_time = now
                    elif now - last_s_time < TIMEOUT:
                        last_s_time = now
                elif key_lower == 'd':
                    last_d_time = now
                    last_a_time = 0
                    # Mutual extension to support simultaneous steering and driving
                    if now - last_w_time < TIMEOUT:
                        last_w_time = now
                    elif now - last_s_time < TIMEOUT:
                        last_s_time = now
                elif key_lower == 'i':
                    tilt_angle = min(30, tilt_angle + 5)
                    px_instance.set_cam_tilt_angle(tilt_angle)
                elif key_lower == 'k':
                    tilt_angle = max(-30, tilt_angle - 5)
                    px_instance.set_cam_tilt_angle(tilt_angle)
                elif key_lower == 'l':
                    pan_angle = min(30, pan_angle + 5)
                    px_instance.set_cam_pan_angle(pan_angle)
                elif key_lower == 'j':
                    pan_angle = max(-30, pan_angle - 5)
                    px_instance.set_cam_pan_angle(pan_angle)
                elif key_lower == 'c':
                    # Play the horn sound in a separate thread so it does not block the control loop
                    music.sound_play_threading(horn_sound_path)

            # Evaluate states
            is_forward = (now - last_w_time < TIMEOUT)
            is_backward = (now - last_s_time < TIMEOUT)
            is_left = (now - last_a_time < TIMEOUT)
            is_right = (now - last_d_time < TIMEOUT)
            
            # Apply Steering
            if is_left:
                drive.set_steering(-30)
            elif is_right:
                drive.set_steering(30)
            else:
                drive.set_steering(0)
                
            # Apply Drive
            if is_forward:
                drive.forward(speed)
            elif is_backward:
                drive.backward(speed)
            else:
                drive.stop()
                
            # Print state on change to prevent infinite terminal scrolling
            current_state = (is_forward, is_backward, is_left, is_right, pan_angle, tilt_angle)
            if current_state != prev_state:
                state_str = "STOPPED"
                if is_forward:
                    state_str = "FORWARD"
                elif is_backward:
                    state_str = "BACKWARD"
                
                steer_str = "CENTER"
                if is_left:
                    steer_str = "LEFT"
                elif is_right:
                    steer_str = "RIGHT"
                    
                print(f"[DRIVE] Motion: {state_str} | Steer: {steer_str} | Cam: Pan {pan_angle}°, Tilt {tilt_angle}°")
                prev_state = current_state
                
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nKeyboard control ended by user.")
    finally:
        drive.stop()
        drive.set_steering(0)
        px_instance.set_cam_pan_angle(0)
        px_instance.set_cam_tilt_angle(0)
        print("Hardware reset completed.")

if __name__ == "__main__":
    run_keyboard_control()
