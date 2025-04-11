#!/bin/bash

# Colors for the terminal
GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

check_status() {
    if [ $1 -eq 200 ] || [ $1 -eq 201 ]; then
        echo -e "${GREEN}[✔] $2 is working!${RESET}"
    else
        echo -e "${RED}[✘] $2 failed (status $1)${RESET}"
    fi
}

echo "▶️ Testing Writer -> POST /write"
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -d "hello world" http://localhost:8081/write)
check_status $response "Writer"

echo "▶️ Testing Reader -> GET /data"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/data)
check_status $response "Reader"

echo "▶️ Testing Reader -> GET /health"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
check_status $response "Reader /health"

echo "▶️ Frontend should be available at: http://localhost:5000"