import os
import subprocess
import datetime
import webbrowser
import urllib.parse
import uuid

def get_current_time() -> str:
    """Returns the current local date and time."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def open_application(app_name: str) -> str:
    """Opens a common Windows application by name (e.g., 'notepad', 'calculator')."""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "browser": "start https://www.google.com" # Quick hack for default browser
    }
    
    app_name = app_name.lower()
    if app_name in apps:
        try:
            if "start " in apps[app_name]:
                os.system(apps[app_name])
            else:
                subprocess.Popen(apps[app_name])
            return f"Successfully opened {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"
    else:
        return f"Application '{app_name}' not found in the safe list (supported: {', '.join(apps.keys())})."

def compose_email(to_address: str, subject: str, body: str) -> str:
    """
    Composes an email by opening a new Gmail compose tab in the browser 
    pre-filled with the recipient, subject, and body.
    Important: You must ask the user for the recipient, subject, and body before calling this tool.
    """
    try:
        # URL encode the subject and body to safely handle spaces and special characters
        subject_enc = urllib.parse.quote(subject)
        body_enc = urllib.parse.quote(body)
        
        # Use Gmail's compose URL format instead of mailto (which fails if no desktop client is set)
        gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to={to_address}&su={subject_enc}&body={body_enc}"
        
        # Open default OS web browser directly to Gmail
        webbrowser.open(gmail_link)
        return f"Successfully opened Gmail in your browser to draft the email to {to_address}."
    except Exception as e:
        return f"Failed to open Gmail: {str(e)}"

def save_note(filename: str, content: str) -> str:
    """
    Saves a text note to a file in the 'notes' directory.
    If the file exists, it will append to it.
    """
    try:
        os.makedirs("notes", exist_ok=True)
        # Ensure safe filename
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip() + ".txt"
        filepath = os.path.join("notes", safe_filename)
        
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"--- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(content + "\n\n")
            
        # Automatically open the saved note so the user sees it
        if os.name == 'nt':
            os.startfile(os.path.abspath(filepath))
        else:
            webbrowser.open('file://' + os.path.abspath(filepath))
        return f"Successfully saved and opened the note as {safe_filename}."
    except Exception as e:
        return f"Failed to save note: {str(e)}"

def create_calendar_event(title: str, date_YYYYMMDD: str, time_HHMMSS: str, duration_minutes: int = 60) -> str:
    """
    Creates an iCalendar (.ics) file and opens it. Opening it prompts the default OS calendar app.
    """
    try:
        os.makedirs("events", exist_ok=True)
        filename = f"events/event_{uuid.uuid4().hex[:8]}.ics"
        
        # Start and End Times
        start_datetime_str = f"{date_YYYYMMDD}T{time_HHMMSS}"
        
        try:
            start_dt = datetime.datetime.strptime(start_datetime_str, "%Y%m%dT%H%M%S")
            end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
            end_datetime_str = end_dt.strftime("%Y%m%dT%H%M%S")
        except:
            # Fallback if parsing fails
            end_datetime_str = start_datetime_str
            
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Commander AI//EN
BEGIN:VEVENT
UID:{uuid.uuid4()}
DTSTAMP:{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}
DTSTART:{start_datetime_str}
DTEND:{end_datetime_str}
SUMMARY:{title}
END:VEVENT
END:VCALENDAR"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(ics_content)
            
        # Open the file
        filepath = os.path.abspath(filename)
        if os.name == 'nt':
            os.startfile(filepath)
        else:
            webbrowser.open('file://' + filepath)
            
        return f"Successfully generated calendar event '{title}' and opened it in your calendar app."
    except Exception as e:
        return f"Failed to create calendar event: {str(e)}"
