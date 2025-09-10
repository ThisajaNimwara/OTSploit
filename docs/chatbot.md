# Chatbot (ICS/OT Assistant)

The chatbot can answer OT/ICS questions, enrich with web snippets, and summarize NVD CVEs.

## Configure API keys (optional)
`OTSploit.ini`:
```ini
[API]
gemini_key = <your gemini key>
serper_key = <your serper key>
nvd_key = <your nvd api key>
```
Or set env vars: `GEMINI_API_KEY`, `SERPER_API_KEY`, `NVD_API_KEY`.

## One-shot
```text
OTSploit > chatbot -q "CVE-2024-47135 detail"
```

## Interactive
```text
OTSploit > chatbot
chatbot> How to scan Profinet?
chatbot> back
```

## Module-aware context
When a module is selected, its options (e.g., target, port, rack, slot) are included in the prompt to provide more targeted answers.

## Notes
- If keys are missing, the bot falls back to a minimal local response.
- NVD rate-limits; if lookups fail, retry later.
