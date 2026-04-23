"""
Registry of adapter implementations available to the manipulation pack.

The runner treats adapters as named plugins. Centralizing registration here keeps
dataset descriptors declarative: they only need to reference an `adapter_id`,
while the registry owns the mapping to concrete translation classes.
"""

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.adapters.droid.robot.end_effector import (
    DroidEndEffectorAdapter,
)
from mosaico_alchemy.manipulation.adapters.droid.robot.joint_state import (
    DroidJointStateAdapter,
)
from mosaico_alchemy.manipulation.adapters.droid.robot.pose import (
    DroidPoseAdapter,
)
from mosaico_alchemy.manipulation.adapters.droid.robot.velocity import (
    DroidVelocityAdapter,
)
from mosaico_alchemy.manipulation.adapters.droid.scalar.boolean import (
    DroidBooleanAdapter,
)
from mosaico_alchemy.manipulation.adapters.droid.scalar.floating64 import (
    DroidFloating64Adapter,
)
from mosaico_alchemy.manipulation.adapters.droid.scalar.integer64 import (
    DroidInteger64Adapter,
)
from mosaico_alchemy.manipulation.adapters.droid.vision.video_frame import (
    DroidVideoFrameAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.action.terminate_episode import (
    FractalRT1TerminateEpisodeAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.geometry.quaternion import (
    FractalRT1QuaternionAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.geometry.spatial_bounds import (
    FractalRT1OrientationBoxAdapter,
    FractalRT1RobotOrientationPositionsBoxAdapter,
    FractalRT1WorkspaceBoundsAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.geometry.vector2d import (
    FractalRT1Vector2dAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.geometry.vector3d import (
    FractalRT1Vector3dAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.language.text_embedding import (
    FractalRT1TextEmbeddingAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.robot.pose import (
    FractalRT1PoseAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.scalar.boolean import (
    FractalRT1BooleanAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.scalar.floating32 import (
    FractalRT1Floating32Adapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.scalar.string import (
    FractalRT1StringAdapter,
)
from mosaico_alchemy.manipulation.adapters.fractal_rt1.vision.video_frame import (
    FractalRT1VideoFrameAdapter,
)
from mosaico_alchemy.manipulation.adapters.reassemble.audio.audio import (
    ReassembleAudioAdapter,
)
from mosaico_alchemy.manipulation.adapters.reassemble.robot.compensated_base_force_torque import (
    ReassembleCompensatedBaseForceTorqueAdapter,
)
from mosaico_alchemy.manipulation.adapters.reassemble.robot.end_effector import (
    ReassembleEndEffectorAdapter,
)
from mosaico_alchemy.manipulation.adapters.reassemble.robot.joint_state import (
    ReassembleJointStateAdapter,
)
from mosaico_alchemy.manipulation.adapters.reassemble.robot.measured_force_torque import (
    ReassembleMeasuredForceTorqueAdapter,
)
from mosaico_alchemy.manipulation.adapters.reassemble.robot.pose import (
    ReassemblePoseAdapter,
)
from mosaico_alchemy.manipulation.adapters.reassemble.robot.velocity import (
    ReassembleVelocityAdapter,
)
from mosaico_alchemy.manipulation.adapters.reassemble.vision.events import (
    ReassembleEventsAdapter,
)
from mosaico_alchemy.manipulation.adapters.reassemble.vision.video_frame import (
    ReassembleVideoFrameAdapter,
)


class AdapterRegistry:
    """
    Stores the adapter classes that can be resolved during ingestion.

    The registry exists to decouple dataset descriptors from concrete imports. A
    plugin can reference `reassemble.pose` or `fractal_rt1.video_frame` by id,
    and the runner can later resolve that id without knowing anything about the
    dataset family that produced it.
    """

    def __init__(self) -> None:
        """Initializes an empty adapter registry."""
        self._adapters: dict[str, type[BaseAdapter]] = {}

    def register(self, adapter_cls: type[BaseAdapter]) -> None:
        """
        Registers an adapter class under its declared `adapter_id`.

        Args:
            adapter_cls: Adapter implementation to expose through the registry.

        Raises:
            ValueError: If another adapter already uses the same identifier.
        """
        if adapter_cls.adapter_id in self._adapters:
            raise ValueError(f"Adapter '{adapter_cls.adapter_id}' already registered")
        self._adapters[adapter_cls.adapter_id] = adapter_cls

    def get(self, adapter_id: str) -> type[BaseAdapter]:
        """
        Resolves the adapter class associated with a descriptor `adapter_id`.

        Args:
            adapter_id: Stable identifier referenced by a topic descriptor.

        Returns:
            The registered adapter class.

        Raises:
            KeyError: If no adapter was registered under `adapter_id`.
        """
        try:
            return self._adapters[adapter_id]
        except KeyError as exc:
            raise KeyError(f"Unknown adapter_id '{adapter_id}'") from exc

    def all(self) -> dict[str, type[BaseAdapter]]:
        """
        Returns a copy of the current adapter mapping.

        Returning a copy keeps registry ownership explicit and avoids accidental
        mutation by callers that only need to inspect available adapters.
        """
        return dict(self._adapters)


def build_default_adapter_registry() -> AdapterRegistry:
    """
    Builds the adapter registry shipped with the manipulation pack.

    The default registry is the open-source baseline: it wires together every adapter
    bundled by the package so CLI and runner code can work without extra setup.

    Returns:
        An adapter registry pre-populated with the built-in adapters.
    """
    registry = AdapterRegistry()
    registry.register(FractalRT1TerminateEpisodeAdapter)
    registry.register(FractalRT1BooleanAdapter)
    registry.register(FractalRT1Floating32Adapter)
    registry.register(FractalRT1StringAdapter)
    registry.register(FractalRT1Vector2dAdapter)
    registry.register(FractalRT1Vector3dAdapter)
    registry.register(FractalRT1PoseAdapter)
    registry.register(FractalRT1QuaternionAdapter)
    registry.register(FractalRT1OrientationBoxAdapter)
    registry.register(FractalRT1RobotOrientationPositionsBoxAdapter)
    registry.register(FractalRT1WorkspaceBoundsAdapter)
    registry.register(FractalRT1TextEmbeddingAdapter)
    registry.register(FractalRT1VideoFrameAdapter)
    registry.register(ReassembleJointStateAdapter)
    registry.register(ReassemblePoseAdapter)
    registry.register(ReassembleVelocityAdapter)
    registry.register(ReassembleVideoFrameAdapter)
    registry.register(ReassembleEventsAdapter)
    registry.register(ReassembleMeasuredForceTorqueAdapter)
    registry.register(ReassembleCompensatedBaseForceTorqueAdapter)
    registry.register(ReassembleAudioAdapter)
    registry.register(ReassembleEndEffectorAdapter)
    registry.register(DroidJointStateAdapter)
    registry.register(DroidPoseAdapter)
    registry.register(DroidVelocityAdapter)
    registry.register(DroidEndEffectorAdapter)
    registry.register(DroidVideoFrameAdapter)
    registry.register(DroidBooleanAdapter)
    registry.register(DroidFloating64Adapter)
    registry.register(DroidInteger64Adapter)
    return registry
