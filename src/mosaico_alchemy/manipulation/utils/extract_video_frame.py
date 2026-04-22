"""
Video frame extraction helpers.

This module provides the small utility used to decode embedded video payloads from
HDF5 datasets into per-frame records that match the ingestion pipeline contract.
"""

import io


def _resolve_timestamp(frame_idx, frame, timestamps):
    """Choose the most reliable timestamp for a decoded frame.

    The helper prefers explicit dataset timestamps when available, falls back to the
    container-provided frame time, and only uses `0.0` as a last resort so callers
    get a stable numeric timestamp even for imperfect exports.
    """
    if frame_idx < len(timestamps):
        return timestamps[frame_idx]
    if frame.time is not None:
        return float(frame.time)
    return 0.0


def _encode_jpeg(frame):
    """Convert a decoded frame to JPEG bytes for downstream ingestion."""
    image = frame.to_image()
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


def extract_video_frames(h5_handle, video_dataset_path, timestamps):
    """Yield decoded video frames as timestamped JPEG payloads.

    This helper exists because some datasets embed full video streams inside HDF5
    blobs rather than storing one image per sample. Decoding them here lets plugins
    keep their ingestion plans record-oriented while preserving the original stream as
    close as possible to frame-level messages.

    Args:
        h5_handle: Open HDF5 handle containing the encoded video dataset.
        video_dataset_path: Path to the dataset holding the raw video bytes.
        timestamps: Sequence of per-frame timestamps supplied by the dataset, when
            available.

    Yields:
        Dictionaries with `timestamp` and JPEG-encoded `image` entries, matching the
        shape expected by file-backed video adapters.
    """
    import av

    video_bytes = bytes(h5_handle[video_dataset_path][()])
    timestamps = list(timestamps)

    with av.open(io.BytesIO(video_bytes), mode="r") as container:
        stream = container.streams.video[0]

        for frame_idx, frame in enumerate(container.decode(stream)):
            yield {
                "timestamp": _resolve_timestamp(frame_idx, frame, timestamps),
                "image": _encode_jpeg(frame),
            }
