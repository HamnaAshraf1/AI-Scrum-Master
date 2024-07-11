#!/bin/sh

ollama serve &

sleep 5

ollama pull llama3

sleep 10

python3 slackbot/example.py
