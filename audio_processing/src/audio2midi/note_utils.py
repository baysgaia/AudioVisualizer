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
    hop_length: int = 512,  # デフォルトのhop_length
    min_duration: float = 0.1
) -> List[Tuple[float, float, float]]:
    """
    連続したMIDIノートをインターバル（開始時間、終了時間、ノート）に変換します。

    Args:
        midi_notes: MIDIノート番号の配列
        voiced_flags: 有声フレームを示すブール配列
        sr: サンプリングレート
        hop_length: フレーム間のホップ長（サンプル数）
        min_duration: 最小ノート長（秒）

    Returns:
        List of (start_time, end_time, note)
    """
    print(f"\nノートインターバル変換デバッグ情報:")
    print(f"入力データ情報:")
    print(f"- MIDIノート配列長: {len(midi_notes)}")
    print(f"- 有声フラグ配列長: {len(voiced_flags)}")
    print(f"- サンプリングレート: {sr}Hz")
    print(f"- ホップ長: {hop_length}サンプル")
    print(f"- 最小ノート長: {min_duration}秒")

    intervals = []
    current_note = None
    start_frame = None
    frame_duration = hop_length / sr  # 1フレームあたりの秒数

    for i, (note, is_voiced) in enumerate(zip(midi_notes, voiced_flags)):
        if is_voiced and not np.isnan(note):
            if current_note is None:
                current_note = note
                start_frame = i
            elif abs(note - current_note) >= 0.5:  # 半音以上の変化で新しいノート
                duration = (i - start_frame) * frame_duration
                if duration >= min_duration:
                    intervals.append((
                        start_frame * frame_duration,
                        i * frame_duration,
                        round(current_note)
                    ))
                current_note = note
                start_frame = i
        elif current_note is not None:
            duration = (i - start_frame) * frame_duration
            if duration >= min_duration:
                intervals.append((
                    start_frame * frame_duration,
                    i * frame_duration,
                    round(current_note)
                ))
            current_note = None
            start_frame = None

    # 最後のノートの処理
    if current_note is not None:
        duration = (len(midi_notes) - start_frame) * frame_duration
        if duration >= min_duration:
            intervals.append((
                start_frame * frame_duration,
                len(midi_notes) * frame_duration,
                round(current_note)
            ))

    print(f"\n生成されたインターバル:")
    print(f"- インターバル数: {len(intervals)}")
    if intervals:
        print(f"- 時間範囲: {intervals[0][0]:.2f}秒 - {intervals[-1][1]:.2f}秒")
        notes = [interval[2] for interval in intervals]
        print(f"- 音域範囲: {min(notes)} - {max(notes)} (MIDI note)")
        durations = [interval[1] - interval[0] for interval in intervals]
        print(f"- ノート長範囲: {min(durations):.3f}秒 - {max(durations):.3f}秒")
        print(f"- 総時間: {intervals[-1][1]:.2f}秒")
    else:
        print("警告: インターバルが生成されませんでした")

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
    # デバッグ情報の出力
    print("\nデバッグ情報:")
    print(f"セグメント数: {len(segments)}")
    print(f"ノート数: {len(notes)}")
    
    if segments:
        print("\nセグメントの時間範囲:")
        print(f"最初のセグメント: {segments[0]['start']}s - {segments[0]['end']}s")
        print(f"最後のセグメント: {segments[-1]['start']}s - {segments[-1]['end']}s")
    
    if notes:
        print("\nノートの時間範囲:")
        print(f"最初のノート: {notes[0][0]}s - {notes[0][1]}s")
        print(f"最後のノート: {notes[-1][0]}s - {notes[-1][1]}s")

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

    print(f"\nマッチング結果: {len(matched)}個のセグメントが見つかりました")
    return matched

def convert_pitch_to_note(pitch_value):
    """
    ピッチ数値を音名に変換する関数
    日本語コメントをそのまま残す
    """
    # 実際の変換ロジックをここに書く
    pass

# 他に重複定義や未使用関数があればコメントアウトまたは削除