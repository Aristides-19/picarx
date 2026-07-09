import sys
import select
import termios
import tty
import time
from picarx import Picarx
from rich import print

def get_key_non_blocking():
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

def main():
    print("Initializing PiCar-X...")
    px = Picarx()
    px.stop()
    px.set_dir_servo_angle(0)
    
    manual = """
===================================================
     INDIVIDUAL MOTOR TEST TOOL (PI-CAR X)
===================================================
 Instructions:
   Press a key to run a SINGLE motor.
   Observe which physical wheel spins (Left or Right?).

 Keys:
   [Q] : Activate MOTOR 1 ONLY (Code: Left motor)
   [E] : Activate MOTOR 2 ONLY (Code: Right motor)
   [Space] : Stop both motors

   [Ctrl + C] : Exit program
===================================================
"""

    active_motor = 0  # 0: none, 1: Motor 1, 2: Motor 2
    print(manual)
    prev_active_motor = None

    try:
        while True:
            # Print status only on changes
            if active_motor != prev_active_motor:
                if active_motor == 1:
                    print("[STATUS] ACTIVE: MOTOR 1 (Code: Left)  | Physical: ?")
                elif active_motor == 2:
                    print("[STATUS] ACTIVE: MOTOR 2 (Code: Right) | Physical: ?")
                else:
                    print("[STATUS] BOTH MOTORS STOPPED")
                prev_active_motor = active_motor
                
            key = get_key_non_blocking()
            if key is not None:
                if key == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                
                key_lower = key.lower()
                if key_lower == 'q':
                    active_motor = 1
                elif key_lower == 'e':
                    active_motor = 2
                elif key == ' ':
                    active_motor = 0

            # Apply speed to selected motor
            if active_motor == 1:
                px.set_motor_speed(1, 50)  # Motor 1 forward
                px.set_motor_speed(2, 0)   # Motor 2 stopped
            elif active_motor == 2:
                px.set_motor_speed(1, 0)   # Motor 1 stopped
                px.set_motor_speed(2, -50) # Motor 2 forward (forward direction polarity)
            else:
                px.stop()
                
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        pass
    finally:
        print("\n\nExiting and stopping motors...")
        px.stop()
        px.reset()
        time.sleep(0.2)
        print("Done!")

if __name__ == "__main__":
    main()
