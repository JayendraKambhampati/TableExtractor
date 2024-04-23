#!/bin/sh
#0 0 1 * * ./app1/save_monthly_script_path.sh
MONTH=$(date -d "-1 month" +%m)
#MONTH=$(date -v-1m "+%m")
#YEAR=$(date +%Y)
YEAR=2024
  # select from save_monthly_script_path($THE_MONTH, $THE_YEAR)
echo "Running save_monthly_script_path($MONTH,$YEAR)function:"
psql postgresql://ippuser:postgres@localhost/ipp_logs << EOF
     select from save_monthly_script_path($MONTH,$YEAR);
EOF








#!/bin/sh

# Function to send email notification
send_email_notification() {
    TO="rama.kambhampati@optum.com"
    SUBJECT="Regular Notification"
    BODY="This is a regular notification sent via script execution."
    
    echo "$BODY" | mail -s "$SUBJECT" "$TO"
}

MONTH=$(date -d "-1 month" +%m)
YEAR=2024

# Function to execute
execute_function() {
    echo "Running save_monthly_script_path($MONTH,$YEAR) function:"
    psql postgresql://ippuser:postgres@localhost/ipp_logs << EOF
    select from save_monthly_script_path($MONTH,$YEAR);
EOF
}

# Execute the function
execute_function

# Check if script is running from a terminal
if tty -s; then
    echo "Script is not running from cron."
    send_email_notification
else
    echo "Script is running from cron."
fi
