"""
Run the whole analysis, in order, from the raw files to the figures.

    .venv/bin/python python/run_all.py

Every random draw is seeded from config.SEED, so a rerun reproduces the tables
exactly. The bootstrap in tailrisk.py is the slow step.
"""

from __future__ import annotations

import importlib
import json
import platform
import sys
import time

import config

STEPS = [
    ("Build the US family file from MEPS", "build_meps"),
    ("Put Nigeria on the harmonised basis", "build_nigeria"),
    ("Harmonised catastrophic spending", "burden"),
    ("Tail risk: VaR, CVaR and GPD fits", "tailrisk"),
    ("Parity and crossover", "parity"),
    ("Figures", "exhibits"),
]


def main():
    started = time.time()
    timings = []
    for title, module in STEPS:
        print("\n" + "=" * 78)
        print(title)
        print("=" * 78)
        t0 = time.time()
        importlib.import_module(module).main()
        dt = time.time() - t0
        timings.append({"step": title, "module": module, "seconds": round(dt, 1)})
        print(f"[{title}: {dt:.1f}s]")

    import numpy, pandas, scipy, matplotlib
    params = {k: v for k, v in vars(config).items()
              if k.isupper() and isinstance(v, (int, float, str, bool,
                                                tuple, list, dict, type(None)))}
    (config.ROOT / "output" / "params_used.json").write_text(json.dumps({
        "params": {k: (str(v) if isinstance(v, (tuple, list, dict)) else v)
                   for k, v in params.items()},
        "versions": {"python": platform.python_version(),
                     "numpy": numpy.__version__, "pandas": pandas.__version__,
                     "scipy": scipy.__version__,
                     "matplotlib": matplotlib.__version__},
        "timings": timings,
    }, indent=2, default=str))

    total = time.time() - started
    print("\n" + "=" * 78)
    print(f"Done in {total:.0f}s. Tables in "
          f"{config.TABLES.relative_to(config.ROOT)}, figures in "
          f"{config.FIGURES.relative_to(config.ROOT)}.")


if __name__ == "__main__":
    sys.exit(main())
