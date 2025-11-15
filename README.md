# Overleaf MCP Server

A Model Context Protocol (MCP) server that allows AI assistants (ChatGPT, Claude, and other MCP-compatible models) to **read**, **list**, and **update specific LaTeX sections** in Overleaf projects directly from chat — with no copy/paste and no risk of breaking formatting.

This server is designed for resumes, research papers, theses, reports, and any LaTeX files stored in Overleaf.

---

## ✨ Features

- **Read any LaTeX file**
  - Preview mode (clean readable text)
  - Raw mode (full LaTeX source)

- **List all files in the Overleaf project**

- **Update ONLY a specific LaTeX section**
  - Safe: only the section body is replaced
  - Everything else stays byte-for-byte identical

- **No full-file overwriting**
  - Prevents formatting loss or breaking templates

---

## 📦 Installation

### 1. Install FastMCP
```bash
pip install fastmcp
```

### 2. Clone this repository
```bash
git clone <your-repo-url>
cd overleaf-mcp-server
```

### 3. Configure environment variables
Find your Overleaf project's Git URL:
Overleaf → Menu → Git → "Clone this project via Git"

Set the following:

```bash
export OVERLEAF_GIT_URL="https://git.overleaf.com/<project-id>"
export OVERLEAF_TOKEN="olp_your_access_token"
```

Required:

OVERLEAF_GIT_URL — Overleaf Git HTTPS URL

OVERLEAF_TOKEN — Overleaf Git access token


### 4. Run the MCP server
```bash
fastmcp run server.py
```
