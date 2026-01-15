"""Business services for transcribe application.

Services are organized by domain:
- audio: Audio streaming and chunk management
- transcription: Transcription processing and segment handling
- meeting: Meeting lifecycle orchestration
"""

from .audio import cleanup_audio, stream_and_split_audio
from .meeting import (
    finalize_transcription,
    get_meeting_status,
    mark_meeting_failed,
    start_transcription,
    update_meeting_audio_url,
)
from .transcription import (
    adjust_segment_timestamps,
    merge_segments,
    segments_to_text,
    transcribe_audio_file,
)

__all__ = [
    "adjust_segment_timestamps",
    "cleanup_audio",
    "finalize_transcription",
    "get_meeting_status",
    "mark_meeting_failed",
    "merge_segments",
    "segments_to_text",
    # Meeting services
    "start_transcription",
    # Audio services
    "stream_and_split_audio",
    # Transcription services
    "transcribe_audio_file",
    "update_meeting_audio_url",
]
