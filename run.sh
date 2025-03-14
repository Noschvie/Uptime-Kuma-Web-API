#!/bin/sh

export DIR=./app
export VENV=$DIR/.venv/bin/activate

# Check if .env exists and load it
if [ -f "./.env" ]; then
  export $(cat ./.env | xargs)
fi

if [ -z "$NAME" ]; then
  export NAME=uptime-kuma-web-api
fi

if [ -z "$WORKER_CLASS" ]; then
  export WORKER_CLASS=uvicorn.workers.UvicornWorker
fi

if [ -z "$BIND" ]; then
  export BIND=0.0.0.0:8000
fi

if [ -z "$LOG_LEVEL" ]; then
  export LOG_LEVEL=INFO
fi

cd $DIR

exec gunicorn main:app \
  --name $NAME \
  --workers 1 \
  --worker-class $WORKER_CLASS \
  --bind=$BIND \
  --log-level=$LOG_LEVEL 