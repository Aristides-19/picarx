import sys
from picarx import Picarx
from rich import print

# Import modular features
from features.keyboard_control import run_keyboard_control
from features.battery_monitor import run_battery_monitor
from features.camera_server import run_camera_server
from features.obstacle_avoidance import run_obstacle_avoidance
from features.voice_prompts import run_voice_prompts
from features.vosk_voice_control import run_vosk_voice_control

def main():
    """
    Main entry point for the PiCar-X system.
    Displays a menu and runs the selected modular feature.
    """
    print("[bold green]Initializing PiCar-X Hardware...[/bold green]")
    try:
        # Initialize the shared Picarx hardware instance once
        px = Picarx()
        # Play engine startup sound asynchronously
        import os
        from robot_hat import Music
        music = Music()
        music.music_set_volume(100)
        project_root = os.path.dirname(os.path.abspath(__file__))
        startup_sound = os.path.join(project_root, "assets", "car-start-engine.wav")
        music.sound_play_threading(startup_sound)
    except Exception as e:
        print(f"[bold red]Failed to initialize Picarx: {e}[/bold red]")
        sys.exit(1)
        
    while True:
        # Display an English, rich-formatted menu
        print("\n[bold cyan]===================================================[/bold cyan]")
        print("[bold white]            PICAR-X SYSTEM MAIN MENU[/bold white]")
        print("[bold cyan]===================================================[/bold cyan]")
        print(" Please select a feature to run:")
        print("   [1] Keyboard Driving Control")
        print("   [2] Battery Status Monitor")
        print("   [3] Camera Web Server")
        print("   [4] Obstacle Avoidance")
        print("   [5] Voice Prompts Demo")
        print("   [6] Vosk Offline Voice Control")
        print("   [7] Exit System")
        print("[bold cyan]===================================================[/bold cyan]")
        
        try:
            choice = input("Enter choice (1-7): ").strip()
        except KeyboardInterrupt:
            print("\nExiting system...")
            break
            
        if choice == '1':
            try:
                run_keyboard_control(px)
            except Exception as e:
                print(f"[bold red]Error running Keyboard Control: {e}[/bold red]")
        elif choice == '2':
            try:
                run_battery_monitor(px)
            except Exception as e:
                print(f"[bold red]Error running Battery Monitor: {e}[/bold red]")
        elif choice == '3':
            try:
                run_camera_server(px)
            except Exception as e:
                print(f"[bold red]Error running Camera Server: {e}[/bold red]")
        elif choice == '4':
            try:
                run_obstacle_avoidance(px)
            except Exception as e:
                print(f"[bold red]Error running Obstacle Avoidance: {e}[/bold red]")
        elif choice == '5':
            try:
                run_voice_prompts(px)
            except Exception as e:
                print(f"[bold red]Error running Voice Prompts: {e}[/bold red]")
        elif choice == '6':
            try:
                run_vosk_voice_control(px)
            except Exception as e:
                print(f"[bold red]Error running Vosk Voice Control: {e}[/bold red]")
        elif choice == '7':
            print("Exiting system. Goodbye!")
            break
        else:
            print("[bold yellow]Invalid choice. Please select 1, 2, 3, 4, 5, 6, or 7.[/bold yellow]")
            
    # Clean up hardware before exit
    print("\nShutting down system...")
    px.reset()
    print("[bold green]Shutdown complete.[/bold green]")

if __name__ == "__main__":
    main()
