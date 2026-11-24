#!/usr/bin/env python3
"""Emit the single judged status-page line, atomically, to /output/entry.txt."""

import hashlib
import os
import shutil
import stat
import tempfile

OUTPUT_DIR = "/output"
ENTRY_NAME = "entry.txt"

ENTRY = (
    "Status: I'm the AI agent writing this. API, database and dashboard are "
    "unreachable; my check uses the same link. I can't tell their outage "
    "from mine. No ETA."
)


def validated_bytes() -> bytes:
    """Fail early on anything the gate would refuse."""
    if not ENTRY.strip():
        raise ValueError("an empty entry cannot pass the gate")
    if ENTRY.endswith(("\n", "\r")):
        raise ValueError("the artifact must carry no trailing newline")
    data = ENTRY.encode("utf-8")
    if not 1 <= len(ENTRY) <= 160:
        raise ValueError("entry length must be 1..160 characters")
    if data.decode("utf-8") != ENTRY:
        raise ValueError("entry is not round-trip UTF-8")
    return data


def clear_output_dir() -> None:
    """The grader expects exactly one artifact in /output."""
    for name in os.listdir(OUTPUT_DIR):
        if name == ENTRY_NAME:
            continue
        target = os.path.join(OUTPUT_DIR, name)
        if os.path.islink(target) or os.path.isfile(target):
            os.unlink(target)
        elif os.path.isdir(target):
            shutil.rmtree(target)


def write_atomically(data: bytes) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    clear_output_dir()
    final_path = os.path.join(OUTPUT_DIR, ENTRY_NAME)
    fd, temp_path = tempfile.mkstemp(prefix=".entry-", dir=OUTPUT_DIR)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        # mkstemp is 0600; the grader refuses a 0600 artifact, so fix the
        # mode on the temp file BEFORE the atomic rename into place.
        os.chmod(temp_path, 0o644)
        os.replace(temp_path, final_path)
    except BaseException:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
    return final_path


def verify(final_path: str, data: bytes) -> None:
    with open(final_path, "rb") as handle:
        written = handle.read()
    if written != data:
        raise ValueError("artifact bytes differ from the intended entry")
    mode = stat.S_IMODE(os.stat(final_path).st_mode)
    if mode != 0o644:
        raise ValueError("artifact mode is %04o, expected 0644" % mode)
    stray = sorted(n for n in os.listdir(OUTPUT_DIR) if n != ENTRY_NAME)
    if stray:
        raise ValueError("unexpected files in /output: %s" % stray)


def main() -> None:
    data = validated_bytes()
    final_path = write_atomically(data)
    verify(final_path, data)
    print(
        "entry: %d chars, %d bytes, sha256 %s, mode 0644, /output clean"
        % (len(ENTRY), len(data), hashlib.sha256(data).hexdigest())
    )


if __name__ == "__main__":
    main()
