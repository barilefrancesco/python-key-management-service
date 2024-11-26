# Run the cleanup script at midnight every day
0 0 * * * /usr/bin/python3 /code/cleanup_logs.py >> /var/log/cron.log 2>&1
