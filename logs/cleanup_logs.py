import os
import glob
from datetime import datetime, timedelta

LOG_DIR = '/code'

def cleanup_logs():
    cutoff_date = datetime.now() - timedelta(days=30)
    log_files = glob.glob(os.path.join(LOG_DIR, '/kms/data/app.log.*'))

    for log_file in log_files:
        file_stat = os.stat(log_file)
        file_creation_time = datetime.fromtimestamp(file_stat.st_ctime)
        if file_creation_time < cutoff_date:
            os.remove(log_file)
            print(f"Deleted log file: {log_file}")

if __name__ == "__main__":
    cleanup_logs()