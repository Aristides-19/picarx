import time
from robot_hat import utils
from rich import print

def run_battery_monitor(px_instance=None):
    """
    Continuous battery monitoring feature. Shows voltage, estimated charge %,
    and status level in real-time.
    """
    print("Starting Battery Monitor Feature...")
    
    manual = """
===================================================
             BATTERY MONITOR FEATURE
===================================================
 Displays current battery voltage and status.
 Updates every second.

 Exit:
   [Ctrl + C] : Exit to Main Menu
===================================================
"""
    print(manual)
    
    try:
        while True:
            voltage = utils.get_battery_voltage()
            
            # Estimate charge percentage (assuming 2S Li-ion pack: 6.0V = 0%, 8.4V = 100%)
            percentage = max(0.0, min(100.0, (voltage - 6.0) / (8.4 - 6.0) * 100.0))
            
            # Determine charge status
            if voltage > 7.8:
                status = "[green]Good (High)[/green]"
            elif voltage > 6.7:
                status = "[yellow]Fair (Medium)[/yellow]"
            else:
                status = "[red]Low (Recharge immediately!)[/red]"
                
            print(f"[BATTERY] Voltage: {voltage:.2f}V | Charge: {percentage:.1f}% | Status: {status}")
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nBattery monitor ended by user.")

if __name__ == "__main__":
    run_battery_monitor()
