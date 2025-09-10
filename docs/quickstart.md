# Quick Start

This short guide helps you get OTSploit running quickly.

## Install
- Python 3.8+ recommended
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Run (Standalone UI)
```bash
python OTSploit_standalone.py
# or (to avoid site-package interference)
python -S OTSploit_standalone.py
```

## Basic workflow
```text
OTSploit > list
OTSploit > use 14
OTSploit (S7-300/400 PLC Control) > show options
OTSploit (...) > set target 192.168.1.10
OTSploit (...) > set port 102
OTSploit (...) > run
```

## Configuration
Add API keys (optional) in `OTSploit.ini`:
```ini
[API]
gemini_key = <your gemini key>
serper_key = <your serper key>
nvd_key = <your nvd api key>
```

Or set env vars: `GEMINI_API_KEY`, `SERPER_API_KEY`, `NVD_API_KEY`.
