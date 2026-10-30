"""Change de boîte de tips automatiquement quand la boîte en cours est vide.

Démontre un pattern courant avec PyLabRobot : piocher les tips une par
une dans une liste de boîtes (tip racks), et dès qu'une boîte n'a plus
de tips, passer automatiquement à la boîte suivante au lieu de planter.

Construit sur une configuration Hamilton STARLet (vérifiée en simulation)
car PyLabRobot ne supporte pas le Tecan Fluent -- voir les notes en bas
du fichier pour l'utiliser avec une plateforme réellement supportée
(Hamilton STAR/Vantage, Tecan EVO, Opentrons).
"""

import asyncio
from typing import Iterator

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import LiquidHandlerChatterboxBackend
from pylabrobot.resources import (
    TIP_CAR_480_A00,
    STARLetDeck,
    hamilton_96_tiprack_300uL_filter,
)
from pylabrobot.resources.tip_rack import TipRack, TipSpot


def iter_available_tip_spots(tip_racks: list[TipRack]) -> Iterator[TipSpot]:
    """Renvoie les emplacements de tips disponibles, boîte après boîte.

    Parcourt tip_racks dans l'ordre ; dès qu'une boîte n'a plus de tip,
    passe automatiquement à la suivante. Lève RuntimeError si toutes les
    boîtes sont vides.
    """
    for rack in tip_racks:
        for spot in rack.get_all_items():
            if spot.has_tip():
                yield spot
    raise RuntimeError("Toutes les boîtes de tips sont vides.")


async def run_with_auto_tip_rack_switch(num_pickups: int) -> None:
    """Pioche num_pickups tips, en changeant de boîte automatiquement."""
    deck = STARLetDeck()

    tip_carrier = TIP_CAR_480_A00(name="tip carrier")
    tip_carrier[0] = rack_1 = hamilton_96_tiprack_300uL_filter(name="tip rack 1")
    tip_carrier[1] = rack_2 = hamilton_96_tiprack_300uL_filter(name="tip rack 2")
    deck.assign_child_resource(tip_carrier, rails=1)

    # Pour la démo : ne laisser que 2 tips dans la boîte 1, pour voir le
    # changement de boîte rapidement plutôt qu'après 96 prélèvements.
    rack_1.set_tip_state([False] * 94 + [True] * 2)

    lh = LiquidHandler(backend=LiquidHandlerChatterboxBackend(), deck=deck)
    await lh.setup()

    tip_spots = iter_available_tip_spots([rack_1, rack_2])
    current_rack_name = None

    try:
        for _ in range(num_pickups):
            spot = next(tip_spots)
            if spot.parent.name != current_rack_name:
                current_rack_name = spot.parent.name
                print(f">>> Utilisation de la boîte : {current_rack_name}")

            await lh.pick_up_tips([spot])
            await lh.discard_tips()
    finally:
        await lh.stop()


def main() -> None:
    asyncio.run(run_with_auto_tip_rack_switch(num_pickups=5))


if __name__ == "__main__":
    main()

# --- Pour une vraie plateforme ---------------------------------------------
# 1. Remplace LiquidHandlerChatterboxBackend() par le backend réel :
#      from pylabrobot.liquid_handling.backends import STAR      # Hamilton
#      from pylabrobot.liquid_handling.backends import EVO       # Tecan EVO
#    (Le Tecan Fluent n'est pas supporté par PyLabRobot.)
# 2. Adapte le deck, les boîtes de tips et les rails à ta configuration
#    réelle (nombre de boîtes, type/volume des tips, positions).
# 3. set_tip_state() ci-dessus ne sert qu'à la démo -- sur une vraie
#    boîte neuve, enlève cette ligne : la boîte est pleine par défaut et
#    PyLabRobot suit l'état réel des tips au fil des prélèvements.
