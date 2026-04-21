"""
Joint Torque Command Data Structures.

This module defines an ontology model for joint-space torque commands.
It exists so packs can preserve actuator intent without depending on a robot-specific
command message schema.
"""

from mosaicolabs import MosaicoField, MosaicoType, Serializable


class JointTorqueCommand(Serializable):
    """Represent a joint-space torque command.

    The split between `names` and `torques` mirrors how many robotics datasets encode
    commands: one ordered list of joint identifiers plus one ordered list of numeric
    targets. Preserving that structure keeps ingestion faithful to the source while
    remaining independent from any robot-specific ontology. The two lists must stay
    index-aligned.

    Attributes:
        names: Ordered joint identifiers.
        torques: Ordered torque commands aligned with `names`.
    """

    __ontology_tag__ = "joint_torque_command"

    names: MosaicoType.list_(MosaicoType.string) = MosaicoField(
        description="Names of the different robot joints"
    )
    torques: MosaicoType.list_(MosaicoType.float64) = MosaicoField(
        description="Torque values for the corresponding joints, in the same order as the names list."
    )
