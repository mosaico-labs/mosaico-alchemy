"""
CLI dispatcher for the packs bundled in `mosaicopacks`.

The top-level executable does not implement ingestion itself. Its job is to route
the first positional argument to the matching pack module so each pack can expose
its own dedicated `main` entrypoint and argument parsing.
"""

import importlib
import sys

PACKS_MAP = {
    "manipulation": "mosaicopacks.manipulation.main",
}


def _print_help() -> None:
    available_packs = ", ".join(sorted(PACKS_MAP))
    print("Usage: mosaicopacks <pack> [args...]")
    print()
    print("Mosaico SDK Packs Runner.")
    print()
    print(f"Available packs: {available_packs}")


def run_pack_cli() -> None:
    """
    Dispatches the top-level CLI invocation to the selected pack entrypoint.

    This wrapper keeps the user-facing command stable while allowing each pack to
    own its runtime and argument parser. The selected pack receives an adjusted
    `sys.argv` so downstream help and error messages still look like a normal CLI.

    Raises:
        SystemExit: If the user selects an unknown pack or the pack module does not
            expose a `main` function.
    """
    argv = sys.argv[1:]
    if not argv or argv[0] in {"-h", "--help"}:
        _print_help()
        return

    pack = argv[0]
    if pack not in PACKS_MAP:
        _print_help()
        raise SystemExit(f"Unknown pack '{pack}'")

    module = importlib.import_module(PACKS_MAP[pack])
    entry_point = getattr(module, "main", None)
    if entry_point is None:
        raise SystemExit(f"No 'main' function found in {PACKS_MAP[pack]}")

    sys.argv = [f"{sys.argv[0]} {pack}", *argv[1:]]
    entry_point()


if __name__ == "__main__":
    run_pack_cli()
