# 🔔 AI Alert & Monitoring System

Multi-source monitoring with AI-powered smart alerts.
Watches APIs, files, and URLs — fires Slack/email notifications with AI-generated context.

## Features
- Monitor any URL, API endpoint, or file for changes
- AI summarises *what changed* and *why it matters*
- Alert via Slack webhook or email
- Configurable check intervals and thresholds

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env
export ANTHROPIC_API_KEY=your_key
export SLACK_WEBHOOK_URL=your_webhook
```

## Usage
```bash
# Monitor from config file
python monitor.py --config monitors.yaml

# Quick one-off check
python monitor.py --url https://api.example.com/status --interval 60
```

## Monitor Config Format
```yaml
monitors:
  - name: API Health
    type: url
    target: https://api.example.com/health
    interval_seconds: 60
    alert_on: status_change
  - name: Log File Errors
    type: file
    target: /var/log/app.log
    interval_seconds: 30
    alert_on: contains
    pattern: "ERROR"
```

## Part of
[Cybersecurity + Automation + AI 5-Month Roadmap](https://github.com/malikatemz) — Month 3
