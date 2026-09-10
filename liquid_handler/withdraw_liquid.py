"""Generate a Tecan Fluent worklist that withdraws a user-specified volume
and discards the tip.

The Tecan Fluent is controlled via FluentControl, not by driving the
instrument directly from Python. The standard way to script it is to
write a GWL ("worklist") file -- a plain-text file of Aspirate/Dispense/
Wash commands -- and run it from a "Worklist" step inside a FluentControl
method. This script does exactly that:

  1. A popup window asks the user for a volume (uL) and a liquid class.
  2. A .gwl file is written with one Aspirate command for that volume/
     liquid class, followed by a Wash command (which, for disposable
     tips, ejects the tip).
  3. You load/run the generated .gwl file from a Worklist step in
     FluentControl.

See https://www.tecan.com/knowledge-portal/how-to-use-worklist-in-fluentcontrol
for how a Worklist step consumes a .gwl file.
"""

import tkinter as tk
from tkinter import messagebox, ttk

# Labware label and position the volume is withdrawn from. These must
# match the RackLabel and Position of a labware item placed on your
# Fluent worktable/method -- edit to match your actual setup.
SOURCE_LABWARE = "SourcePlate"
SOURCE_POSITION = 1

OUTPUT_PATH = "withdraw.gwl"

# Common built-in Tecan liquid class names, shown as a starting point.
# Each one MUST exactly match (case-sensitive) a liquid class that
# actually exists in your FluentControl liquid class database (Liquid
# Editor) -- otherwise the worklist step will fail when it runs. Replace
# this list with your own liquid classes.
LIQUID_CLASSES = [
    "Water free dispense",
    "Water free dispense (with clld)",
    "DMSO free dispense",
    "Ethanol 100% free dispense",
    "Serum free dispense",
]


def ask_volume_and_liquid_class():
    """Pop up a window asking for a volume (uL) and a liquid class.

    Returns a (volume_ul, liquid_class) tuple, or None if cancelled.
    """
    result = {}
    root = tk.Tk()
    root.title("Withdraw Liquid")

    tk.Label(root, text="Volume to withdraw (uL):").grid(
        row=0, column=0, padx=8, pady=8, sticky="w"
    )
    volume_entry = tk.Entry(root)
    volume_entry.grid(row=0, column=1, padx=8, pady=8)

    tk.Label(root, text="Liquid class:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
    liquid_class_box = ttk.Combobox(root, values=LIQUID_CLASSES, state="readonly")
    liquid_class_box.current(0)
    liquid_class_box.grid(row=1, column=1, padx=8, pady=8)

    def on_ok():
        try:
            volume = float(volume_entry.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Enter a numeric volume in uL.")
            return
        if volume <= 0:
            messagebox.showerror("Invalid input", "Volume must be greater than 0.")
            return
        result["volume_ul"] = volume
        result["liquid_class"] = liquid_class_box.get()
        root.destroy()

    button_frame = tk.Frame(root)
    button_frame.grid(row=2, column=0, columnspan=2, pady=8)
    tk.Button(button_frame, text="OK", command=on_ok).pack(side="left", padx=4)
    tk.Button(button_frame, text="Cancel", command=root.destroy).pack(side="left", padx=4)

    volume_entry.focus_set()
    root.mainloop()

    if "volume_ul" not in result:
        return None
    return result["volume_ul"], result["liquid_class"]


def build_gwl(volume_ul: float, liquid_class: str) -> str:
    """Build GWL text: aspirate volume_ul with liquid_class, then discard the tip.

    Record format (Tecan GWL spec):
      A;RackLabel;RackID;RackType;Position;TubeID;Volume;LiquidClass;TipType;TipMask;ForcedRackType
    RackID, RackType, TubeID, TipType, TipMask and ForcedRackType are left
    blank to use defaults / the labware's own type.
    """
    aspirate = f"A;{SOURCE_LABWARE};;;{SOURCE_POSITION};;{volume_ul};{liquid_class};;;"
    wash = "W;"
    return f"{aspirate}\n{wash}\n"


def main() -> None:
    answer = ask_volume_and_liquid_class()
    if answer is None:
        print("Cancelled -- no worklist generated.")
        return

    volume_ul, liquid_class = answer
    gwl_text = build_gwl(volume_ul, liquid_class)

    with open(OUTPUT_PATH, "w") as f:
        f.write(gwl_text)

    print(f"Wrote {OUTPUT_PATH}:")
    print(gwl_text)
    print("Run this from a Worklist step in a FluentControl method.")


if __name__ == "__main__":
    main()
