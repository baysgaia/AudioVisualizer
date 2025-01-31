#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pretty_midi
import sys
from pathlib import Path

def analyze_midi(midi_path):
    """MIDIファイルを解析し、詳細情報を表示します。"""
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        
        print(f"\nMIDIファイル解析結果: {Path(midi_path).name}")
        print("-" * 50)
        
        print(f"テンポ: {midi_data.estimate_tempo():.1f} BPM")
        print(f"長さ: {midi_data.get_end_time():.2f} 秒")
        print(f"タイムシグネチャの変更: {len(midi_data.time_signature_changes)}")
        print(f"キーシグネチャの変更: {len(midi_data.key_signature_changes)}")
        
        for i, instrument in enumerate(midi_data.instruments):
            print(f"\nトラック {i+1}:")
            print(f"  名前: {instrument.name if instrument.name else '(未設定)'}")
            print(f"  プログラム番号: {instrument.program}")
            print(f"  ノート数: {len(instrument.notes)}")
            
            if instrument.notes:
                pitches = [note.pitch for note in instrument.notes]
                velocities = [note.velocity for note in instrument.notes]
                durations = [(note.end - note.start) for note in instrument.notes]
                
                print(f"  音域: MIDI {min(pitches)} - {max(pitches)}")
                print(f"  ベロシティ範囲: {min(velocities)} - {max(velocities)}")
                print(f"  ノート長範囲: {min(durations):.3f}秒 - {max(durations):.3f}秒")
                print(f"  平均ノート長: {sum(durations)/len(durations):.3f}秒")
                
                # 最初の5つのノートを表示
                print("\n  最初の5つのノート:")
                for j, note in enumerate(instrument.notes[:5]):
                    print(f"    {j+1}. ピッチ: {note.pitch}, 開始: {note.start:.3f}秒, 長さ: {(note.end - note.start):.3f}秒")
            
            if instrument.lyrics:
                print(f"\n  歌詞イベント数: {len(instrument.lyrics)}")
                print("  最初の3つの歌詞:")
                for lyric in instrument.lyrics[:3]:
                    print(f"    {lyric.text} @ {lyric.time:.3f}秒")
                    
    except Exception as e:
        print(f"エラー: MIDIファイルの解析に失敗しました - {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python analyze_midi.py <midi_file>")
        sys.exit(1)
    
    analyze_midi(sys.argv[1]) 