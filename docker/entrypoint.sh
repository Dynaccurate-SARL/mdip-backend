#!/bin/bash

if [ -z "$RUNNER" ] || [ "$RUNNER" = "API" ]; then
    alembic upgrade head
    uvicorn src.api_main:app --host 0.0.0.0 --port 8000
elif [ "$RUNNER" = "WORKER" ]; then
    taskiq worker --ack-type when_executed src.taskiq_main:broker
fi
