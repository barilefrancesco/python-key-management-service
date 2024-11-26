import os
import glob
from datetime import datetime, timedelta

LOG_DIR = '/kms/data'
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

def parse_log_timestamp(line):
    try:
        timestamp_str = line.split(' - ')[0]
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
    except ValueError:
        return None

def cleanup_logs():
    cutoff_date = datetime.now() - timedelta(days=30)
    temp_file = os.path.join(LOG_DIR, 'app.log.temp')

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as infile, open(temp_file, 'w') as outfile:
            for line in infile:
                log_timestamp = parse_log_timestamp(line)
                if log_timestamp and log_timestamp >= cutoff_date:
                    outfile.write(line)

        # Replace the original log file with the filtered one
        os.replace(temp_file, LOG_FILE)
        print(f"{datetime.utcnow().isoformat()} - Old log entries removed from {LOG_FILE}")
    else:
        print(f"{datetime.utcnow().isoformat()} - Log file {LOG_FILE} does not exist.")


if __name__ == "__main__":
    cleanup_logs()