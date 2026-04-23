"""
Reader utilities for file-backed HDF5 manipulation datasets.

This module wraps raw HDF5 access behind a small context-managed API tailored to the
payload shapes expected by `TopicDescriptor` iterators. The reader centralizes
record extraction, video decoding, event windowing, and audio chunking so dataset
plugins can stay declarative.
"""

from pathlib import Path
from typing import Iterable

import h5py
import numpy as np

from mosaico_alchemy.manipulation.utils.extract_video_frame import (
    extract_video_frames,
)


class HDF5Reader:
    """
    Context-managed reader for HDF5-backed manipulation sequences.

    The reader keeps file-handle lifetime explicit and exposes higher-level helpers
    that normalize raw datasets into payloads ready for adapters. This avoids
    duplicating HDF5 traversal logic across dataset plugins and iterator factories.
    """

    def __init__(self, file_path: Path):
        """Initializes the reader for one HDF5 sequence file."""
        self.file_path = file_path
        self._handle = None

    def __enter__(self):
        """Opens the HDF5 file and returns the active reader instance."""
        self._handle = h5py.File(self.file_path, "r")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Closes the underlying HDF5 handle when leaving the context manager."""
        if self._handle is not None:
            self._handle.close()
            self._handle = None
        return None

    def missing_paths(self, paths: Iterable[str]) -> tuple[str, ...]:
        """
        Returns the dataset-relative paths that are missing from the open HDF5 file.

        Args:
            paths: HDF5 paths required by a topic or sequence plan.

        Returns:
            A tuple containing only the paths that do not exist in the file.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        return tuple(path for path in paths if path not in self._handle)

    def iter_records(self, timestamps_path: str, fields: dict[str, str]):
        """
        Yields timestamp-aligned record payloads from one or more HDF5 datasets.

        Args:
            timestamps_path: Path to the timestamp dataset driving record alignment.
            fields: Mapping from output payload names to HDF5 dataset paths.

        Yields:
            Dictionaries containing one `timestamp` plus the requested fields.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        timestamps = self._handle[timestamps_path][:]
        fields_value = {
            fields_name: self._handle[fields_path][:]
            for fields_name, fields_path in fields.items()
        }

        for i, ts in enumerate(timestamps):
            payload = {"timestamp": ts}
            for field_name, field_value in fields_value.items():
                payload[field_name] = field_value[i]
            yield payload

    def count_records(self, timestamps_path: str) -> int:
        """
        Returns the number of timestamped records available for one dataset group.

        Args:
            timestamps_path: Path to the timestamp dataset driving record alignment.

        Returns:
            The number of records described by the timestamp dataset.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        return len(self._handle[timestamps_path])

    def iter_video_frames(self, video_path: str, timestamps_path: str):
        """
        Yields decoded video frames aligned with the provided timestamp dataset.

        Args:
            video_path: Path to the encoded video blob inside the HDF5 file.
            timestamps_path: Path to the per-frame timestamps.

        Yields:
            Dictionaries containing `timestamp` and JPEG-encoded `image` bytes.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        timestamps = self._handle[timestamps_path][:]
        yield from extract_video_frames(self._handle, video_path, timestamps)

    def count_video_frames(self, timestamps_path: str) -> int:
        """
        Returns the number of video frames expected from one timestamp dataset.

        Args:
            timestamps_path: Path to the per-frame timestamps.

        Returns:
            The number of timestamps, used as the expected frame count.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        return len(self._handle[timestamps_path])

    def _event_window_layout(
        self,
        timestamps_path: str,
        window_seconds: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
        """
        Computes the event-window boundaries used for event-camera aggregation.

        The layout is derived from raw per-event timestamps and reused by both the
        iterator and counter methods so they agree on window count and boundaries.

        Args:
            timestamps_path: Path to the per-event timestamps in seconds.
            window_seconds: Requested duration of each event window.

        Returns:
            Raw timestamps in nanoseconds, window boundaries, split indices, and the
            total number of windows.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
            ValueError: If `window_seconds` is not strictly positive.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")

        timestamps_seconds = self._handle[timestamps_path][:]
        if len(timestamps_seconds) == 0:
            empty = np.array([], dtype=np.int64)
            return empty, empty, empty, 0

        timestamps_ns = np.rint(timestamps_seconds * 1e9).astype(np.int64)
        window_ns = int(round(window_seconds * 1e9))

        first_ts = int(timestamps_ns[0])
        last_ts = int(timestamps_ns[-1])
        num_windows = int(np.ceil((last_ts - first_ts + 1) / window_ns))
        boundaries_ns = (
            first_ts + np.arange(num_windows + 1, dtype=np.int64) * window_ns
        )
        split_indices = np.searchsorted(timestamps_ns, boundaries_ns, side="left")

        return timestamps_ns, boundaries_ns, split_indices, num_windows

    def iter_event_frames(
        self, events_path: str, timestamps_path: str, window_seconds: float = 0.033
    ):
        """
        Yields fixed-duration event-camera windows from a raw event stream.

        Each yielded payload contains the events that fall into one temporal window,
        plus the window boundaries and a representative timestamp. Empty windows are
        preserved so downstream ingestion keeps a stable temporal grid.

        Args:
            events_path: Path to the raw event dataset.
            timestamps_path: Path to the per-event timestamps in seconds.
            window_seconds: Duration of each aggregation window in seconds.

        Yields:
            Dictionaries containing window timestamps, boundaries, and sliced events.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
            ValueError: If `window_seconds` is not strictly positive.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        timestamps_ns, boundaries_ns, split_indices, num_windows = (
            self._event_window_layout(timestamps_path, window_seconds)
        )
        if num_windows == 0:
            return

        events_dataset = self._handle[events_path]

        for i in range(num_windows):
            start_idx = int(split_indices[i])
            end_idx = int(split_indices[i + 1])
            w_start = int(boundaries_ns[i])
            w_end = int(boundaries_ns[i + 1])

            event_timestamps_ns = timestamps_ns[start_idx:end_idx]

            yield {
                "timestamp_ns": int(event_timestamps_ns[-1])
                if end_idx > start_idx
                else w_end,
                "t_start_ns": w_start,
                "t_end_ns": w_end,
                "events": events_dataset[start_idx:end_idx],
                "event_timestamps_ns": event_timestamps_ns,
            }

    def count_event_frames(
        self,
        timestamps_path: str,
        window_seconds: float = 0.033,
    ) -> int:
        """
        Returns the number of event windows produced for a timestamp stream.

        Args:
            timestamps_path: Path to the per-event timestamps in seconds.
            window_seconds: Duration of each aggregation window in seconds.

        Returns:
            The number of event windows implied by the timestamp range.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
            ValueError: If `window_seconds` is not strictly positive.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        _, _, _, num_windows = self._event_window_layout(
            timestamps_path,
            window_seconds,
        )
        return num_windows

    def get_audio(
        self,
        audio_path: str,
        timestamps_path: str,
        max_chunk_bytes: int = 10 * 1024 * 1024,
    ):
        """
        Yields audio payloads chunked to stay under a target byte size.

        Audio in these datasets is stored as one contiguous array. This helper splits
        it into bounded chunks and interpolates chunk timing from the sequence-level
        timestamp range so the resulting payloads remain streamable.

        Args:
            audio_path: Path to the audio samples dataset.
            timestamps_path: Path to timestamps used to infer the audio time span.
            max_chunk_bytes: Maximum target size for each yielded chunk.

        Yields:
            Dictionaries containing chunk start time, duration, and audio samples.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        timestamps = self._handle[timestamps_path][:]
        if len(timestamps) == 0:
            return

        ts_start = float(timestamps[0])
        ts_end = float(timestamps[-1])
        ts_duration = ts_end - ts_start

        audio_data = self._handle[audio_path][:]
        n_samples = len(audio_data)
        if n_samples == 0:
            return

        bytes_per_sample = audio_data.dtype.itemsize * (
            audio_data.shape[1] if audio_data.ndim > 1 else 1
        )
        samples_per_chunk = max(1, max_chunk_bytes // bytes_per_sample)

        for i in range(0, n_samples, samples_per_chunk):
            chunk = audio_data[i : i + samples_per_chunk]
            chunk_ts_start = ts_start + (i / n_samples) * ts_duration
            chunk_duration = (len(chunk) / n_samples) * ts_duration
            yield {
                "ts_start": chunk_ts_start,
                "ts_duration": chunk_duration,
                "audio": chunk,
            }

    def count_audio(
        self,
        audio_path: str,
        timestamps_path: str,
        max_chunk_bytes: int = 10 * 1024 * 1024,
    ) -> int:
        """
        Returns the number of audio chunks that `get_audio` would emit.

        Args:
            audio_path: Path to the audio samples dataset.
            timestamps_path: Path to timestamps used to infer the audio time span.
            max_chunk_bytes: Maximum target size for each audio chunk.

        Returns:
            The number of chunks implied by the audio size and chunk budget.

        Raises:
            RuntimeError: If the reader is used outside its context manager.
        """
        if self._handle is None:
            raise RuntimeError("HDF5Reader is not open")

        timestamps = self._handle[timestamps_path][:]
        if len(timestamps) == 0:
            return 0

        audio_data = self._handle[audio_path]
        n_samples = audio_data.shape[0]
        if n_samples == 0:
            return 0

        bytes_per_sample = audio_data.dtype.itemsize * (
            audio_data.shape[1] if len(audio_data.shape) > 1 else 1
        )
        samples_per_chunk = max(1, max_chunk_bytes // bytes_per_sample)
        return int(np.ceil(n_samples / samples_per_chunk))
