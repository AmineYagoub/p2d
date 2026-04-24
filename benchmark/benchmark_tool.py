#!/usr/bin/env python3
"""P2D Benchmark Tool — Compares token consumption between standard and P2D-guided workflows."""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def chars_to_tokens(chars):
    """Approximate tokens from character count (standard ratio: 4 chars/token)."""
    return max(1, chars // 4)


def run_cmd(cmd, cwd=None):
    """Run a shell command and return stdout, returning empty string on failure."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=60
        )
        return result.stdout
    except (subprocess.TimeoutExpired, Exception):
        return ""


def has_ast_grep():
    """Check if ast-grep (sg) is available."""
    return bool(run_cmd("which sg").strip())


def find_source_files(repo_path, extensions):
    """Find source files matching given extensions."""
    files = []
    for ext in extensions:
        out = run_cmd(f'find "{repo_path}" -type f -name "*.{ext}" -not -path "*/node_modules/*" -not -path "*/.git/*"')
        if out.strip():
            files.extend(out.strip().split("\n"))
    return [f for f in files if f]


def standard_workflow(repo_path, symbol, extensions):
    """Simulate a standard agent workflow: grep + sequential file reads.

    Returns dict with token counts and details.
    """
    start = time.time()

    # Step 1: Broad grep to find candidate files
    ext_args = " ".join(f"--include='*.{e}'" for e in extensions)
    grep_output = run_cmd(f'grep -rn "{symbol}" {ext_args} "{repo_path}"')

    if not grep_output.strip():
        return {
            "mode": "standard",
            "tokens": 0,
            "files_read": 0,
            "matches": 0,
            "elapsed_s": round(time.time() - start, 2),
        }

    # Count matches
    match_lines = [l for l in grep_output.strip().split("\n") if l]
    matches = len(match_lines)

    # Step 2: Read each matched file fully (standard agents read whole files)
    matched_files = set()
    for line in match_lines:
        if ":" in line:
            filepath = line.split(":")[0]
            matched_files.add(filepath)

    total_chars = len(grep_output)  # grep output itself counts
    files_read = 0

    for filepath in sorted(matched_files):
        try:
            with open(filepath, "r", errors="replace") as f:
                content = f.read()
                total_chars += len(content)
                files_read += 1
        except (OSError, IOError):
            pass

    tokens = chars_to_tokens(total_chars)
    elapsed = round(time.time() - start, 2)

    return {
        "mode": "standard",
        "tokens": tokens,
        "files_read": files_read,
        "matches": matches,
        "elapsed_s": elapsed,
    }


def p2d_workflow(repo_path, symbol, extensions, language):
    """Simulate a P2D-guided workflow: ast-grep or targeted grep + summary.

    Returns dict with token counts and details.
    """
    start = time.time()
    sg_available = has_ast_grep()

    if sg_available:
        # Phase 1: ast-grep structural search (returns compact output)
        # Map common extensions to ast-grep language ids
        lang_map = {
            "ts": "typescript",
            "tsx": "tsx",
            "js": "javascript",
            "jsx": "javascript",
            "py": "python",
            "rs": "rust",
            "go": "go",
            "java": "java",
            "rb": "ruby",
        }
        sg_lang = lang_map.get(language, language)

        # Try ast-grep pattern for the symbol
        patterns = [
            f'"$SYM"' ,  # string literal match
        ]

        output = ""
        for pattern in patterns:
            out = run_cmd(
                f'sg -p {pattern} -l {sg_lang} --json "{repo_path}"',
                cwd=repo_path,
            )
            if out.strip():
                output = out
                break

        if not output.strip():
            # Fallback to targeted grep
            output = _targeted_grep(repo_path, symbol, extensions)
            used_ast_grep = False
        else:
            used_ast_grep = True
    else:
        # Fallback: targeted grep with file-type filtering
        output = _targeted_grep(repo_path, symbol, extensions)
        used_ast_grep = False

    # P2D only counts summary tokens, not raw file content
    if not output.strip():
        return {
            "mode": "p2d",
            "tokens": 0,
            "files_read": 0,
            "matches": 0,
            "used_ast_grep": sg_available and used_ast_grep,
            "elapsed_s": round(time.time() - start, 2),
        }

    match_lines = [l for l in output.strip().split("\n") if l]
    matches = len(match_lines)

    # P2D reads only the summary, not full files
    # Estimate summary as ~100 chars per match (filename + line number + context snippet)
    summary_chars = matches * 100
    tokens = chars_to_tokens(summary_chars)

    elapsed = round(time.time() - start, 2)

    return {
        "mode": "p2d",
        "tokens": tokens,
        "files_read": 0,  # P2D doesn't read full files
        "matches": matches,
        "used_ast_grep": sg_available and used_ast_grep,
        "elapsed_s": elapsed,
    }


def _targeted_grep(repo_path, symbol, extensions):
    """Targeted grep with file-type filtering (P2D fallback)."""
    ext_args = " ".join(f"--include='*.{e}'" for e in extensions)
    return run_cmd(f'grep -rn "{symbol}" {ext_args} "{repo_path}"')


def run_benchmark(repo_path, task, mode):
    """Run the benchmark for the given mode(s)."""
    symbol = task["symbol"]
    language = task.get("language", "ts")
    ext_map = {
        "ts": ["ts", "tsx"],
        "js": ["js", "jsx"],
        "py": ["py"],
        "rs": ["rs"],
        "go": ["go"],
        "java": ["java"],
        "rb": ["rb"],
    }
    extensions = ext_map.get(language, [language])

    results = {}

    if mode in ("standard", "both"):
        results["standard"] = standard_workflow(repo_path, symbol, extensions)

    if mode in ("p2d", "both"):
        results["p2d"] = p2d_workflow(repo_path, symbol, extensions, language)

    # Add comparison if both ran
    if "standard" in results and "p2d" in results:
        s_tokens = results["standard"]["tokens"]
        p_tokens = results["p2d"]["tokens"]
        if s_tokens > 0:
            savings_pct = round((1 - p_tokens / s_tokens) * 100, 1)
        else:
            savings_pct = 0.0
        results["comparison"] = {
            "token_savings_pct": savings_pct,
            "standard_tokens": s_tokens,
            "p2d_tokens": p_tokens,
            "files_avoided_reading": results["standard"]["files_read"],
        }

    return results


def main():
    parser = argparse.ArgumentParser(
        description="P2D Benchmark Tool — Compare token consumption between standard and P2D workflows"
    )
    parser.add_argument(
        "--repo", required=True, help="Target repository to analyze"
    )
    parser.add_argument(
        "--task", required=True, help="JSON task file describing the benchmark"
    )
    parser.add_argument(
        "--mode",
        choices=["standard", "p2d", "both"],
        default="both",
        help="Which mode(s) to run (default: both)",
    )
    parser.add_argument(
        "--output",
        default="results",
        help="Output directory for results (default: results/)",
    )
    args = parser.parse_args()

    # Validate inputs
    repo_path = os.path.abspath(args.repo)
    if not os.path.isdir(repo_path):
        print(f"Error: {repo_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    task_path = os.path.abspath(args.task)
    if not os.path.isfile(task_path):
        print(f"Error: {task_path} does not exist", file=sys.stderr)
        sys.exit(1)

    with open(task_path) as f:
        task = json.load(f)

    print(f"Benchmark: {task.get('name', 'unnamed')}")
    print(f"Symbol:    {task['symbol']}")
    print(f"Repo:      {repo_path}")
    print(f"Mode:      {args.mode}")
    print()

    results = run_benchmark(repo_path, task, args.mode)

    # Print results
    for mode_name, data in results.items():
        if mode_name == "comparison":
            continue
        print(f"[{mode_name.upper()}]")
        print(f"  Matches:    {data['matches']}")
        print(f"  Files read: {data['files_read']}")
        print(f"  Tokens:     {data['tokens']}")
        print(f"  Elapsed:    {data['elapsed_s']}s")
        if "used_ast_grep" in data:
            print(f"  ast-grep:   {'yes' if data['used_ast_grep'] else 'no (fallback)'}")
        print()

    if "comparison" in results:
        comp = results["comparison"]
        print(f"[COMPARISON]")
        print(f"  Token savings: {comp['token_savings_pct']}%")
        print(f"  Files avoided: {comp['files_avoided_reading']}")
        print()

    # Write results to output directory
    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    task_name = task.get("name", "benchmark").replace("/", "-")
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    result_file = os.path.join(output_dir, f"{task_name}-{timestamp}.json")

    output_data = {
        "task": task,
        "repo": repo_path,
        "timestamp": timestamp,
        "results": results,
    }

    with open(result_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Results written to: {result_file}")


if __name__ == "__main__":
    main()
