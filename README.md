# 📓 NotebookLM Assistant for Claude (Desktop & CLI)

This project provides a powerful MCP (Model Context Protocol) server that brings the full power of Google NotebookLM into Claude. 

## ✨ Features
- **Research**: List and create notebooks.
- **Content**: Add URLs, text, and files as sources.
- **Generation**: Create Podcasts, Videos, Slides, Mind Maps, Infographics, Quizzes, Flashcards, and Reports.
- **Natural Interaction**: Chat directly with your sources using Claude's reasoning.

---

## 🚀 Step 1: Initialize & Authenticate

Since NotebookLM uses undocumented APIs, you must authenticate once to save your session cookies.

```bash
# 1. Navigate to the project folder
cd /Users/alfredang/projects/notebooklm-assistant

# 2. Login to Google
uv run notebooklm login
```
*A browser will open. Log in to Google, go to NotebookLM, and once the terminal says "Success", you can close the browser.*

---

## 🖥️ Step 2: Setup for Claude Desktop (GUI)

1. Open your Claude Desktop configuration file:
   - **Path**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add (or update) the following configuration:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/alfredang/projects/notebooklm-assistant",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```
3. **Restart Claude Desktop** (fully quit and reopen). You should see the hammer icons for NotebookLM tools.

---

## 💻 Step 3: Setup for Claude Code (CLI)

To use NotebookLM tools in your terminal via Claude Code, run this command once:

```bash
claude mcp add notebooklm "uv --directory /Users/alfredang/projects/notebooklm-assistant run python server.py"
```

### Optional: Install as an Agent Skill
If you want Claude Code to have a "instruction manual" for these tools, run:
```bash
cd /Users/alfredang/projects/notebooklm-assistant
uv run notebooklm skill install
```

---

## 🛠️ Usage Examples

**In Claude Desktop or Claude Code, you can now say:**

- *"Create a **Mind Map** for my 'Project Alpha' notebook."*
- *"Generate a **Deep Dive Podcast** based on these three URLs: [URLs]."*
- *"Summarize my notebook and create a **Quiz** to test my knowledge."*
- *"Make a **Slide Deck** about the key trends in this research."*

---

## 🔧 Troubleshooting
- **Session Exppired**: If tools stop working, run `uv run notebooklm login` again.
- **Updating**: To pull the latest library changes, run `uv sync`.
- **Logs**: If you encounter errors, check the Claude Desktop logs in `~/Library/Logs/Claude/`.
