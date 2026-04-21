"""
Audio Data Structures.

This module defines ontology models for audio payloads and stream metadata.
The structures are designed to preserve encoded audio as exported by source datasets,
so ingestion can remain lossless and codec decisions can stay downstream.
"""

from enum import Enum
from typing import Optional

from mosaicolabs import MosaicoField, MosaicoType, Serializable


class AudioFormat(str, Enum):
    """Supported audio coding formats.

    This enum exists so adapters coming from different datasets can describe the same
    encoding family with a stable shared vocabulary rather than source-specific
    strings.
    """

    WAVE = "wave"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    AAC = "aac"
    OPUS = "opus"
    M4A = "m4a"


class AudioInfo(Serializable):
    """Describe how an audio payload should be decoded.

    This model is separate from `AudioData` because dataset exports do not expose
    audio metadata in a uniform way. Some sources publish it once per stream, some
    repeat it for every chunk, and some omit parts of it entirely. Keeping it
    optional and detached lets adapters preserve what is known without inventing
    defaults or duplicating metadata unnecessarily.

    Attributes:
        channels: Number of channels when known.
        sample_rate: Sampling rate in hertz when known.
        sample_format: Low-level sample representation, such as `s16le`.
        bitrate: Encoded bitrate in bits per second when available.
        coding_format: Declared coding format for the payload.
    """

    __ontology_tag__ = "audio_info"

    channels: MosaicoType.uint8 = MosaicoField(
        nullable=True,
        description="Number of audio channels in the stream.",
    )
    sample_rate: MosaicoType.uint32 = MosaicoField(
        nullable=True,
        description="Sampling rate of the audio stream in hertz.",
    )
    sample_format: MosaicoType.string = MosaicoField(
        nullable=True,
        description="Sample representation format, for example s16le or float32.",
    )
    bitrate: Optional[MosaicoType.uint32] = MosaicoField(
        default=None,
        description="Encoded bitrate of the audio stream in bits per second when available.",
    )
    coding_format: MosaicoType.string = MosaicoField(
        nullable=True,
        description="Declared coding format of the audio stream.",
    )


class AudioData(Serializable):
    """Store encoded audio bytes without forcing a decode step during ingestion.

    This model exists because the pack should preserve the source payload as-is when
    possible. Decoding during ingestion would be more opinionated, potentially lossy,
    and would couple the pipeline to codec-specific runtime behavior.

    Attributes:
        data: Binary payload containing encoded audio bytes.
    """

    __ontology_tag__ = "audio_data"

    data: MosaicoType.binary = MosaicoField(
        description="Binary payload containing the audio data."
    )


class AudioDataStamped(Serializable):
    """Bind one audio payload to the best metadata known at ingestion time.

    The wrapper exists for chunked or message-oriented datasets where bytes and
    stream information conceptually belong together, even when the metadata is only
    partially available.

    Attributes:
        audio_data: Audio payload for the current message or chunk.
        audio_info: Optional stream metadata associated with the payload.
    """

    __ontology_tag__ = "audio_data_stamped"

    audio_data: AudioData = MosaicoField(
        description="Audio payload for the current message."
    )
    audio_info: Optional[AudioInfo] = MosaicoField(
        default=None,
        description="Optional metadata describing the audio payload.",
    )
