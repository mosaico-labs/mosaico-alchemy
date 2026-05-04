"""
Segment Info Data Structures.

This module defines an ontology model for action segment annotations carried by
manipulation datasets. Each segment describes a single action attempt over a
time interval: the action name, an optional parent action for nested compositions,
the eventual outcome of the action, and a flag distinguishing the start of the
segment from its end.

Two messages are typically pushed per segment (one with `is_terminal=False` at the
start, one with `is_terminal=True` at the end) so that downstream consumers can
forward fill the same payload across the whole interval.
"""

from typing import Optional

from mosaicolabs import MosaicoField, MosaicoType, Serializable


class SegmentInfo(Serializable):
    """Annotation of a single action segment within a manipulation episode.

    Attributes:
        action: Natural-language description of the requested or performed action.
        parent_action: Higher-level action that contains this segment, when the
            episode is structured as a composed action graph. None for top-level segments.
        success: Outcome flag of the action represented by this segment.
        is_terminal: Marks the end boundary of the segment. False on the start
            message of the segment, True on the end message.
    """

    __ontology_tag__ = "segment_info"

    action: MosaicoType.string = MosaicoField(
        description="The requested/performed action in natural language."
    )
    parent_action: Optional[MosaicoType.string] = MosaicoField(
        description="The parent action, if this is a 'low level' (nested) action in a composed action setting.",
        default=None,
    )
    success: MosaicoType.bool = MosaicoField(
        description="The success flag of the action represented by this info."
    )
    is_terminal: MosaicoType.bool = MosaicoField(
        description="True if this is the 'end' of the action."
    )
