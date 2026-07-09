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
    
    # Calibration parameters
    # balance: offset factor between -0.90 and 0.90
    # - If negative: slows down left motor (compensates for slow right motor)
    # - If positive: slows down right motor (compensates for slow left motor)
    balance = 0.0
    speed = 60
    moving = False
    
    manual = """
===================================================
    MOTOR SPEED CALIBRATION TOOL (PI-CAR X)
===================================================
 Instructions:
   1. Place the car on a flat surface in a straight line.
   2. Press [W] to start moving forward.
   3. If it veers left, press [D] to adjust.
   4. If it veers right, press [A] to adjust.
   5. Press [Space] to stop the motors.
   6. Write down the final "Balance" value for your projects.

 Keys:
   [W] : Start moving forward
   [Space] : Stop motors
   [A] : Decrease balance (slow down left motor / turn left)
   [D] : Increase balance (slow down right motor / turn right)
   [Ctrl + C] : Exit and save
===================================================
"""
    print(manual)
    
    prev_state = None
    prev_balance = None

    try:
        while True:
            # Calculate speeds applying balance
            if balance < 0:
                # Right motor is slower, slow down left motor
                left_speed = speed * (1.0 + balance)
                right_speed = speed
            else:
                # Left motor is slower, slow down right motor
                left_speed = speed
                right_speed = speed * (1.0 - balance)
                
            # Print status only on changes
            if (moving != prev_state) or (balance != prev_balance):
                print(f"[STATUS] State: {'RUNNING' if moving else 'STOPPED'} | Balance: {balance:.2f} | M1 (Left): {left_speed:.1f} | M2 (Right): {right_speed:.1f}")
                prev_state = moving
                prev_balance = balance
            
            key = get_key_non_blocking()
            if key is not None:
                if key == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                
                key_lower = key.lower()
                if key_lower == 'w':
                    moving = True
                elif key == ' ':
                    moving = False
                elif key_lower == 'a':
                    balance = max(-1, balance - 0.02)
                elif key_lower == 'd':
                    balance = min(1, balance + 0.02)
            
            if moving:
                px.set_motor_speed(1, left_speed)
                px.set_motor_speed(2, -1 * right_speed)
            else:
                px.stop()
                
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n\nCalibration interrupted by user.")
    finally:
        print("Stopping motors and exiting...")
        px.stop()
        px.reset()
        time.sleep(0.2)
        print(f"Finished! Your final balance value is: {balance:.2f}")

if __name__ == "__main__":
    main()
