"""
Iterator factories for DROID parquet and video-backed episodes.

These helpers adapt DROID's storage model to the callable interface expected by
`TopicDescriptor`. Tabular payloads are read from parquet data, while image payloads
are aligned from companion MP4 files using frame indices and timestamps stored in the
episode records.
"""

import functools
from pathlib import Path
from typing import Callable, Iterable


@functools.lru_cache(maxsize=16)
def _get_parquet_df(real_path: str):
    """Caches the full pandas dataframe loaded from one DROID parquet file."""
    import pyarrow.dataset as ds

    return ds.dataset(real_path, format="parquet").scanner().to_table().to_pandas()


def iter_parquet_records(
    fields: dict[str, str],
    real_path: Path,
    episode_index: int,
) -> Callable[[Path], Iterable[dict]]:
    """
    Builds a payload iterator factory for parquet-backed DROID fields.

    The returned callable ignores the sequence path argument because the concrete
    parquet file and episode index are already bound when the descriptor is created.

    Args:
        fields: Mapping from payload field names to parquet column names.
        real_path: Real parquet file containing the episode data.
        episode_index: Episode to extract from the parquet file.

    Returns:
        A callable that yields one payload per parquet row in the episode.
    """

    def _fn(_ignored_path: Path) -> Iterable[dict]:
        df_all = _get_parquet_df(str(real_path))
        df = df_all[df_all["episode_index"] == episode_index]

        columns_to_read = ["timestamp", "episode_index"] + list(fields.values())
        valid_cols = [c for c in columns_to_read if c in df.columns]
        df = df[valid_cols]

        for row in df.to_dict("records"):
            payload = {"timestamp": row.get("timestamp", 0.0)}
            for out_name, in_name in fields.items():
                if in_name in row:
                    payload[out_name] = row[in_name]
            yield payload

    return _fn


def count_parquet_records(
    real_path: Path,
    episode_index: int,
) -> Callable[[Path], int]:
    """
    Builds a counter factory matching the payloads produced by `iter_parquet_records`.

    Args:
        real_path: Real parquet file containing the episode data.
        episode_index: Episode to count inside the parquet file.

    Returns:
        A callable that returns the number of parquet rows in the episode.
    """

    def _fn(_ignored_path: Path) -> int:
        df_all = _get_parquet_df(str(real_path))
        return int((df_all["episode_index"] == episode_index).sum())

    return _fn


def iter_mp4_frames(
    real_path: Path, episode_index: int, camera_key: str
) -> Callable[[Path], Iterable[dict]]:
    """
    Builds a payload iterator factory for camera frames stored in companion MP4 files.

    DROID image topics are not stored inside the parquet file. Instead, this helper
    resolves the matching MP4 asset, seeks to the first frame of the target episode,
    and emits JPEG-encoded frames aligned to the episode timestamps recorded in parquet.

    Args:
        real_path: Real parquet file describing the episode.
        episode_index: Episode to extract from the parquet file.
        camera_key: Logical camera identifier used to locate the matching MP4 path.

    Returns:
        A callable that yields JPEG image payloads aligned with episode timestamps.
    """

    def _fn(_ignored_path: Path) -> Iterable[dict]:
        import io

        import av
        from PIL import Image

        droid_root = real_path.parent.parent.parent
        videos_dir = droid_root / "videos"

        mp4_path = None
        for p in videos_dir.rglob(f"{real_path.stem}.mp4"):
            if camera_key in p.parts or camera_key.replace("/", ".") in p.parts:
                mp4_path = p
                break

        if not mp4_path or not mp4_path.exists():
            return

        df_all = _get_parquet_df(str(real_path))
        df = df_all[df_all["episode_index"] == episode_index][
            ["episode_index", "index", "timestamp"]
        ]
        if len(df) == 0:
            return

        start_frame = int(df["index"].min())
        timestamps = df["timestamp"].values

        try:
            container = av.open(str(mp4_path))
            stream = container.streams.video[0]

            target_time = start_frame / float(stream.average_rate)
            target_pts = int(target_time / stream.time_base)
            container.seek(target_pts, stream=stream, backward=True)

            frames_iter = container.decode(stream)
            curr_frame = None

            for frame in frames_iter:
                f_idx = int(round(frame.time * float(stream.average_rate)))
                curr_frame = frame
                if f_idx >= start_frame:
                    break

            for timestamp in timestamps:
                img_np = curr_frame.to_ndarray(format="rgb24")

                img = Image.fromarray(img_np)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)

                yield {"timestamp": timestamp, "image": buf.getvalue()}

                curr_frame = next(frames_iter)
        except (StopIteration, Exception):
            pass

    return _fn
