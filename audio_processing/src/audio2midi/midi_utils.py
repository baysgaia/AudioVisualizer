#!/usr/bin/env python
# -*- coding: utf-8 -*-
# /audio_processing/src/audio2midi/midi_utils.py
"""
MIDIファイル生成のためのユーティリティモジュール
"""

from typing import List, Tuple
import mido

def note_events_to_midi(
    note_events: List[Tuple[float, float, float]],
    out_path: str = "output.mid",
    bpm: int = 120,
    velocity: int = 64,
    ticks_per_beat: int = 480
) -> None:
    """
    ノートイベントのリストからMIDIファイルを生成します。

    Args:
        note_events: [(start_time, end_time, note_value), ...] の形式のノートリスト
        out_path: 出力MIDIファイルのパス
        bpm: テンポ（拍/分）
        velocity: ノートのベロシティ（0-127）
        ticks_per_beat: 1拍あたりのtick数
    """
    # MIDIファイルとトラックの作成
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack(name="Vocal")
    mid.tracks.append(track)

    # テンポ設定
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))

    # 前回のイベントのtick位置を記録
    prev_tick = 0

    # ノートイベントをソート
    sorted_events = sorted(note_events, key=lambda x: x[0])

    for start_time, end_time, note_val in sorted_events:
        # 音高を整数に丸める
        note_int = int(round(note_val))
        if not 0 <= note_int <= 127:
            print(f"Warning: Note value {note_int} out of MIDI range (0-127), skipping")
            continue

        # 秒→ticks変換
        start_tick = int((start_time * ticks_per_beat * bpm) / 60.0)
        end_tick = int((end_time * ticks_per_beat * bpm) / 60.0)

        # Note Onイベント
        delta_on = start_tick - prev_tick
        track.append(mido.Message(
            'note_on',
            note=note_int,
            velocity=velocity,
            time=delta_on
        ))

        # Note Offイベント
        delta_off = end_tick - start_tick
        track.append(mido.Message(
            'note_off',
            note=note_int,
            velocity=velocity,
            time=delta_off
        ))

        # 前回のtick位置を更新
        prev_tick = end_tick

    # MIDIファイルの保存
    try:
        mid.save(out_path)
        print(f"Successfully saved MIDI file to {out_path}")
    except Exception as e:
        print(f"Error saving MIDI file: {e}") 