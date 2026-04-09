"""Streamlit web UI for the Eclipse battle simulator."""

import random

import streamlit as st

from domain.models import ShipConfig, WeaponGroup
from domain.strategy import (
    DEFAULT_STRATEGY_NAME,
    STRATEGIES,
    GreedyLargestFirst,
    GreedySmallestFirst,
    MaximizeKills,
    RandomAssignment,
)
from presentation.presets import PRESETS
from simulation.runner import SimulationResult, run_simulation

st.set_page_config(page_title="Eclipse Battle Simulator", layout="wide")
st.title("Eclipse: Second Dawn — Battle Simulator")

# ---- session state init ----
for _side in ("attacker", "defender"):
    _key = f"{_side}_ships"
    if _key not in st.session_state:
        st.session_state[_key] = []
    _wkey = f"{_side}_custom_weapons"
    if _wkey not in st.session_state:
        st.session_state[_wkey] = []

if "simulation_history" not in st.session_state:
    st.session_state.simulation_history: list[dict] = []


def _describe_ship(ship: ShipConfig) -> str:
    """Single-line markdown description of a ship with full stats."""
    weapon_parts: list[str] = []
    for w in ship.weapons:
        wtype = "Missile" if w.is_missile else "Cannon"
        weapon_parts.append(f"{wtype} {w.dice_count}d x{w.damage}dmg")
    weapons_str = ", ".join(weapon_parts) if weapon_parts else "No weapons"
    return (
        f"**{ship.name}** x{ship.count} — "
        f"{weapons_str} | "
        f"Comp +{ship.computer} | Shield -{ship.shield} | "
        f"Hull {ship.hull} | Init {ship.initiative}"
    )


def _describe_fleet(ships: list[ShipConfig]) -> str:
    """Multi-line markdown description of all ships in a fleet."""
    return "\n".join(f"- {_describe_ship(s)}" for s in ships)


def _summarize_fleet(ships: list[ShipConfig]) -> str:
    """Short one-liner for expander headers (names and counts only)."""
    return ", ".join(f"{s.name} x{s.count}" for s in ships)


def _add_preset(side: str, preset_name: str) -> None:
    preset = PRESETS[preset_name]
    st.session_state[f"{side}_ships"].append(preset)


def _add_weapon(side: str, prefix: str) -> None:
    wtype = st.session_state.get(f"{prefix}_wtype", "Cannon")
    dice = st.session_state.get(f"{prefix}_wdice", 1)
    dmg = st.session_state.get(f"{prefix}_wdmg", 1)
    st.session_state[f"{side}_custom_weapons"].append(
        {"dice_count": dice, "damage": dmg, "is_missile": wtype == "Missile"},
    )


def _clear_weapons(side: str) -> None:
    st.session_state[f"{side}_custom_weapons"] = []


def _add_custom(side: str, prefix: str) -> None:
    name = st.session_state.get(f"{prefix}_name", "Custom Ship")
    count = st.session_state.get(f"{prefix}_count", 1)
    computer = st.session_state.get(f"{prefix}_computer", 0)
    shield = st.session_state.get(f"{prefix}_shield", 0)
    hull = st.session_state.get(f"{prefix}_hull", 0)
    initiative = st.session_state.get(f"{prefix}_initiative", 0)

    weapons = tuple(
        WeaponGroup(
            dice_count=w["dice_count"],
            damage=w["damage"],
            is_missile=w["is_missile"],
        )
        for w in st.session_state[f"{side}_custom_weapons"]
    )

    ship = ShipConfig(
        name=name,
        weapons=weapons,
        computer=computer,
        shield=shield,
        hull=hull,
        initiative=initiative,
        count=count,
    )
    st.session_state[f"{side}_ships"].append(ship)
    st.session_state[f"{side}_custom_weapons"] = []


def _clear_fleet(side: str) -> None:
    st.session_state[f"{side}_ships"] = []


def _render_fleet_builder(side: str) -> list[ShipConfig]:
    label = "Attacker" if side == "attacker" else "Defender"
    prefix = f"{side}_custom"

    st.subheader(f"{label} Fleet")

    # Preset buttons
    st.markdown("**Add preset:**")
    cols = st.columns(3)
    preset_names = list(PRESETS.keys())
    for i, name in enumerate(preset_names):
        with cols[i % 3]:
            if st.button(name, key=f"{side}_preset_{name}", use_container_width=True):
                _add_preset(side, name)
                st.rerun()

    # Custom ship builder
    with st.expander("Add custom ship type"):
        st.text_input("Name", value="Custom Ship", key=f"{prefix}_name")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input(
                "Count", min_value=1, max_value=8, value=1,
                key=f"{prefix}_count",
            )
            st.number_input(
                "Computer", min_value=0, max_value=9, value=0,
                key=f"{prefix}_computer",
            )
        with c2:
            st.number_input(
                "Shield", min_value=0, max_value=9, value=0,
                key=f"{prefix}_shield",
            )
            st.number_input(
                "Hull", min_value=0, max_value=20, value=0,
                key=f"{prefix}_hull",
            )
        st.number_input(
            "Initiative", min_value=0, max_value=15, value=0,
            key=f"{prefix}_initiative",
        )

        st.markdown("**Weapons:**")
        pending_weapons: list[dict] = st.session_state[f"{side}_custom_weapons"]
        if pending_weapons:
            for i, w in enumerate(pending_weapons):
                wtype = "Missile" if w["is_missile"] else "Cannon"
                st.text(f"  {i + 1}. {wtype} — {w['dice_count']}d x{w['damage']}dmg")
        else:
            st.caption("No weapons added yet.")

        w1, w2, w3 = st.columns(3)
        with w1:
            st.selectbox("Type", ["Cannon", "Missile"], key=f"{prefix}_wtype")
        with w2:
            st.number_input(
                "Dice (per ship)", min_value=1, max_value=10, value=1,
                key=f"{prefix}_wdice",
            )
        with w3:
            st.number_input(
                "Damage (per hit)", min_value=1, max_value=6, value=1,
                key=f"{prefix}_wdmg",
            )
        wb1, wb2 = st.columns(2)
        with wb1:
            if st.button("Add Weapon", key=f"{prefix}_wadd"):
                _add_weapon(side, prefix)
                st.rerun()
        with wb2:
            if pending_weapons and st.button("Clear Weapons", key=f"{prefix}_wclear"):
                _clear_weapons(side)
                st.rerun()

        st.divider()
        if st.button(f"Add to {label}", key=f"{prefix}_add"):
            _add_custom(side, prefix)
            st.rerun()

    # Current fleet display
    ships: list[ShipConfig] = st.session_state[f"{side}_ships"]
    if ships:
        st.markdown("**Current fleet:**")
        st.markdown(_describe_fleet(ships))
        if st.button(f"Clear {label}", key=f"{side}_clear"):
            _clear_fleet(side)
            st.rerun()
    else:
        st.info(f"No ships added to {label.lower()} fleet yet.")

    return ships


# ---- Layout ----
left, right = st.columns(2)

with left:
    attacker_ships = _render_fleet_builder("attacker")

with right:
    defender_ships = _render_fleet_builder("defender")

# ---- Simulation controls ----
st.divider()
ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
with ctrl1:
    n_sims = st.slider(
        "Number of simulations",
        min_value=100, max_value=100_000, value=10_000, step=100,
    )
with ctrl2:
    seed = st.number_input(
        "Random seed (0 = random)", min_value=0, max_value=999_999, value=42,
    )
with ctrl3:
    strategy_name = st.selectbox(
        "Dice assignment strategy",
        list(STRATEGIES.keys()),
        index=list(STRATEGIES.keys()).index(DEFAULT_STRATEGY_NAME),
    )

run_btn = st.button("Run Simulation", type="primary", use_container_width=True)

# ---- Results ----
if run_btn:
    if not attacker_ships or not defender_ships:
        st.error("Both sides need at least one ship type.")
    else:
        strategy_cls = STRATEGIES[strategy_name]
        if strategy_cls is RandomAssignment:
            strategy_instance = strategy_cls(random.Random(seed if seed > 0 else None))
        else:
            strategy_instance = strategy_cls()

        with st.spinner(f"Running {n_sims:,} simulations..."):
            result: SimulationResult = run_simulation(
                attacker_configs=attacker_ships,
                defender_configs=defender_ships,
                n=n_sims,
                seed=seed if seed > 0 else None,
                strategy=strategy_instance,
            )

        st.session_state.simulation_history.append({
            "attacker_fleet": _describe_fleet(attacker_ships),
            "attacker_summary": _summarize_fleet(attacker_ships),
            "defender_fleet": _describe_fleet(defender_ships),
            "defender_summary": _summarize_fleet(defender_ships),
            "result": result,
        })

        st.divider()
        st.subheader("Results")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Attacker wins", f"{result.attacker_win_pct:.1f}%")
        m2.metric("Defender wins", f"{result.defender_win_pct:.1f}%")
        m3.metric("Draws", f"{result.draw_pct:.1f}%")
        m4.metric("Avg rounds", f"{result.avg_rounds:.1f}")

        col_a, col_d = st.columns(2)
        with col_a:
            st.metric("Avg attacker survivors", f"{result.avg_attacker_survivors:.2f}")
        with col_d:
            st.metric("Avg defender survivors", f"{result.avg_defender_survivors:.2f}")

        st.bar_chart(
            {
                "Attacker": [result.attacker_win_pct],
                "Defender": [result.defender_win_pct],
                "Draw": [result.draw_pct],
            },
            horizontal=True,
        )

# ---- Simulation History ----
history: list[dict] = st.session_state.simulation_history
if len(history) > 1:
    st.divider()
    hdr1, hdr2 = st.columns([4, 1])
    with hdr1:
        st.subheader("Simulation History")
    with hdr2:
        if st.button("Clear History", use_container_width=True):
            st.session_state.simulation_history = []
            st.rerun()

    for entry in reversed(history[:-1]):
        r: SimulationResult = entry["result"]
        header = (
            f"{entry['attacker_summary']}  vs  {entry['defender_summary']}"
            f"  —  Attacker {r.attacker_win_pct:.1f}% / Defender {r.defender_win_pct:.1f}%"
        )
        with st.expander(header):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Attacker wins", f"{r.attacker_win_pct:.1f}%")
            m2.metric("Defender wins", f"{r.defender_win_pct:.1f}%")
            m3.metric("Draws", f"{r.draw_pct:.1f}%")
            m4.metric("Avg rounds", f"{r.avg_rounds:.1f}")

            col_a, col_d = st.columns(2)
            with col_a:
                st.metric("Avg attacker survivors", f"{r.avg_attacker_survivors:.2f}")
            with col_d:
                st.metric("Avg defender survivors", f"{r.avg_defender_survivors:.2f}")

            st.markdown("**Attacker fleet:**")
            st.markdown(entry["attacker_fleet"])
            st.markdown("**Defender fleet:**")
            st.markdown(entry["defender_fleet"])
