from mosaicolabs import CompressedImage, ImageFormat, Message

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class ReassembleVideoFrameAdapter(BaseAdapter):
    adapter_id = "reassemble.video_frame"
    ontology_type = CompressedImage

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=CompressedImage(
                data=payload["image"],
                format=ImageFormat.JPEG,
            ),
        )
