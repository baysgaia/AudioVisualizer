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
    velocity: int = 100
) -> None:
    """
    マッチングされたセグメントからMIDIファイルを生成します。
    
    Args:
        matched_segments: マッチングされたセグメントのリスト
        output_file: 出力MIDIファイルパス
        tempo: テンポ（BPM）
        velocity: ノートのベロシティ（0-127）
    """
    midi = MIDIFile(1)  # 1トラック
    track = 0
    time = 0
    midi.addTrackName(track, time, "Vocal Track")
    midi.addTempo(track, time, tempo)
    
    for segment in matched_segments:
        note = segment["note_segment"]["note"]
        start = segment["overlap_start"]
        end = segment["overlap_end"]
        duration = end - start
        text = segment["text_segment"]["text"]
        
        # ノートイベントを追加
        midi.addNote(track, 0, int(note), start, duration, velocity)
        
        # 歌詞イベントを追加
        midi.addLyric(track, start, text)
    
    with open(output_file, "wb") as f:
        midi.writeFile(f)

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