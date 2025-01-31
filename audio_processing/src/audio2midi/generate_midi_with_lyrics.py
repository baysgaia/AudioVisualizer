#!/usr/bin/env python
# -*- coding: utf-8 -*-
# /audio_processing/src/audio2midi/generate_midi_with_lyrics.py
"""
マッチングされたセグメントからMIDIファイルやその他の形式のファイルを生成するモジュール
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Optional
from midiutil import MIDIFile

def create_midi_with_lyrics(
    matched_segments: List[Dict],
    output_file: str,
    tempo: int = 120,
    velocity: int = 100,
    min_duration: float = 0.1,  # 最小ノート長を追加
    text_offset: float = 0.01   # テキストイベントのオフセットを追加
) -> None:
    """
    マッチングされたセグメントからMIDIファイルを生成します。
    
    Args:
        matched_segments: マッチングされたセグメントのリスト
        output_file: 出力MIDIファイルパス
        tempo: テンポ（BPM）
        velocity: ノートのベロシティ（0-127）
        min_duration: 最小ノート長（秒）
        text_offset: テキストイベントの時間オフセット（秒）
    """
    midi = MIDIFile(2)  # 2トラックに変更（ノート用とテキスト用）
    note_track = 0
    text_track = 1
    time = 0

    midi.addTrackName(note_track, time, "Vocal Notes")
    midi.addTrackName(text_track, time, "Lyrics")
    midi.addTempo(note_track, time, tempo)
    midi.addTempo(text_track, time, tempo)
    
    # デバッグ情報の出力
    print(f"Processing {len(matched_segments)} matched segments")
    
    # セグメントを時間でソート
    sorted_segments = sorted(matched_segments, key=lambda x: x["overlap_start"])
    
    for i, segment in enumerate(sorted_segments):
        note = segment["note_segment"]["note"]
        start = segment["overlap_start"]
        end = segment["overlap_end"]
        duration = end - start
        text = segment["text_segment"]["text"]
        
        # バリデーションチェックを追加
        if start < 0 or end < 0:
            print(f"Warning: Negative time values at segment {i} - start: {start}, end: {end}")
            continue
            
        if duration < min_duration:
            print(f"Warning: Duration {duration}s is less than minimum {min_duration}s at segment {i}")
            continue
            
        if not (0 <= int(note) <= 127):
            print(f"Warning: Invalid MIDI note number {note} at segment {i}")
            continue
        
        # ノートイベントを追加（ノートトラックに）
        try:
            midi.addNote(note_track, 0, int(note), start, duration, velocity)
            # テキストイベントを別トラックに追加（わずかな時間オフセットを付ける）
            midi.addText(text_track, start + text_offset, text)
            print(f"Added note {int(note)} at {start}s with duration {duration}s and text '{text}'")
        except Exception as e:
            print(f"Error adding note at segment {i}: {e}")
            print(f"Segment details: note={note}, start={start}, duration={duration}, text='{text}'")
            continue

    # MIDIファイルの書き出し
    try:
        with open(output_file, "wb") as f:
            midi.writeFile(f)
        print(f"Successfully wrote MIDI file to {output_file}")
    except Exception as e:
        print(f"Error writing MIDI file: {e}")

def export_to_json(
    matched_segments: List[Dict],
    output_file: str
) -> None:
    """
    マッチングされたセグメントをJSONファイルとして出力します。
    
    Args:
        matched_segments: マッチングされたセグメントのリスト
        output_file: 出力JSONファイルパス
    """
    output_data = {
        "segments": matched_segments,
        "metadata": {
            "total_segments": len(matched_segments),
            "format_version": "1.0"
        }
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

def export_to_csv(
    matched_segments: List[Dict],
    output_file: str
) -> None:
    """
    マッチングされたセグメントをCSVファイルとして出力します。
    
    Args:
        matched_segments: マッチングされたセグメントのリスト
        output_file: 出力CSVファイルパス
    """
    fieldnames = [
        "start_time", "end_time", "text",
        "note", "note_start", "note_end"
    ]
    
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for segment in matched_segments:
            writer.writerow({
                "start_time": segment["overlap_start"],
                "end_time": segment["overlap_end"],
                "text": segment["text_segment"]["text"],
                "note": segment["note_segment"]["note"],
                "note_start": segment["note_segment"]["start"],
                "note_end": segment["note_segment"]["end"]
            })

def export_segments(
    matched_segments: List[Dict],
    output_path: str,
    format: str = "midi",
    **kwargs
) -> None:
    """
    マッチングされたセグメントを指定された形式で出力します。
    
    Args:
        matched_segments: マッチングされたセグメントのリスト
        output_path: 出力ファイルパス
        format: 出力形式 ("midi", "json", "csv")
        **kwargs: 各形式固有のオプション
    """
    output_path = Path(output_path)
    
    if format == "midi":
        create_midi_with_lyrics(matched_segments, str(output_path), **kwargs)
    elif format == "json":
        export_to_json(matched_segments, str(output_path))
    elif format == "csv":
        export_to_csv(matched_segments, str(output_path))
    else:
        raise ValueError(f"Unsupported format: {format}")