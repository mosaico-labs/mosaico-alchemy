from typing import Any, Optional

from mosaicolabs.ros_bridge import ROSAdapterBase
from mosaicolabs.ros_bridge.adapters.helpers import _validate_msgdata

from mosaico_alchemy.manipulation.ontology import TekscanSensor


class TekscanSensorAdapter(ROSAdapterBase[TekscanSensor]):
    """
    Adapter override for 'std_msgs/msg/Float64MultiArray' to `TekscanSensor` model.

    MML codes this data as a generic `Float64MultiArray`, but we know it to be a TekscanSensor
    and can convert it to a more specific type.
    """

    ros_msgtype = "std_msgs/msg/Float64MultiArray"
    __mosaico_ontology_type__ = TekscanSensor
    _REQUIRED_KEYS = ("data",)

    @classmethod
    def from_dict(cls, ros_data: dict) -> TekscanSensor:
        """
        Converts a ROS Float64MultiArray message to a TekscanSensor.

        Args:
            ros_data: ROS Float64MultiArray message as a dictionary.

        Returns:
            TekscanSensor instance.
        """
        _validate_msgdata(cls, ros_data)
        return TekscanSensor(values=list(ros_data["data"]))

    @classmethod
    def schema_metadata(cls, ros_data: dict, **kwargs: Any) -> Optional[dict]:
        return None
