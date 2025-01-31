# python/src/audio2midi/note_utils.py

import numpy as np
from typing import List, Tuple

def midi_notes_to_intervals(f0, voiced_flags, sr):
    """
    Convert pitch information to MIDI intervals.

    Args:
        f0: Pitch array.
        voiced_flags: Boolean array indicating voiced frames.
        sr: Sample rate.

    Returns:
        List of (start_time, end_time, note).
    """
    # 日本語コメント: ノート変換の例示的処理
    intervals = []
    for freq, vf in zip(f0, voiced_flags):
        if vf:
            note = 69 + 12 * np.log2(freq / 440.0)  # A4=440Hz基準
            intervals.append((note, freq))
        else:
            intervals.append((None, None))
    return intervals

def match_segments_and_notes(segments, notes):
    """
    Whisperのセグメント( start, end, text ) リスト と
    ノート情報( start_sec, end_sec, note_val ) をマッチングさせる。

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
    notes_sorted = sorted(notes, key=lambda x: x[0])  # (start_sec, end_sec, val)

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