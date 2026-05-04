"""
Iterator factories for Reassemble HDF5 sequences.

These helpers adapt `HDF5Reader` methods to the callable shape expected by
`TopicDescriptor`: a factory receives static dataset paths up front and returns a
function that can later stream or count data for one concrete sequence file.
"""

from pathlib import Path
from typing import Callable, Iterable

import h5py

from mosaico_alchemy.manipulation.readers import HDF5Reader


def _iter_segment_boundaries(
    h5_path: Path, segments_info_path: str, action: str = "grasp"
) -> Iterable[dict]:
    """Walk segments_info/{n}/{start,end,success} plus optional low_level/{k}/...
    and yield two SegmentInfo records per segment (one start with is_terminal=False
    and one end with is_terminal=True). Pairing the two boundaries lets a SyncHold
    consumer carry the same payload across the whole segment interval.
    """
    with h5py.File(str(h5_path), "r") as f:
        grp = f.get(segments_info_path)
        if grp is None:
            return
        for key in sorted(grp.keys(), key=lambda k: int(k)):
            s = grp[key]
            if not all(k in s for k in ("start", "end", "success")):
                continue
            start_s = float(s["start"][()])
            end_s = float(s["end"][()])
            success = bool(s["success"][()])
            yield {
                "timestamp": start_s,
                "action": action,
                "parent_action": None,
                "success": success,
                "is_terminal": False,
            }
            yield {
                "timestamp": end_s,
                "action": action,
                "parent_action": None,
                "success": success,
                "is_terminal": True,
            }
            ll = s.get("low_level")
            if ll is None:
                continue
            for lk in sorted(ll.keys(), key=lambda k: int(k)):
                ls = ll[lk]
                if not all(k in ls for k in ("start", "end", "success")):
                    continue
                l_start_s = float(ls["start"][()])
                l_end_s = float(ls["end"][()])
                l_success = bool(ls["success"][()])
                yield {
                    "timestamp": l_start_s,
                    "action": action,
                    "parent_action": action,
                    "success": l_success,
                    "is_terminal": False,
                }
                yield {
                    "timestamp": l_end_s,
                    "action": action,
                    "parent_action": action,
                    "success": l_success,
                    "is_terminal": True,
                }


def iter_grasp_failure_labels(
    segments_info_path: str = "segments_info",
    action: str = "grasp",
) -> Callable[[Path], Iterable[dict]]:
    """Builds a payload iterator factory for SegmentInfo records derived from the
    Reassemble HDF5 `segments_info` group.

    Args:
        segments_info_path: HDF5 group containing per-segment annotations.
        action: Action name carried in each emitted SegmentInfo record.

    Returns:
        A callable that accepts a sequence path and yields SegmentInfo payloads
        (two per segment: one start with `is_terminal=False`, one end with
        `is_terminal=True`).
    """

    def _fn(sequence_path: Path) -> Iterable[dict]:
        yield from _iter_segment_boundaries(sequence_path, segments_info_path, action)

    return _fn


def count_grasp_failure_labels(
    segments_info_path: str = "segments_info",
) -> Callable[[Path], int]:
    """Builds a counter factory matching the payloads produced by
    `iter_grasp_failure_labels`. Returns the total number of records that will
    be emitted (two per segment, including any nested low_level segments).
    """

    def _fn(sequence_path: Path) -> int:
        return sum(1 for _ in _iter_segment_boundaries(sequence_path, segments_info_path))

    return _fn


def iter_records(
    timestamps_path: str,
    fields: dict[str, str],
) -> Callable[[Path], Iterable[dict]]:
    """
    Builds a payload iterator factory for timestamp-aligned HDF5 record arrays.

    Args:
        timestamps_path: HDF5 dataset containing the record timestamps.
        fields: Mapping from payload field names to HDF5 dataset paths.

    Returns:
        A callable that accepts a sequence path and yields record payloads.
    """

    def _fn(sequence_path: Path) -> Iterable[dict]:
        with HDF5Reader(sequence_path) as reader:
            yield from reader.iter_records(
                timestamps_path=timestamps_path,
                fields=fields,
            )

    return _fn


def count_records(timestamps_path: str) -> Callable[[Path], int]:
    """
    Builds a counter factory matching the payloads produced by `iter_records`.

    Args:
        timestamps_path: HDF5 dataset containing the record timestamps.

    Returns:
        A callable that accepts a sequence path and returns the number of records.
    """

    def _fn(sequence_path: Path) -> int:
        with HDF5Reader(sequence_path) as reader:
            return reader.count_records(timestamps_path)

    return _fn


def iter_video_frames(
    video_path: str,
    timestamps_path: str,
) -> Callable[[Path], Iterable[dict]]:
    """
    Builds a payload iterator factory for encoded video frames stored in HDF5.

    Args:
        video_path: HDF5 dataset containing the encoded video stream.
        timestamps_path: HDF5 dataset containing per-frame timestamps.

    Returns:
        A callable that accepts a sequence path and yields frame payloads.
    """

    def _fn(sequence_path: Path) -> Iterable[dict]:
        with HDF5Reader(sequence_path) as reader:
            yield from reader.iter_video_frames(
                video_path=video_path,
                timestamps_path=timestamps_path,
            )

    return _fn


def count_video_frames(timestamps_path: str) -> Callable[[Path], int]:
    """
    Builds a counter factory matching the payloads produced by `iter_video_frames`.

    Args:
        timestamps_path: HDF5 dataset containing per-frame timestamps.

    Returns:
        A callable that accepts a sequence path and returns the frame count.
    """

    def _fn(sequence_path: Path) -> int:
        with HDF5Reader(sequence_path) as reader:
            return reader.count_video_frames(timestamps_path)

    return _fn


def iter_event_frames(
    events_path: str,
    timestamps_path: str,
    window_seconds: float = 0.033,
) -> Callable[[Path], Iterable[dict]]:
    """
    Builds a payload iterator factory for event-camera windows.

    The reader groups raw event streams into fixed temporal windows so the adapter
    receives bounded payloads instead of one unstructured event sequence.

    Args:
        events_path: HDF5 dataset containing the raw events.
        timestamps_path: HDF5 dataset containing per-event timestamps.
        window_seconds: Duration of each aggregation window in seconds.

    Returns:
        A callable that accepts a sequence path and yields event-window payloads.
    """

    def _fn(sequence_path: Path) -> Iterable[dict]:
        with HDF5Reader(sequence_path) as reader:
            yield from reader.iter_event_frames(
                events_path=events_path,
                timestamps_path=timestamps_path,
                window_seconds=window_seconds,
            )

    return _fn


def count_event_frames(
    timestamps_path: str,
    window_seconds: float = 0.033,
) -> Callable[[Path], int]:
    """
    Builds a counter factory matching the payloads produced by `iter_event_frames`.

    Args:
        timestamps_path: HDF5 dataset containing per-event timestamps.
        window_seconds: Duration of each aggregation window in seconds.

    Returns:
        A callable that accepts a sequence path and returns the number of windows.
    """

    def _fn(sequence_path: Path) -> int:
        with HDF5Reader(sequence_path) as reader:
            return reader.count_event_frames(timestamps_path, window_seconds)

    return _fn


def iter_audio(
    audio_path: str,
    timestamps_path: str,
) -> Callable[[Path], Iterable[dict]]:
    """
    Builds a payload iterator factory for chunked audio data.

    Args:
        audio_path: HDF5 dataset containing the audio samples.
        timestamps_path: HDF5 dataset used to infer the temporal extent of the audio.

    Returns:
        A callable that accepts a sequence path and yields audio chunk payloads.
    """

    def _fn(sequence_path: Path) -> Iterable[dict]:
        with HDF5Reader(sequence_path) as reader:
            yield from reader.get_audio(
                audio_path=audio_path,
                timestamps_path=timestamps_path,
            )

    return _fn


def count_audio(audio_path: str, timestamps_path: str) -> Callable[[Path], int]:
    """
    Builds a counter factory matching the payloads produced by `iter_audio`.

    Args:
        audio_path: HDF5 dataset containing the audio samples.
        timestamps_path: HDF5 dataset used to infer the temporal extent of the audio.

    Returns:
        A callable that accepts a sequence path and returns the number of chunks.
    """

    def _fn(sequence_path: Path) -> int:
        with HDF5Reader(sequence_path) as reader:
            return reader.count_audio(
                audio_path=audio_path,
                timestamps_path=timestamps_path,
            )

    return _fn
