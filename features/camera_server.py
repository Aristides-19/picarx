import time
import socket
from vilib import Vilib
from rich import print

def get_ip_address():
    """
    Retrieves the local IP address of the Raspberry Pi.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a dummy external IP to determine local routing interface
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def run_camera_server(px_instance=None):
    """
    Starts the SunFounder Vilib camera server and keeps it running.
    Allows viewing the video stream on a local web page.
    """
    print("Starting Camera Web Server Feature...")
    
    ip = get_ip_address()
    
    manual = f"""
===================================================
             CAMERA WEB SERVER FEATURE
===================================================
 The camera server is now running!
 
 Open your web browser and go to one of these links:
   - Interface: [bold cyan]http://{ip}:9000/[/bold cyan]
   - Raw Stream: [bold cyan]http://{ip}:9000/mjpg[/bold cyan]

 Exit:
   [Ctrl + C] : Stop server and return to Main Menu
===================================================
"""
    print(manual)
    
    # Start the camera and web server.
    # local=False prevents opening an X11 window (safest for headless SSH sessions).
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=False, web=True)
    
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopping camera web server...")
    finally:
        # Safely shut down the camera stream
        Vilib.camera_close()
        print("Camera server shutdown complete.")

if __name__ == "__main__":
    run_camera_server()
