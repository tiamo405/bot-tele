import schedule
import time
import threading

# Global flag to track if scheduler thread is already started
_scheduler_started = False
_scheduler_lock = threading.Lock()

def schedule_checker():
    """Function that runs in a separate thread to check schedules"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_scheduler():
    """Start the global scheduler thread (only once)"""
    global _scheduler_started
    
    with _scheduler_lock:
        if not _scheduler_started:
            # Start the scheduler in a separate thread
            reminder_thread = threading.Thread(target=schedule_checker)
            reminder_thread.daemon = True  # Thread will exit when main program exits
            reminder_thread.start()
            
            _scheduler_started = True
            print("Global scheduler thread started")
        else:
            print("Scheduler thread already running")
