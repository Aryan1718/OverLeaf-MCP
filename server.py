import os
from pathlib import Path
from typing import Optional
import re

from fastmcp import FastMCP

from overleaf_git import clone_overleaf_repo, run, get_git_email
from latex_utils import (
    normalize_latex_content,
    latex_preview,
    extract_section_body,
    strip_latex_to_plain,
)

# MCP server instance
mcp = FastMCP("overleaf-mcp")


@mcp.tool
def read_overleaf_file(
    path: str = "main.tex",
    raw: bool = False,
) -> str:
    """
    Read a file from the Overleaf project.

    Parameters
    ----------
    path : str
        Relative path to the file inside the Overleaf repo.
    raw : bool
        If True, return full LaTeX source.
        If False, return a human-friendly preview.
    """
    try:
        repo_dir = clone_overleaf_repo()
    except Exception as e:
        return f"Git clone failed:\n{e}"

    file_path = repo_dir / path

    if not file_path.exists():
        return f"File '{path}' does not exist in the Overleaf project."

    content = file_path.read_text(encoding="utf-8")

    if raw:
        return content

    return latex_preview(content)


@mcp.tool
def list_overleaf_files() -> list[str]:
    """
    List all files in the Overleaf project (recursively).
    Does NOT include .git directory.
    Returns a list of relative file paths.
    """
    try:
        repo_dir = clone_overleaf_repo()
    except Exception as e:
        return [f"Git clone failed: {e}"]

    file_paths: list[str] = []

    for root, dirs, files in os.walk(repo_dir):
        # Skip .git
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            full_path = Path(root) / file
            rel_path = full_path.relative_to(repo_dir)
            file_paths.append(str(rel_path))

    return file_paths


@mcp.tool
def update_overleaf_section(
    path: str,
    section_title: str,
    new_section_body: str,
    heading_command: str = "section",
    commit_message: Optional[str] = None,
) -> str:
    """
    Replace ONLY the body of a LaTeX section with a given title, and push changes.

    This is the ONLY write tool. It:
      - Reads the file.
      - Finds the matching section header.
      - Replaces only the body of that section.
      - Leaves everything else in the file untouched.

    Parameters
    ----------
    path : str
        File to edit, e.g. "test.tex" or "ARYAN-PANDIT-RESUME-2/dothis.tex".
    section_title : str
        The exact title of the section, e.g. "PROJECTS", "TECHNICAL SKILLS",
        "Introduction", "Methodology", etc.
    heading_command : str
        The LaTeX command used for the section header.
        Examples:
          - "section"  -> matches \section{PROJECTS}
          - "sect"     -> matches \sect{PROJECTS} (custom macro)
    new_section_body : str
        New content for that section (LaTeX). Only the body is replaced.
    commit_message : str | None
        Optional git commit message.
    """
    try:
        repo_dir = clone_overleaf_repo()
    except Exception as e:
        return f"Git clone failed:\n{e}"

    file_path = repo_dir / path
    if not file_path.exists():
        return f"File '{path}' does not exist in the Overleaf project."

    text = file_path.read_text(encoding="utf-8")

    heading_cmd_escaped = re.escape(heading_command)
    title_escaped = re.escape(section_title)

    # Match:
    #   \sect{TITLE}<whitespace>BODY_UP_TO_NEXT_SECTION_OR_END
    # or
    #   \section{TITLE}...
    pattern = (
        rf"(\\{heading_cmd_escaped}\*?\{{{title_escaped}\}}\s*)"  # group 1: header
        rf"(.*?)"                                                # group 2: body
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

    # Normalize new section body before inserting (fix \n issues)
    new_section_body = normalize_latex_content(new_section_body)

    def replacer(match: re.Match) -> str:
        header = match.group(1)
        body = new_section_body.strip() + "\n"
        return header + body

    new_text, count = regex.subn(replacer, text, count=1)

    if count == 0:
        return (
            f"Section '{section_title}' with heading '\\{heading_command}' "
            f"not found in '{path}'. No changes made."
        )

    file_path.write_text(new_text, encoding="utf-8")

    email = get_git_email()
    run(["git", "config", "user.name", "Overleaf MCP Bot"], cwd=repo_dir)
    run(["git", "config", "user.email", email], cwd=repo_dir)

    run(["git", "add", path], cwd=repo_dir)

    if commit_message is None:
        commit_message = f"Update section '{section_title}' in {path}"

    try:
        run(["git", "commit", "-m", commit_message], cwd=repo_dir)
    except RuntimeError:
        return "No changes to commit after section replacement."

    try:
        run(["git", "push", "origin", "main"], cwd=repo_dir)
    except RuntimeError:
        run(["git", "push", "origin", "master"], cwd=repo_dir)

    return (
        f"Successfully updated section '{section_title}' in '{path}' "
        f"and pushed to Overleaf."
    )


@mcp.tool
def summarize_overleaf_section(
    path: str,
    section_title: str,
    heading_command: str = "section",
    max_sentences: int = 3,
) -> str:
    """
    Summarize a specific LaTeX section in simple language.

    - Keeps important technical words.
    - Returns a short summary plus one example line if possible.

    Works for resumes, research papers, and theses.
    """
    try:
        repo_dir = clone_overleaf_repo()
    except Exception as e:
        return f"Git clone failed:\n{e}"

    file_path = repo_dir / path
    if not file_path.exists():
        return f"File '{path}' does not exist in the Overleaf project."

    full_text = file_path.read_text(encoding="utf-8")
    body = extract_section_body(full_text, section_title, heading_command)

    if body is None:
        return (
            f"Section '{section_title}' with heading '\\{heading_command}' "
            f"not found in '{path}'."
        )

    plain = strip_latex_to_plain(body)

    if not plain:
        return f"Section '{section_title}' is empty or could not be parsed."

    # Very simple sentence splitting
    sentences = re.split(r"(?<=[.!?])\s+", plain)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return plain

    summary_sentences = sentences[:max_sentences]
    summary = " ".join(summary_sentences)

    # Try to pick one concrete example line:
    lines = [l.strip() for l in plain.splitlines() if l.strip()]
    bullet_lines = [l for l in lines if l.startswith("- ")]
    if bullet_lines:
        example = bullet_lines[0]
    elif len(sentences) > 1:
        example = sentences[1]
    else:
        example = sentences[0]

    result_parts = [
        f"Summary of '{section_title}':",
        summary,
        "",
        "Example:",
        example,
    ]
    return "\n".join(result_parts).strip()


if __name__ == "__main__":
    mcp.run()
