
import json
from datetime import datetime

def backup_filename(file):
    # E.g., patients.json → patients_backup.json
    if file.endswith('.json'):
        return file.replace('.json', '_backup.json')
    else:
        return file + '_backup'

def log_action(action, filetitle, status):
    log_entry = {
        "timestamp": datetime.now().isoformat(timespec='seconds'),
        "action": action,
        "file": filetitle,
        "status": status
    }
    try:
        # Append to logs.json
        logs = []
        try:
            with open("logs.json", 'r') as lfile:
                logs = json.load(lfile)
        except Exception:
            pass
        logs.append(log_entry)
        with open("logs.json", 'w') as lfile:
            json.dump(logs, lfile, indent=2)
    except Exception as e:
        print(f"Logging error: {e}")

def write_json(file, data):
    try:
        with open(file, 'w') as main_f:
            json.dump(data, main_f, indent=2)
        log_action("write", file, "opened with write mode")

        backup_file = backup_filename(file)
        with open(backup_file, 'w') as backup_f:
            json.dump(data, backup_f, indent=2)
        log_action("write_backup", backup_file, "backup added ")
    except Exception as e:
        log_action("write", file, f"error: {str(e)}")

def read_json(file):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        log_action("read", file, "read operation")
        return data
    except Exception as e:
        log_action("read", file, f"error: {str(e)}")
        # Try reading backup
        try:
            backup_file = backup_filename(file)
            with open(backup_file, 'r') as bf:
                data = json.load(bf)
            log_action("read_backup", backup_file, "ok")
            return data
        except Exception as be:
            log_action("read_backup", backup_file, f"error: {str(be)}")
            return []
