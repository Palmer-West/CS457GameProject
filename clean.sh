#!/bin/bash

# Check if files exist and delete them
if [ -f "server.log" ]; then
    rm "server.log"
    echo "server.log deleted"
else
    echo "server.log not found"
fi

if [ -f "client.log" ]; then
    rm "client.log"
    echo "client.log deleted"
else
    echo "client.log not found"
fi
