from domain.models import ShipConfig, WeaponGroup

ION_CANNON = WeaponGroup(dice_count=1, damage=1)
PLASMA_CANNON = WeaponGroup(dice_count=1, damage=2)
PLASMA_MISSILE = WeaponGroup(dice_count=2, damage=2, is_missile=True)
ANTIMATTER_CANNON = WeaponGroup(dice_count=1, damage=4)
SOLITON_CANNON = WeaponGroup(dice_count=1, damage=3)
FLUX_MISSILE = WeaponGroup(dice_count=2, damage=3, is_missile=True)

PRESETS: dict[str, ShipConfig] = {
    "Ancient Ship": ShipConfig(
        name="Ancient Ship",
        weapons=(ION_CANNON, ION_CANNON),
        computer=1,
        shield=0,
        hull=1,
        initiative=2,
        count=1,
    ),
    "GCDS": ShipConfig(
        name="GCDS",
        weapons=(ION_CANNON, ION_CANNON, ION_CANNON, ION_CANNON),
        computer=1,
        shield=0,
        hull=7,
        initiative=0,
        count=1,
    ),
    "Terran Interceptor": ShipConfig(
        name="Terran Interceptor",
        weapons=(ION_CANNON,),
        computer=0,
        shield=0,
        hull=0,
        initiative=3,
        count=1,
    ),
    "Terran Cruiser": ShipConfig(
        name="Terran Cruiser",
        weapons=(ION_CANNON,),
        computer=1,
        shield=0,
        hull=1,
        initiative=2,
        count=1,
    ),
    "Terran Dreadnought": ShipConfig(
        name="Terran Dreadnought",
        weapons=(ION_CANNON, ION_CANNON),
        computer=0,
        shield=0,
        hull=1,
        initiative=1,
        count=1,
    ),
    "Terran Starbase": ShipConfig(
        name="Terran Starbase",
        weapons=(ION_CANNON,),
        computer=0,
        shield=0,
        hull=0,
        initiative=4,
        count=1,
    ),
}
