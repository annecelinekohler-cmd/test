# Python Data Analysis Starter

A minimal example project for doing data analysis in Python with pandas.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python analysis.py
```

This loads `data/sales_sample.csv`, computes total units and revenue per
region, prints the summary, and saves a bar chart to
`output/revenue_by_region.png`.

## Structure

- `data/` — input datasets (CSV)
- `output/` — generated charts and results
- `analysis.py` — the analysis script
- `liquid_handler/` — liquid handler control script (see below)

## Liquid handler: withdraw & discard (Tecan Fluent)

`liquid_handler/withdraw_liquid.py` targets a **Tecan Fluent**. Fluent
isn't driven directly from Python the way some other liquid handlers
are — it's controlled through Tecan's FluentControl software, which runs
worklists: plain-text `.gwl` files listing Aspirate/Dispense/Wash
commands. So the script:

1. Pops up a window asking for a volume (uL) **and** a liquid class
   (dropdown).
2. Writes `withdraw.gwl` with one Aspirate command for that volume/liquid
   class, followed by a Wash command (which ejects the tip for
   disposable-tip setups).

```bash
python liquid_handler/withdraw_liquid.py
```

Then, in FluentControl, add a **Worklist** step to your method and point
it at the generated `withdraw.gwl` file to actually run it — see
[How to use worklist in FluentControl](https://www.tecan.com/knowledge-portal/how-to-use-worklist-in-fluentcontrol).

Before using this for real, edit the constants at the top of the script:

- `SOURCE_LABWARE` / `SOURCE_POSITION` — must match a labware item's
  RackLabel and Position in your actual Fluent method/worktable.
- `LIQUID_CLASSES` — these are just common Tecan liquid class names as a
  starting point. Each one must exactly match (case-sensitive) a liquid
  class that actually exists in your FluentControl Liquid Editor, or the
  worklist step will fail when it runs.

Tkinter (used for the popup) ships with most Python installs. If you get
`ModuleNotFoundError: No module named 'tkinter'`, install it via your
system package manager, e.g. `sudo apt install python3-tk` on
Debian/Ubuntu (macOS and Windows installers include it by default). Note
that GUI popups need a real display — they won't work in a headless
environment like a cloud dev container (e.g. GitHub Codespaces without a
virtual desktop).
