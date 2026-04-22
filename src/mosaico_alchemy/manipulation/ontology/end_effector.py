"""
End-Effector Data Structures.

This module defines a compact ontology model for end-effector state.
It exists for datasets that expose tool state as parallel numeric arrays instead of
robot-specific message types.
"""

from mosaicolabs import MosaicoField, MosaicoType, Serializable


class EndEffector(Serializable):
    """Represent end-effector state vectors for a single sample.

    The model exists to preserve a common dataset pattern: position, velocity, and
    effort exported as parallel arrays with implicit index-based meaning. Keeping that
    shape avoids inventing axis names or robot-specific semantics during ingestion.
    The three lists are therefore expected to stay aligned by index.

    Attributes:
        efforts: Effort values for each controlled end-effector dimension.
        positions: Position values for each controlled end-effector dimension.
        velocities: Velocity values for each controlled end-effector dimension.
    """

    __ontology_tag__ = "end_effector"

    efforts: MosaicoType.list_(MosaicoType.float64) = MosaicoField(
        description="End-effector effort values for each controlled dimension."
    )
    positions: MosaicoType.list_(MosaicoType.float64) = MosaicoField(
        description="End-effector position values for each controlled dimension."
    )
    velocities: MosaicoType.list_(MosaicoType.float64) = MosaicoField(
        description="End-effector velocity values for each controlled dimension."
    )
