from typing import Any, Optional

from mosaicolabs.ros_bridge import ROSAdapterBase
from mosaicolabs.ros_bridge.adapters.helpers import _validate_msgdata

from mosaico_alchemy.manipulation.ontology import JointTorqueCommand


class JointTorqueCommandAdapter(ROSAdapterBase[JointTorqueCommand]):
    """
    Adapter override for 'std_msgs/msg/Float64MultiArray' to `JointTorqueCommand` model.

    MML codes this data as a generic `Float64MultiArray`, but we know it to be a joint torque
    command and can convert it to a more specific type.
    """

    ros_msgtype = "std_msgs/msg/Float64MultiArray"
    __mosaico_ontology_type__ = JointTorqueCommand
    _REQUIRED_KEYS = ("data",)
    JOINT_NAMES = tuple(f"iiwa_joint_{index}" for index in range(1, 8))

    @classmethod
    def from_dict(cls, ros_data: dict) -> JointTorqueCommand:
        """
        Converts a ROS Float64MultiArray message to a JointTorqueCommand.

        Args:
            ros_data: ROS Float64MultiArray message as a dictionary.

        Returns:
            JointTorqueCommand instance.

        Raises:
            ValueError: If the message is missing the 'data' field or has an incorrect
                number of torque values.
        """
        _validate_msgdata(cls, ros_data)
        torques = ros_data["data"]
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
