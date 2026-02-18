# Ollama Model Manager (GTK3)

A lightweight GTK3 frontend for managing local Ollama models.

## Features

- List installed models
- Pull new models with live progress
- Delete models with confirmation
- Non-blocking UI (threaded downloads)

## Requirements

- Linux
- Python 3.9+
- GTK3
- Ollama running locally (`http://localhost:11434`)
- `pip install -r requirements.txt`

## Installation

```bash
git clone https://github.com/sleeperofsaturn/ollama-model-manager.git
cd ollama-model-manager
pip install -r requirements.txt
