#!/bin/sh
nohup ollama serve &
fastapi run main.py