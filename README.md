# Eclipse Battle Simulator

Monte Carlo battle simulator for the board game **Eclipse: Second Dawn for the Galaxy**.
Configure two opposing fleets, run thousands of simulated battles, and get win probabilities,
average survivors, and round-count statistics.

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** for dependency management

## Getting Started

```bash
# Install dependencies
uv sync

# Launch the web UI
uv run streamlit run presentation/app.py

# Run the test suite
uv run python -m pytest tests/ -v
```
