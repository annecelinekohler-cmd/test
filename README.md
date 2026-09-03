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

## Liquid handler: withdraw & discard

`liquid_handler/withdraw_liquid.py` pops up a window asking for a volume
in uL, then withdraws that volume with the liquid handler and discards
the tip into the wash station's waste port. Built on
[PyLabRobot](https://docs.pylabrobot.org) targeting a **Tecan Freedom
EVO** (150 deck by default) with a 100uL disposable tip.

```bash
python liquid_handler/withdraw_liquid.py
```

By default it runs in **simulation** (prints each command, no hardware
needed) so you can try it safely. To run on real hardware, edit the
backend and deck layout — instructions are in the comments at the bottom
of the script. In short: swap in the real `EVO` backend (talks to the
instrument over USB via the same driver EVOware uses, so it must run on
the Windows PC connected to the liquid handler), and adjust the tip
rack/plate/carrier resources and rail positions to match your actual
deck layout and tip volume.

Tkinter (used for the popup) ships with most Python installs. If you get
`ModuleNotFoundError: No module named 'tkinter'`, install it via your
system package manager, e.g. `sudo apt install python3-tk` on
Debian/Ubuntu (macOS and Windows installers include it by default).
