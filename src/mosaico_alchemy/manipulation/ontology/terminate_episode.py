"""
Episode Termination Data Structures.

This module defines an ontology model for episode-termination signals exported by
Fractal RT-1 style datasets. The goal is to preserve the exact source encoding
instead of collapsing it into a more opinionated boolean flag.
"""

from mosaicolabs import MosaicoField, MosaicoType, Serializable


class TerminateEpisode(Serializable):
    """Represent the RT-1 episode termination signal.

    The model exists because the source dataset does not publish a single explicit
    `done` value. It emits a fixed 3-element vector with one undocumented slot, so
    the safest ingestion behavior is to preserve that encoding exactly and let
    downstream consumers decide how much interpretation they want to apply.

    Attributes:
        terminate_episode: Raw 3-element termination vector from the source dataset.
    """

    __ontology_tag__ = "terminate_episode"

    terminate_episode: MosaicoType.list_(MosaicoType.int32, list_size=3) = MosaicoField(
        description=(
            "RT-1 terminate signal encoded as a 3-element int32 vector in the order "
            "[terminate, continue, undocumented]."
        )
    )
