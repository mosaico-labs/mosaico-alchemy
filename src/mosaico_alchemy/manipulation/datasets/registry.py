"""
Registry of dataset plugins available to the manipulation ingestion pipeline.

The registry centralizes how dataset roots are mapped to plugin implementations.
That keeps CLI and runner code generic: they can resolve dataset support through
this module instead of hard-coding knowledge of every dataset family.
"""

from pathlib import Path

from mosaicopacks.manipulation.contracts import DatasetPlugin
from mosaicopacks.manipulation.datasets.droid import DROIDPlugin
from mosaicopacks.manipulation.datasets.fractal_rt1 import FractalRT1Plugin
from mosaicopacks.manipulation.datasets.mml import MMLPlugin
from mosaicopacks.manipulation.datasets.reassemble import ReassemblePlugin


class DatasetRegistry:
    """
    Stores dataset plugins and resolves them by identifier or compatible root.

    The same registry supports two workflows:
    - explicit selection, where the CLI already knows the desired `dataset_id`;
    - auto-detection, where the runner asks each plugin whether it supports a root.

    Keeping both paths in one place makes plugin resolution predictable and easier
    to extend in open-source deployments.
    """

    def __init__(self) -> None:
        """Initializes an empty dataset plugin registry."""
        self._plugins: list[DatasetPlugin] = []

    def register(self, plugin: DatasetPlugin) -> None:
        """
        Registers a dataset plugin instance in resolution order.

        Registration order matters for `resolve`, because the first plugin whose
        `supports` method returns `True` wins. The default registry therefore
        encodes the intended precedence between built-in dataset families.

        Args:
            plugin: Plugin instance to expose through the registry.
        """
        self._plugins.append(plugin)

    def all(self) -> list[DatasetPlugin]:
        """
        Returns the registered plugins in resolution order.

        A copy is returned so callers can inspect the available plugins without
        mutating the registry state shared by the runner and CLI.
        """
        return list(self._plugins)

    def get(self, dataset_id: str) -> DatasetPlugin:
        """
        Resolves a plugin by its stable public identifier.

        This path is used when the caller has already chosen the plugin explicitly,
        for example after an interactive CLI selection.

        Args:
            dataset_id: Public identifier declared by the plugin.

        Returns:
            The matching dataset plugin instance.

        Raises:
            KeyError: If no registered plugin exposes `dataset_id`.
        """
        for plugin in self._plugins:
            if plugin.dataset_id == dataset_id:
                return plugin
        raise KeyError(f"Unknown dataset plugin '{dataset_id}'")

    def resolve(self, root: Path) -> DatasetPlugin:
        """
        Resolves the first plugin that recognizes the given dataset root.

        Args:
            root: Dataset root supplied by the user.

        Returns:
            The first registered plugin whose `supports` method accepts `root`.

        Raises:
            ValueError: If no plugin recognizes the dataset layout.
        """
        for plugin in self._plugins:
            if plugin.supports(root):
                return plugin
        raise ValueError(f"No dataset plugin found for {root}")


def build_default_dataset_registry() -> DatasetRegistry:
    """
    Builds the dataset registry shipped with the manipulation pack.

    The default registry wires together every built-in dataset plugin so the CLI
    can offer interactive selection and the runner can auto-detect known layouts
    out of the box.

    Returns:
        A dataset registry pre-populated with the built-in plugins.
    """
    registry = DatasetRegistry()
    registry.register(FractalRT1Plugin())
    registry.register(ReassemblePlugin())
    registry.register(MMLPlugin())
    registry.register(DROIDPlugin())
    return registry
