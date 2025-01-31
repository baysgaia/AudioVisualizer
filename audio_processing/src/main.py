#!/usr/bin/env python
# -*- coding: utf-8 -*-
# /audio_processing/src/main.py
"""
音声文字起こしと音楽情報処理のメインスクリプト

このスクリプトは以下の機能を提供します：
1. 音声文字起こし（Whisper）
2. ピッチ抽出（librosa）
3. 歌詞とピッチのマッチング
4. MIDI/JSON/CSV形式での出力
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

from audio2midi.audio_to_text import transcribe_audio, AudioTranscriptionError
from audio2midi.pitch_extraction import extract_pitch_librosa
from audio2midi.note_utils import midi_notes_to_intervals, match_segments_and_notes
from audio2midi.generate_midi_with_lyrics import export_segments

def get_device() -> str:
    """
    利用可能なデバイス（GPU/CPU）を検出して返します。

    Returns:
        str: 'cuda' (GPU利用可能時) または 'cpu'
    """
    # 日本語コメント: 本来はシステムのGPU/CPUなどをチェックするロジック
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"

def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数をパースします。

    Returns:
        argparse.Namespace: パースされた引数
    """
    parser = argparse.ArgumentParser(description="音声処理パイプライン")
    
    # 入力ファイル
    parser.add_argument("audio_path", type=str, help="音声ファイルパス")
    
    # Whisper関連のオプション
    parser.add_argument("--model-name", type=str, default="large", help="Whisperモデル名")
    parser.add_argument("--device", type=str, help="使用するデバイス (cpu/cuda)")
    parser.add_argument("--language", type=str, help="文字起こしの言語 (例: ja)")
    parser.add_argument("--noise-reduction", action="store_true", help="ノイズ削減を適用する")
    
    # ピッチ抽出オプション
    parser.add_argument("--min-pitch", type=str, default="C2", help="最低音高 (例: C2)")
    parser.add_argument("--max-pitch", type=str, default="C6", help="最高音高 (例: C6)")
    parser.add_argument("--min-duration", type=float, default=0.1, help="最小ノート長（秒）")
    
    # 出力オプション
    parser.add_argument("--output-format", type=str, default="midi",
                      choices=["midi", "json", "csv"], help="出力形式")
    parser.add_argument("--output-path", type=str, help="出力ファイルパス")
    
    # MIDI固有のオプション
    parser.add_argument("--tempo", type=int, default=120, help="MIDIテンポ（BPM）")
    parser.add_argument("--velocity", type=int, default=100, help="MIDIベロシティ（0-127）")
    
    return parser.parse_args()

def process_audio(args: argparse.Namespace) -> None:
    """
    音声処理パイプラインのメイン処理を実行します。

    Args:
        args: コマンドライン引数
    """
    device = args.device or get_device()
    
    try:
        # 1. 音声文字起こし
        print("音声文字起こしを実行中...")
        transcription = transcribe_audio(
            args.audio_path,
            args.model_name,
            device,
            args.language,
            args.noise_reduction
        )
        
        print(f"検出された言語: {transcription.get('language', '不明')}")
        print(f"文字起こし結果: {transcription['text']}")
        
        segments = transcription["segments"]
        if not segments:
            raise AudioTranscriptionError("セグメントが検出されませんでした。")
        
        # 2. ピッチ抽出
        print("ピッチ抽出を実行中...")
        midi_notes, voiced_flags, sr = extract_pitch_librosa(
            args.audio_path,
            fmin=args.min_pitch,
            fmax=args.max_pitch
        )
        
        # 3. ノートインターバルの生成
        print("ノートインターバルを生成中...")
        note_intervals = midi_notes_to_intervals(
            midi_notes,
            voiced_flags,
            sr,
            min_duration=args.min_duration
        )
        
        # 4. 歌詞とノートのマッチング
        print("歌詞とノートをマッチング中...")
        matched_segments = match_segments_and_notes(segments, note_intervals)
        
        # 5. 結果の出力
        output_path = args.output_path or f"output.{args.output_format}"
        print(f"結果を{args.output_format}形式で出力中: {output_path}")
        
        midi_kwargs = {
            "tempo": args.tempo,
            "velocity": args.velocity
        } if args.output_format == "midi" else {}
        
        export_segments(
            matched_segments,
            output_path,
            format=args.output_format,
            **midi_kwargs
        )
        
        print("処理が完了しました！")
        
    except (FileNotFoundError, AudioTranscriptionError) as e:
        print(f"エラーが発生しました: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main() -> None:
    """
    メイン実行関数。コマンドライン引数を処理し、パイプラインを実行します。
    """
    args = parse_args()
    process_audio(args)

if __name__ == "__main__":
    main() 