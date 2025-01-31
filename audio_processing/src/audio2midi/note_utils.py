#!/usr/bin/env python
# -*- coding: utf-8 -*-
# /audio_processing/src/audio2midi/note_utils.py
"""
音符とセグメントの処理に関するユーティリティモジュール
"""

from typing import List, Tuple, Dict, Any, Union, Optional
import numpy as np

def midi_notes_to_intervals(
    midi_notes: np.ndarray,
    voiced_flags: np.ndarray,
    sr: int,
    min_duration: float = 0.1
) -> List[Tuple[float, float, float]]:
    """
    連続したMIDIノートをインターバル（開始時間、終了時間、ノート）に変換します。

    Args:
        midi_notes: MIDIノート番号の配列
        voiced_flags: 有声フレームを示すブール配列
        sr: サンプリングレート
        min_duration: 最小ノート長（秒）

    Returns:
        List of (start_time, end_time, note)
    """
    intervals = []
    current_note = None
    start_frame = None
    frame_length = 1.0 / sr

    for i, (note, is_voiced) in enumerate(zip(midi_notes, voiced_flags)):
        if is_voiced and not np.isnan(note):
            if current_note is None:
                current_note = note
                start_frame = i
            elif abs(note - current_note) >= 0.5:  # 半音以上の変化で新しいノート
                duration = (i - start_frame) * frame_length
                if duration >= min_duration:
                    intervals.append((
                        start_frame * frame_length,
                        i * frame_length,
                        round(current_note)
                    ))
                current_note = note
                start_frame = i
        elif current_note is not None:
            duration = (i - start_frame) * frame_length
            if duration >= min_duration:
                intervals.append((
                    start_frame * frame_length,
                    i * frame_length,
                    round(current_note)
                ))
            current_note = None
            start_frame = None

    # 最後のノートの処理
    if current_note is not None:
        duration = (len(midi_notes) - start_frame) * frame_length
        if duration >= min_duration:
            intervals.append((
                start_frame * frame_length,
                len(midi_notes) * frame_length,
                round(current_note)
            ))

    return intervals

def match_segments_and_notes(
    segments: List[Dict[str, Union[float, str]]],
    notes: List[Tuple[float, float, float]]
) -> List[Dict[str, Any]]:
    """
    Whisperのセグメント(start, end, text)リストと
    ノート情報(start_sec, end_sec, note_val)をマッチングさせます。

    Parameters
    ----------
    segments : list of dict
        例: [{"start": 2.0, "end": 3.5, "text": "あ"}, ...]
    notes : list of tuple
        例: [(start_sec, end_sec, note_val), ...]

    Returns
    -------
    list of dict
        [
          {
            "text_segment": {"start":..., "end":..., "text":...},
            "note_segment": {"start":..., "end":..., "note":...},
            "overlap_start": float,
            "overlap_end": float
          },
          ...
        ]
    """
    matched = []
    i, j = 0, 0
    segments_sorted = sorted(segments, key=lambda x: x["start"])
    notes_sorted = sorted(notes, key=lambda x: x[0])

    while i < len(segments_sorted) and j < len(notes_sorted):
        w = segments_sorted[i]
        n = notes_sorted[j]
        w_start, w_end = w["start"], w["end"]
        n_start, n_end, n_val = n

        overlap_start = max(w_start, n_start)
        overlap_end = min(w_end, n_end)

        if overlap_start < overlap_end:
            matched.append({
                "text_segment": w,
                "note_segment": {
                    "start": n_start,
                    "end": n_end,
                    "note": n_val
                },
                "overlap_start": overlap_start,
                "overlap_end": overlap_end
            })

        if w_end < n_end:
            i += 1
        else:
            j += 1

    return matched

def convert_pitch_to_note(pitch_value):
    """
    ピッチ数値を音名に変換する関数
    日本語コメントをそのまま残す
    """
    # 実際の変換ロジックをここに書く
    pass

# 他に重複定義や未使用関数があればコメントアウトまたは削除