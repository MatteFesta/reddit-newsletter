# 🚀 The Weekly Sync

**AI-powered Reddit newsletter generator** — Curates the best posts from your favorite subreddits and delivers them as a beautiful email digest.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.0-orange?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 📡 **Multi-subreddit monitoring** — Track any number of subreddits
- 🧠 **AI-powered curation** — Gemini picks and summarizes the best stories
- 📧 **Beautiful HTML emails** — FT-style newsletter design
- ⚙️ **Configurable** — Edit `settings.yaml`, no code changes needed
- 🤖 **Automated scheduling** — GitHub Actions runs it every Monday
- 🎨 **Interactive CLI** — Rich terminal interface

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/reddit-newsletter.git
cd reddit-newsletter
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Gmail credentials (use App Password, NOT your regular password)
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_APP_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=recipient@example.com
```

### 3. Run

```bash
python main.py
```

You'll see an interactive menu:
```
[1] 📧 Generate & Send Newsletter
[2] 👀 Preview Only (No Email)
[3] ⚙️  View Current Settings
[4] 📂 Open Output Folder
[5] ❌ Exit
```

---

## ⚙️ Configuration

Edit `config/settings.yaml` to customize:

```yaml
subreddits:
  - LocalLLaMA
  - AI_Agents
  - MachineLearning
  # Add more...

fetch:
  posts_per_subreddit: 5
  time_period: week  # hour, day, week, month, year, all
```

---

## 📅 Automated Scheduling (GitHub Actions)

The workflow at `.github/workflows/weekly_newsletter.yml` runs automatically every **Monday at 9:00 AM** (Rome time).

### Setup Steps:

1. **Push this repo to GitHub**

2. **Add Secrets** in your GitHub repo:
   - Go to: `Settings` → `Secrets and variables` → `Actions`
   - Click `New repository secret` and add:
     - `GEMINI_API_KEY`
     - `EMAIL_ADDRESS`
     - `EMAIL_APP_PASSWORD`
     - `RECIPIENT_EMAIL`

3. **Done!** The newsletter will run automatically every Monday.

To run manually: Go to `Actions` tab → `Weekly Newsletter` → `Run workflow`

---

## 🔗 Important Links

### API & Billing

| Service | Link | Notes |
|---------|------|-------|
| **Google AI Studio** | [aistudio.google.com](https://aistudio.google.com/) | Get your Gemini API key |
| **Gemini API Pricing** | [ai.google.dev/pricing](https://ai.google.dev/pricing) | Free tier: 15 RPM, 1M tokens/min |
| **Google Cloud Console** | [console.cloud.google.com](https://console.cloud.google.com/) | Monitor usage & billing |
| **Gmail App Passwords** | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) | Generate app-specific password |

### GitHub Actions

| Link | Description |
|------|-------------|
| [Actions Usage](https://github.com/settings/billing) | Monitor your GitHub Actions minutes |
| [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions) | Documentation for customizing workflows |

---

## 📁 Project Structure

```
reddit-newsletter/
├── main.py                 # CLI entry point
├── config/
│   └── settings.yaml       # Configuration file
├── src/
│   ├── config_loader.py    # Loads YAML config
│   ├── reddit_fetcher.py   # Fetches posts from Reddit
│   ├── llm_analyzer.py     # Gemini AI integration
│   └── email_sender.py     # Gmail SMTP sender
├── output/
│   └── newsletters/        # Generated newsletters saved here
├── .github/
│   └── workflows/
│       └── weekly_newsletter.yml   # GitHub Actions automation
├── .env                    # Your secrets (NEVER commit this!)
├── .gitignore
├── requirements.txt
└── README.md              # You are here!
```

---

## 🔧 Troubleshooting

### "Rate limited" errors from Reddit
Reddit limits unauthenticated API requests. The script includes retry logic, but if issues persist:
- Reduce `posts_per_subreddit` in settings
- Increase `delay_between_requests`

### "Authentication failed" for email
- Make sure you're using a **Gmail App Password**, not your account password
- Enable 2FA on your Google account first
- Generate app password at: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### "GEMINI_API_KEY not found"
- Check your `.env` file exists and has correct format
- No spaces around `=` in `.env` file
- Get a key from [aistudio.google.com](https://aistudio.google.com/)

---

## 📝 License

MIT License — feel free to use and modify!

---

<p align="center">
  <i>Built with ☕ and 🤖 by an AI assistant</i>
</p>
