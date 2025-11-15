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

🧩 Available Tools
1. read_overleaf_file
Read a file from the project.

Parameters

path: file path (e.g., "main.tex")

raw:

true → full LaTeX

false → human-friendly preview

Example

lua
Copy code
read_overleaf_file(path="main.tex", raw=true)
2. list_overleaf_files
List all files inside the Overleaf repository.

Example

scss
Copy code
list_overleaf_files()
3. update_overleaf_section
Safely update ONLY a specific LaTeX section.

Parameters

path — file to modify

section_title — section title inside {}

heading_command — macro name (section, sect, subsection, etc.)

new_section_body — replacement LaTeX body

commit_message — optional commit message

Example

swift
Copy code
update_overleaf_section(
  path="resume.tex",
  section_title="PROJECTS",
  heading_command="sect",
  new_section_body="\\begin{enumerate}\n\\item New project...\n\\end{enumerate}",
  commit_message="Update PROJECTS section"
)
💬 Using the Server in ChatGPT
How to add MCP server
Open Settings → Developer → MCP Clients → Add Server

Add your MCP server URL (http://localhost:8000 or your FastMCP cloud URL)

ChatGPT will automatically load:

read_overleaf_file

list_overleaf_files

update_overleaf_section

Example Workflow (Resume Editing)
You:

Read the PROJECTS section from my resume.

ChatGPT calls:

lua
Copy code
read_overleaf_file(path="resume.tex", raw=true)
You:

Replace only the first project with this new one.

ChatGPT calls:

scss
Copy code
update_overleaf_section(...)
Only that section updates. Everything else stays untouched.

🤖 Using the Server in Claude
Claude Desktop
Open Claude Desktop

Go to Settings → Integrations → Add MCP Server

Use command:

arduino
Copy code
fastmcp run server.py
Add your environment variables under the integration settings.

Claude Web (Browser)
If your account has MCP enabled:

Go to Settings → MCP Servers

Add server → choose “Local binary” or “HTTP server”

Claude will automatically detect your tools

🛡 Why This Method Is Safe
No full-file overwrites

Only the specified section’s body is changed

Perfect for long papers, academic templates, and resumes

Prevents LaTeX formatting corruption

Keeps original spacing, macros, and structure intact

📚 Works Best For
Resumes / CVs

Research papers

Multi-section reports

University assignments

Theses / dissertations

Books with multiple .tex files

ACM / IEEE / Springer templates

🚀 Future Enhancements
Insert new sections

Delete sections

Rename LaTeX sections

Compile + return PDF preview

Automatic backup commits
