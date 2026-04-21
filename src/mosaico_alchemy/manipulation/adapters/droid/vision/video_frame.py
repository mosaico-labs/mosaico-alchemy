from mosaicolabs import CompressedImage, ImageFormat, Message

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class DroidVideoFrameAdapter(BaseAdapter):
    adapter_id = "droid.video_frame"
    ontology_type = CompressedImage

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=CompressedImage(
                data=payload.get("image"),
                format=ImageFormat.JPEG,
            ),
        )
