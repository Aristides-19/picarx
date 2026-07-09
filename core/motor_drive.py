from picarx import Picarx
from rich import print

class MotorDrive:
    # Calibrated speed balance factor.
    # A value of -0.90 reduces the Left Motor (Motor 1) to 10% of target speed
    # to match the degraded Right Motor (Motor 2) and make the car go straight.
    BALANCE = -0.90

    def __init__(self, picarx_instance=None):
        """
        Initializes the MotorDrive helper.
        Can accept an existing Picarx instance to avoid re-initializing the hardware.
        """
        if picarx_instance is not None:
            self.px = picarx_instance
        else:
            self.px = Picarx()

    def forward(self, speed):
        """
        Drive the robot forward applying the constant speed balance to keep it straight.
        """
        if self.BALANCE < 0:
            left_speed = speed * (1.0 + self.BALANCE)
            right_speed = speed
        else:
            left_speed = speed
            right_speed = speed * (1.0 - self.BALANCE)
            
        self.px.set_motor_speed(1, left_speed)
        self.px.set_motor_speed(2, -1 * right_speed)

    def backward(self, speed):
        """
        Drive the robot backward applying the constant speed balance to keep it straight.
        """
        if self.BALANCE < 0:
            left_speed = speed * (1.0 + self.BALANCE)
            right_speed = speed
        else:
            left_speed = speed
            right_speed = speed * (1.0 - self.BALANCE)
            
        self.px.set_motor_speed(1, -1 * left_speed)
        self.px.set_motor_speed(2, right_speed)

    def stop(self):
        """
        Stop both motors.
        """
        self.px.stop()

    def set_steering(self, angle):
        """
        Set the steering servo angle.
        """
        self.px.set_dir_servo_angle(angle)

if __name__ == "__main__":
    import time
    print("Testing core.MotorDrive class...")
    drive = MotorDrive()
    print("Driving forward for 2 seconds...")
    drive.forward(60)
    time.sleep(2)
    print("Driving backward for 2 seconds...")
    drive.backward(60)
    time.sleep(2)
    print("Stopping...")
    drive.stop()
    print("Test finished successfully!")
