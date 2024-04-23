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
