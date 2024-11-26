#!/bin/bash

# Check if CRON_ENABLED is set to true
if [ "$CRON_ENABLED" = "true" ]; then
  # Add the cron job
  echo "* 0 * * * /usr/local/bin/python /kms/logs/cleanup_logs.py >> /kms/data/cron.log 2>&1" | crontab -

  # Run cleanup_logs.py immediately on startup
  /usr/local/bin/python /kms/logs/cleanup_logs.py >> /kms/data/cron.log 2>&1
fi

# Start cron
service cron start