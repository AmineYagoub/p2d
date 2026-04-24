# P2D Benchmark Tool

Compares token consumption between a standard agent workflow and a P2D-guided workflow.

## Usage

```bash
python3 benchmark_tool.py --repo /path/to/target/repo --task tasks/find-usages.json
```

### Options

| Flag | Description |
|:-----|:------------|
| `--repo PATH` | Target repository to analyze (required) |
| `--task FILE` | JSON task file describing the benchmark (required) |
| `--mode {standard,p2d,both}` | Which mode(s) to run (default: both) |
| `--output PATH` | Output directory for results (default: results/) |

### Task File Format

```json
{
  "name": "find-usages-of-UserService",
  "description": "Find all files that import or reference UserService",
  "symbol": "UserService",
  "expected_files": 12,
  "expected_matches": 34,
  "language": "ts"
}
```

## How It Works

**Standard mode:** Simulates an agent reading files sequentially and searching with grep. Counts total characters read as approximate tokens (chars / 4).

**P2D mode:** Simulates a P2D-guided agent running ast-grep or targeted grep. Counts only the summary output tokens, not raw file content.

Results are written as JSON to the `results/` directory.

## Requirements

- Python 3.8+ (no external dependencies)
- ast-grep (`sg`) optional — P2D mode falls back to targeted grep if unavailable
