import re
from typing import Optional


def normalize_latex_content(s: str) -> str:
    """
    Fix common escaping issues from tool calls, especially '\\n' being used
    as a literal instead of a linebreak after '\\'.
    Example:
        '...May 2026\\\\nMaster...' -> '...May 2026\\\\\\nMaster...'
    """
    return s.replace("\\n", "\\\n")


def latex_preview(text: str) -> str:
    """
    Produce a human-friendly preview from LaTeX:
    - Strip preamble and document env markers
    - Render section headings as plain text
    - Render \\item lines as bullets
    - Skip comments and empty lines
    """
    lines = text.splitlines()
    out: list[str] = []

    section_cmds = ["section", "subsection", "subsubsection", "cvsection", "chapter", "sect"]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("%"):
            continue
        if stripped.startswith("\\documentclass"):
            continue
        if stripped.startswith("\\usepackage"):
            continue
        if stripped.startswith("\\begin{document}") or stripped.startswith("\\end{document}"):
            continue

        # Section-like commands: \section{Title}, \sect{Title}, etc.
        m = re.match(r"\\([a-zA-Z]+)\*?\{([^}]*)\}", stripped)
        if m and m.group(1) in section_cmds:
            title = m.group(2).strip()
            out.append("")
            out.append(title.upper())
            out.append("-" * len(title))
            continue

        # \item lines -> bullet points
        if stripped.startswith("\\item"):
            content = stripped[len("\\item"):].lstrip()
            out.append(f"- {content}")
            continue

        # Default: include line as-is
        out.append(stripped)

    return "\n".join(out).strip()


def extract_section_body(
    full_text: str,
    section_title: str,
    heading_command: str = "section",
) -> Optional[str]:
    """
    Extract the body of a LaTeX section given its title and heading command.
    Returns the body text or None if not found.
    """
    heading_cmd_escaped = re.escape(heading_command)
    title_escaped = re.escape(section_title)

    pattern = (
        rf"(\\{heading_cmd_escaped}\*?\{{{title_escaped}\}}\s*)"  # header
        rf"(.*?)"                                                # body
        rf"(?=("                                                 # lookahead: stop before next header/end
        rf"\\{heading_cmd_escaped}\b|"
        rf"\\section\b|"
        rf"\\subsection\b|"
        rf"\\chapter\b|"
        rf"\\cvsection\b|"
        rf"\\end\{{document\}}"
        rf"))"
    )

    regex = re.compile(pattern, re.DOTALL)
    m = regex.search(full_text)
    if not m:
        return None
    return m.group(2)


def strip_latex_to_plain(text: str) -> str:
    """
    Very simple LaTeX -> plain text cleaner.
    Keeps technical terms but removes most commands and markup.

    Works for resumes, research papers, theses, etc.
    """
    # Remove comments
    lines = []
    for line in text.splitlines():
        if line.strip().startswith("%"):
            continue
        lines.append(line)
    text = "\n".join(lines)

    # Turn \item into bullets
    text = re.sub(r"\\item\s*", "- ", text)

    # Keep contents of simple commands: \textbf{API} -> API
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^}]*)\}", r"\1", text)

    # Remove remaining backslash-commands without arguments: \textbf, \emph, etc.
    text = re.sub(r"\\[a-zA-Z]+(\*?)", "", text)

    # Replace multiple spaces/newlines with single spaces/newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()
