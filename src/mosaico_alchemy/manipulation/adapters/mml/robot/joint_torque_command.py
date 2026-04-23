from typing import Any, Optional

from mosaicolabs.ros_bridge import ROSAdapterBase

from mosaico_alchemy.manipulation.ontology import JointTorqueCommand


class JointTorqueCommandAdapter(ROSAdapterBase[JointTorqueCommand]):
    ros_msgtype = "std_msgs/msg/Float64MultiArray"
    __mosaico_ontology_type__ = JointTorqueCommand
    _REQUIRED_KEYS = ("data",)
    JOINT_NAMES = tuple(f"iiwa_joint_{index}" for index in range(1, 8))

    @classmethod
    def from_dict(cls, ros_data: dict) -> JointTorqueCommand:
        torques = ros_data.get("data")
        if torques is None:
            raise ValueError("Float64MultiArray payload is missing the 'data' field")
        if len(torques) != len(cls.JOINT_NAMES):
            raise ValueError(
                f"Expected {len(cls.JOINT_NAMES)} torque values, received {len(torques)}"
            )

        return JointTorqueCommand(
            names=list(cls.JOINT_NAMES),
            torques=list(torques),
        )

    @classmethod
    def schema_metadata(cls, ros_data: dict, **kwargs: Any) -> Optional[dict]:
        return None
