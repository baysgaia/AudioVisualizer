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
    confidence: np.ndarray,
    sr: int,
    hop_length: int = 160,  # CREPEのstep_size=10msに対応（10ms * 16000Hz = 160サンプル）
    min_duration: float = 0.1,
    confidence_threshold: float = 0.5  # 信頼度の閾値
) -> List[Tuple[float, float, float]]:
    """
    連続したMIDIノートをインターバル（開始時間、終了時間、ノート）に変換します。

    Args:
        midi_notes: MIDIノート番号の配列
        confidence: CREPEによる信頼度スコアの配列
        sr: サンプリングレート
        hop_length: フレーム間のホップ長（サンプル数）
        min_duration: 最小ノート長（秒）
        confidence_threshold: 信頼度の閾値

    Returns:
        List of (start_time, end_time, note)
    """
    print(f"\nノートインターバル変換デバッグ情報:")
    print(f"入力データ情報:")
    print(f"- MIDIノート配列長: {len(midi_notes)}")
    print(f"- 信頼度配列長: {len(confidence)}")
    print(f"- サンプリングレート: {sr}Hz")
    print(f"- ホップ長: {hop_length}サンプル")
    print(f"- 最小ノート長: {min_duration}秒")
    print(f"- 信頼度閾値: {confidence_threshold}")

    intervals = []
    current_note = None
    start_frame = None
    frame_duration = hop_length / sr  # 1フレームあたりの秒数

    for i, (note, conf) in enumerate(zip(midi_notes, confidence)):
        if conf >= confidence_threshold and not np.isnan(note):
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

def merge_short_notes(
    notes: List[Tuple[float, float, float]],
    min_duration: float = 0.05,
    cent_tolerance: float = 100.0
) -> List[Tuple[float, float, float]]:
    """
    短いノートを前後のノートとマージまたは削除します。

    Args:
        notes: [(start_time, end_time, midi_note), ...] の形式のノートリスト
        min_duration: 最小ノート長（秒）
        cent_tolerance: 同一ノートとみなすセント差の閾値

    Returns:
        マージ処理後のノートリスト
    """
    if not notes:
        return []

    # ノートを時間順にソート
    sorted_notes = sorted(notes, key=lambda x: x[0])
    merged_notes = []
    i = 0

    while i < len(sorted_notes):
        start, end, note = sorted_notes[i]
        duration = end - start

        if duration < min_duration:
            # 前後のノートを確認
            prev_note = merged_notes[-1] if merged_notes else None
            next_note = sorted_notes[i + 1] if i + 1 < len(sorted_notes) else None

            merged = False
            # 前のノートとのマージを試みる
            if prev_note:
                prev_start, prev_end, prev_note_val = prev_note
                if abs(note - prev_note_val) <= cent_tolerance / 100.0:
                    # 前のノートとマージ
                    merged_notes[-1] = (prev_start, end, (prev_note_val * (prev_end - prev_start) + note * duration) / (prev_end - prev_start + duration))
                    merged = True

            # 次のノートとのマージを試みる
            elif next_note and not merged:
                next_start, next_end, next_note_val = next_note
                if abs(note - next_note_val) <= cent_tolerance / 100.0:
                    # 次のノートとマージ
                    sorted_notes[i + 1] = (start, next_end, (note * duration + next_note_val * (next_end - next_start)) / (duration + next_end - next_start))
                    merged = True
                    i += 1
                    continue

            # マージできない場合は短いノートを無視
            if not merged:
                i += 1
                continue
        else:
            merged_notes.append((start, end, note))
        i += 1

    return merged_notes

def smooth_vibrato(
    notes: List[Tuple[float, float, float]],
    time_window: float = 0.2,
    cent_tolerance: float = 200.0
) -> List[Tuple[float, float, float]]:
    """
    ビブラートやしゃくりと思われる短い音程変化を平滑化します。

    Args:
        notes: [(start_time, end_time, midi_note), ...] の形式のノートリスト
        time_window: 検討する時間窓（秒）
        cent_tolerance: ビブラートとみなす音程差の閾値（セント）

    Returns:
        平滑化されたノートリスト
    """
    if not notes:
        return []

    # ノートを時間順にソート
    sorted_notes = sorted(notes, key=lambda x: x[0])
    smoothed_notes = []
    i = 0

    while i < len(sorted_notes):
        current_note = sorted_notes[i]
        current_start, current_end, current_pitch = current_note

        # 時間窓内のノートを収集
        window_notes = []
        j = i
        window_end = current_start + time_window

        while j < len(sorted_notes) and sorted_notes[j][0] < window_end:
            window_notes.append(sorted_notes[j])
            j += 1

        if len(window_notes) > 1:
            # 窓内のノートの音程変化を確認
            pitches = [n[2] for n in window_notes]
            pitch_range = max(pitches) - min(pitches)

            if pitch_range * 100 <= cent_tolerance:  # セント単位に変換して比較
                # ビブラートとみなしてマージ
                merged_start = window_notes[0][0]
                merged_end = window_notes[-1][1]
                # 重み付き平均で新しい音程を計算
                total_duration = sum(n[1] - n[0] for n in window_notes)
                weighted_pitch = sum((n[1] - n[0]) * n[2] for n in window_notes) / total_duration
                
                smoothed_notes.append((merged_start, merged_end, weighted_pitch))
                i = j
                continue

        smoothed_notes.append(current_note)
        i += 1

    return smoothed_notes

# 他に重複定義や未使用関数があればコメントアウトまたは削除