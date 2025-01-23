import tkinter as tk
from datetime import timedelta
import threading
import psutil

# Global variables
allowed_apps = []  # List of allowed apps (populated at runtime)
timer_running = False  # To track if the timer is running

# Function to capture currently running apps
def capture_running_apps():
    global allowed_apps
    for process in psutil.process_iter(['pid', 'name']):
        app_name = process.info['name']
        if app_name not in allowed_apps:
            allowed_apps.append(app_name)

# Function to block only new apps
def block_new_apps():
    while timer_running:  # Only block apps while the timer is running
        for process in psutil.process_iter(['pid', 'name']):
            app_name = process.info['name']
            if app_name not in allowed_apps:
                try:
                    process.kill()  # Kill the process
                except psutil.AccessDenied:
                    pass

# Function to start the timer
def start_timer(duration):
    global timer_running
    timer_running = True  # Timer starts
    def update_time():
        nonlocal duration
        if duration > 0:
            duration -= 1
            timer_label.config(text=str(timedelta(seconds=duration)))
            root.after(1000, update_time)
        else:
            timer_label.config(text="Time's up!")
            timer_running = False  # Timer ends

    update_time()

# Function to handle the Start button
def start_focus_session():
    global timer_running
    if not timer_running:
        try:
            # Get duration from input and convert to seconds
            duration_minutes = int(timer_input.get())
            duration_seconds = duration_minutes * 60

            # Start the timer
            start_timer(duration_seconds)

            # Start app blocking in a separate thread
            threading.Thread(target=block_new_apps, daemon=True).start()

            # Disable input and start button during the session
            timer_input.config(state='disabled')
            start_button.config(state='disabled')
        except ValueError:
            timer_label.config(text="Enter a valid number!")

# Timer UI setup
def create_dashboard():
    global root, timer_input, start_button, timer_label
    root = tk.Tk()
    root.title("Focus Dashboard")
    root.geometry("300x200")
    root.attributes("-topmost", True)  # Keep window on top

    # Instruction label
    instruction_label = tk.Label(root, text="Enter focus time (minutes):", font=("Arial", 12))
    instruction_label.pack(pady=10)

    # Timer input field
    timer_input = tk.Entry(root, font=("Arial", 14), justify="center")
    timer_input.pack(pady=5)

    # Start button
    start_button = tk.Button(root, text="Start Focus Session", font=("Arial", 12), command=start_focus_session)
    start_button.pack(pady=10)

    # Timer label
    timer_label = tk.Label(root, text="", font=("Arial", 18))
    timer_label.pack(pady=10)

    # Start the Tkinter main loop
    root.mainloop()

# Main function to run the app
if __name__ == "__main__":
    # Step 1: Capture currently running apps
    capture_running_apps()

    # Step 2: Create the dashboard
    create_dashboard()
