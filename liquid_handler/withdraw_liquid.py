"""Withdraw a user-specified volume of liquid and discard the tip.

Workflow:
  1. A popup window asks the user how many microliters (uL) to withdraw.
  2. The liquid handler picks up a tip, aspirates that volume from the
     source well, and discards the tip into the trash.

Built on PyLabRobot (https://docs.pylabrobot.org), which supports many
liquid handler brands (Hamilton, Tecan, Opentrons, ...) through a common
API. This script runs in SIMULATION by default (no hardware required) so
you can try it out safely. To run on real hardware, see "Switching to
real hardware" below.
"""

import asyncio
import tkinter as tk
from tkinter import simpledialog

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import LiquidHandlerChatterboxBackend
from pylabrobot.resources import (
    TIP_CAR_480_A00,
    PLT_CAR_L5AC_A00,
    STARLetDeck,
    hamilton_96_tiprack_300uL_filter,
)
from pylabrobot.resources.corning import cor_96_wellplate_360uL_Fb

# Well the liquid handler withdraws from, and the tip position it uses.
# Change these to match your physical deck layout.
SOURCE_WELL = "A1"
TIP_SPOT = "A1"


def ask_volume_ul() -> float | None:
    """Pop up a window asking the user for a volume in uL.

    Returns the entered volume, or None if the user cancelled.
    """
    root = tk.Tk()
    root.withdraw()  # only show the dialog, not an empty main window
    volume = simpledialog.askfloat(
        title="Withdraw Liquid",
        prompt="Enter volume to withdraw (uL):",
        minvalue=0.1,
        maxvalue=1000.0,
        parent=root,
    )
    root.destroy()
    return volume


async def withdraw_and_discard(volume_ul: float) -> None:
    """Pick up a tip, aspirate volume_ul from the source well, discard the tip."""
    deck = STARLetDeck()

    tip_carrier = TIP_CAR_480_A00(name="tip carrier")
    tip_carrier[0] = tip_rack = hamilton_96_tiprack_300uL_filter(name="tip rack")
    deck.assign_child_resource(tip_carrier, rails=1)

    plate_carrier = PLT_CAR_L5AC_A00(name="plate carrier")
    plate_carrier[0] = source_plate = cor_96_wellplate_360uL_Fb(name="source plate")
    deck.assign_child_resource(plate_carrier, rails=9)

    # LiquidHandlerChatterboxBackend just prints each command -- swap this
    # out for a real backend to run on hardware (see module docstring).
    lh = LiquidHandler(backend=LiquidHandlerChatterboxBackend(), deck=deck)
    await lh.setup()

    try:
        await lh.pick_up_tips(tip_rack[TIP_SPOT])
        await lh.aspirate(source_plate[SOURCE_WELL], vols=[volume_ul])
        await lh.discard_tips()
    finally:
        await lh.stop()


def main() -> None:
    volume_ul = ask_volume_ul()
    if volume_ul is None:
        print("Cancelled -- no volume entered.")
        return

    print(f"Withdrawing {volume_ul} uL...")
    asyncio.run(withdraw_and_discard(volume_ul))
    print("Done: tip discarded.")


if __name__ == "__main__":
    main()

# --- Switching to real hardware -------------------------------------------
# 1. Replace LiquidHandlerChatterboxBackend() above with the backend for
#    your instrument, e.g.:
#      from pylabrobot.liquid_handling.backends import STAR   # Hamilton STAR
#      lh = LiquidHandler(backend=STAR(), deck=deck)
#    or:
#      from pylabrobot.liquid_handling.backends import EVO    # Tecan EVO
#      lh = LiquidHandler(backend=EVO(), deck=deck)
# 2. Update SOURCE_WELL, TIP_SPOT, and the deck/resource setup in
#    withdraw_and_discard() to match your actual deck layout (labware
#    types and rail/carrier positions).
# 3. See https://docs.pylabrobot.org for the full list of supported
#    backends and how to configure each one (USB/network connection, etc).
