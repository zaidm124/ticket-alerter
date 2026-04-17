#!/bin/bash
# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Run the python script using the venv and log output with a timestamp
echo "-----------------------------------" >> run_log.txt
date >> run_log.txt
./venv/bin/python3 scrape.py >> run_log.txt 2>&1

# Optional: Send a Mac desktop notification if a match is found
if grep -q "MATCH FOUND" run_log.txt; then
    osascript -e 'display notification "Tickets below 3000 Rs might be available!" with title "Ticket Alert 🎫"'
fi
