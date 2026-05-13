from mosaicolabs import CompressedImage, ImageFormat, Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class ReassembleVideoFrameAdapter(BaseAdapter[CompressedImage]):
    """
    Adapter for `video_frame` data in Reassemble datasets.

    Translates `video_frame` data from the dataset's message format to the
    `mosaicolabs.CompressedImage` ontology type.
    """

    adapter_id = "reassemble.video_frame"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp", "image")

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
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=CompressedImage(
                data=payload["image"],
                format=ImageFormat.JPEG,
            ),
        )
