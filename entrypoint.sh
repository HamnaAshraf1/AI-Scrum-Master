#!/bin/sh

curl -fsSL https://ollama.com/install.sh | sh
sleep 5
ollama serve &

sleep 5

ollama pull llama3.1

sleep 10

python3 start.py
