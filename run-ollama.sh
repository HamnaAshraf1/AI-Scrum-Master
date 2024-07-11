#!/bin/sh

ollama serve &
sleep 5
ollama list
ollama pull llama3
