"""
Iterator factories for Reassemble HDF5 sequences.

These helpers adapt `HDF5Reader` methods to the callable shape expected by
`TopicDescriptor`: a factory receives static dataset paths up front and returns a
function that can later stream or count data for one concrete sequence file.
"""

from pathlib import Path
from typing import Callable, Iterable

from mosaico_alchemy.manipulation.readers import HDF5Reader


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
