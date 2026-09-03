"""Withdraw a user-specified volume of liquid and discard the tip.

Workflow:
  1. A popup window asks the user how many microliters (uL) to withdraw.
  2. The liquid handler picks up a tip, aspirates that volume from the
     source well, and discards the tip into the wash station's waste port.

Built on PyLabRobot (https://docs.pylabrobot.org) targeting a Tecan
Freedom EVO liquid handler. This script runs in SIMULATION by default
(no hardware required) so you can try it out safely. To run on real
hardware, see "Switching to real hardware" below.
"""

import asyncio
import tkinter as tk
from tkinter import simpledialog

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import LiquidHandlerChatterboxBackend
from pylabrobot.resources.tecan import (
    EVO150Deck,
    DiTi_SBS_3_Pos_MCA96,
    DiTi_100ul_Te_MO,
    MP_3Pos_PCR,
    DeepWell_96_Well,
)

# Well the liquid handler withdraws from, and the tip position it uses.
# Change these -- along with the deck layout in withdraw_and_discard() --
# to match your physical deck.
SOURCE_WELL = "A1"
TIP_SPOT = "A1"

# The tip type below (DiTi_100ul_Te_MO) holds up to 110 uL -- keep the
# popup's max in sync with whatever tip you actually use.
MAX_VOLUME_UL = 100.0


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
        maxvalue=MAX_VOLUME_UL,
        parent=root,
    )
    root.destroy()
    return volume


async def withdraw_and_discard(volume_ul: float) -> None:
    """Pick up a tip, aspirate volume_ul from the source well, discard the tip."""
    # with_wash_station=True (the default) gives the deck a wash station
    # with a waste port we use as the tip trash.
    deck = EVO150Deck()

    tip_carrier = DiTi_SBS_3_Pos_MCA96(name="tip carrier")
    tip_carrier[0] = tip_rack = DiTi_100ul_Te_MO(name="tip rack")
    deck.assign_child_resource(tip_carrier, rails=10)

    plate_carrier = MP_3Pos_PCR(name="plate carrier")
    plate_carrier[0] = source_plate = DeepWell_96_Well(name="source plate")
    deck.assign_child_resource(plate_carrier, rails=16)

    waste = deck.get_resource("wash_waste")

    # LiquidHandlerChatterboxBackend just prints each command -- swap this
    # out for the real EVO backend to run on hardware (see module docstring).
    lh = LiquidHandler(backend=LiquidHandlerChatterboxBackend(), deck=deck)
    await lh.setup()

    try:
        await lh.pick_up_tips(tip_rack[TIP_SPOT])
        await lh.aspirate(source_plate[SOURCE_WELL], vols=[volume_ul])
        await lh.drop_tips([waste], allow_nonzero_volume=True)
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
# 1. Replace LiquidHandlerChatterboxBackend() above with the real EVO
#    backend:
#      from pylabrobot.liquid_handling.backends import EVO
#      # diti_count = number of LiHa channels configured for disposable
#      # tips on your instrument.
#      lh = LiquidHandler(backend=EVO(diti_count=8), deck=deck)
#    The EVO backend talks to the instrument over USB, using the same
#    driver EVOware uses -- run this on the Windows PC connected to the
#    liquid handler, with the instrument powered on.
# 2. Update SOURCE_WELL, TIP_SPOT, MAX_VOLUME_UL, and the deck/resource
#    setup in withdraw_and_discard() to match your actual deck layout:
#    which EVO model (EVO100Deck / EVO150Deck / EVO200Deck), which tip
#    rack and carrier you use, and which rail/carrier positions hold
#    what. See pylabrobot.resources.tecan for the full list of Tecan
#    labware definitions (tip racks, plates, carriers).
# 3. See https://docs.pylabrobot.org for more on the Tecan backend and
#    its setup requirements.
