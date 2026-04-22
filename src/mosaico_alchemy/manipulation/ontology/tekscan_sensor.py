"""
Tekscan Sensor Data Structures.

This module defines an ontology model for Tekscan tactile sensor samples.
The structure preserves pressure-map data in the flattened form commonly used by
dataset exports.
"""

from typing import Optional

from mosaicolabs import MosaicoField, MosaicoType, Serializable


class TekscanSensor(Serializable):
    """Represent one Tekscan pressure map sample.

    The model exists to keep tactile data close to the source export. The flattened
    `values` vector can be reshaped into a 2D grid when `rows` and `cols` are known,
    but those dimensions stay optional because some datasets expose only the raw
    array and no explicit geometry metadata.

    Attributes:
        values: Flattened pressure values from the sensor array.
        rows: Optional number of rows in the sensor layout.
        cols: Optional number of columns in the sensor layout.
    """

    __ontology_tag__ = "tekscan_sensor"

    values: MosaicoType.list_(MosaicoType.float64) = MosaicoField(
        description="Values of the sensor array."
    )
    rows: Optional[MosaicoType.int64] = MosaicoField(
        default=None, description="Number of rows in the sensor array."
    )
    cols: Optional[MosaicoType.int64] = MosaicoField(
        default=None, description="Number of columns in the sensor array."
    )
