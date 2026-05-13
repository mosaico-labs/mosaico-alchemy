from mosaicolabs import CompressedImage, ImageFormat, Message
from PIL import Image as PILImage

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class FractalRT1VideoFrameAdapter(BaseAdapter[CompressedImage]):
    """
    Adapter for `video_frame` topic from FractalRT1 datasets.

    Translated from `video_frame` message (custom Protocol Buffers) to
    `mosaicolabs.CompressedImage`.
    """

    adapter_id = "fractal_rt1.video_frame"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "image")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `video_frame` payload into a `mosaicolabs.CompressedImage` message.

        Args:
            payload: Raw payload from the `video_frame` topic.

        Returns:
            A `Message` containing the `mosaicolabs.CompressedImage` data.
        """
        cls._validate_payload(payload=payload)
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=CompressedImage.from_image(
                PILImage.fromarray(payload["image"]),
                format=ImageFormat.JPEG,
                quality=90,
            ),
        )
