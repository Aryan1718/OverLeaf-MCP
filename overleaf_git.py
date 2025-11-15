import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse, urlunparse, quote

# Overleaf configuration
OVERLEAF_GIT_URL = os.environ.get("OVERLEAF_GIT_URL")
OVERLEAF_TOKEN = os.environ.get("OVERLEAF_TOKEN")
OVERLEAF_EMAIL = os.environ.get("OVERLEAF_EMAIL")


def run(cmd, cwd=None):
    """
    Run a shell command and capture stderr/stdout so we can see git errors.
    """
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"returncode: {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return result


def get_git_email() -> str:
    """
    Return email to use for git commits.
    """
    return OVERLEAF_EMAIL or "overleaf-mcp@example.com"


def clone_overleaf_repo() -> Path:
    """
    Clone the Overleaf Git repository using the Git auth token.

    OVERLEAF_GIT_URL should be the plain project URL, e.g.:
        https://git.overleaf.com/<project-id>

    OVERLEAF_TOKEN is your Git authentication token from Overleaf.
    """
    if not OVERLEAF_GIT_URL or not OVERLEAF_TOKEN:
        raise RuntimeError(
            "Missing Overleaf configuration. Set OVERLEAF_GIT_URL and "
            "OVERLEAF_TOKEN environment variables."
        )

    if not OVERLEAF_GIT_URL.startswith("https://"):
        raise RuntimeError("OVERLEAF_GIT_URL must start with https://")

    # Create temp dir and keep a global reference so it's not cleaned up early
    tmpdir = tempfile.TemporaryDirectory()
    repo_dir = Path(tmpdir.name) / "project"
    if "_TMPDIRS" not in globals():
        globals()["_TMPDIRS"] = []
    globals()["_TMPDIRS"].append(tmpdir)

    # Parse the base URL (e.g. https://git.overleaf.com/<project-id>)
    parsed = urlparse(OVERLEAF_GIT_URL)
    if not parsed.hostname:
        raise RuntimeError(f"Invalid OVERLEAF_GIT_URL: {OVERLEAF_GIT_URL}")

    # Overleaf expects: username "git", password = token.
    # We embed that as: https://git:<token>@git.overleaf.com/<project-id>
    user = "git"
    password = quote(OVERLEAF_TOKEN, safe="")

    host = parsed.hostname
    netloc = f"{user}:{password}@{host}"
    if parsed.port:
        netloc += f":{parsed.port}"

    auth_url = urlunparse(parsed._replace(netloc=netloc))

    # Perform git clone
    run(["git", "clone", auth_url, str(repo_dir)])

    return repo_dir
