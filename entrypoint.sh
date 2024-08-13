#!/bin/sh

ollama serve &

sleep 5

ollama pull llama3.1

sleep 10

python3 start.py
