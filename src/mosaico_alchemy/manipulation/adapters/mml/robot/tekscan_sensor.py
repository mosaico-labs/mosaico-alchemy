from typing import Any, Optional

from mosaicolabs.ros_bridge import ROSAdapterBase

from mosaico_alchemy.manipulation.ontology import TekscanSensor


class TekscanSensorAdapter(ROSAdapterBase[TekscanSensor]):
    ros_msgtype = "std_msgs/msg/Float64MultiArray"
    __mosaico_ontology_type__ = TekscanSensor
    _REQUIRED_KEYS = ("data",)

    @classmethod
    def from_dict(cls, ros_data: dict) -> TekscanSensor:
        values = ros_data.get("data")
        if values is None:
            raise ValueError("Float64MultiArray payload is missing the 'data' field")

        return TekscanSensor(values=list(values))

    @classmethod
    def schema_metadata(cls, ros_data: dict, **kwargs: Any) -> Optional[dict]:
        return None
