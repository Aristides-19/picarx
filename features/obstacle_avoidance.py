import time
from picarx import Picarx
from core.motor_drive import MotorDrive
from rich import print

def run_obstacle_avoidance(px_instance=None):
    """
    Obstacle Avoidance Feature. Uses the ultrasonic sensor to detect obstacles,
    steer away, or back up to avoid collisions.
    """
    print("Starting Obstacle Avoidance Feature...")
    
    # Initialize Picarx and MotorDrive
    if px_instance is None:
        px_instance = Picarx()
        
    drive = MotorDrive(px_instance)
    
    # Configuration Constants
    POWER = 60
    SAFE_DISTANCE = 35.0    # Distance in cm to drive straight safely
    DANGER_DISTANCE = 15.0  # Distance in cm where backing up is required
    
    manual = """
===================================================
            OBSTACLE AVOIDANCE FEATURE
===================================================
 The robot will drive autonomously and steer away
 from objects detected by the ultrasonic sensor.
 
 Exit:
   [Ctrl + C] : Stop robot and return to Main Menu
===================================================
"""
    print(manual)
    
    prev_state = None
    
    try:
        while True:
            # Read ultrasonic sensor distance in cm
            distance = round(px_instance.ultrasonic.read(), 2)
            
            # Decide actions based on distance
            if distance >= SAFE_DISTANCE:
                state_str = "CLEAR - Driving Forward"
                drive.set_steering(0)
                drive.forward(POWER)
            elif distance >= DANGER_DISTANCE:
                state_str = "OBJECT DETECTED - Steering Right"
                drive.set_steering(30)
                drive.forward(POWER)
                time.sleep(0.1)
            else:
                state_str = "DANGER ZONE - Backing Up"
                drive.set_steering(-30)
                drive.backward(POWER)
                time.sleep(0.5)
                
            # Log status only on state change to avoid terminal spam
            if state_str != prev_state:
                print(f"[AVOID] Dist: {distance:.1f} cm | State: {state_str}")
                prev_state = state_str
                
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nObstacle avoidance ended by user.")
    finally:
        # Reset and stop the robot safely
        drive.stop()
        drive.set_steering(0)
        print("Hardware reset completed.")

if __name__ == "__main__":
    run_obstacle_avoidance()
