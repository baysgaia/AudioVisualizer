#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
whisper_test.py
---------------
Whisperを使って音声ファイルを文字起こしし、結果を表示します。

Usage:
    python whisper_test.py --audio /path/to/audio.wav [--model base --lang ja]
"""

import os
import argparse
import whisper

def parse_arguments():
    parser = argparse.ArgumentParser(description="Whisper test script")

    # スクリプトが置かれているディレクトリを基準に、input_mix.wav へのパスを生成
    script_dir = os.path.dirname(__file__)
    # ルートディレクトリにある input_mix.wav を想定 ( ../.. で2階層上がる 例 )
    default_audio_path = os.path.abspath(os.path.join(script_dir, "../../input_mix.wav"))

    parser.add_argument(
        "--audio",
        required=False,
        default=default_audio_path,  # デフォルトで input_mix.wav を参照
        help=f"Path to the audio file. Default: {default_audio_path}"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="large",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size. Default is 'large'."
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="ja",
        help="Language code (e.g. 'ja' for Japanese). Default is 'ja'."
    )
    return parser.parse_args()

def main():
    args = parse_arguments()

    # Audioファイルの存在チェック
    if not os.path.exists(args.audio):
        raise FileNotFoundError(f"Audio file not found: {args.audio}")

    # Whisperモデルのロード
    print(f"Loading Whisper model: {args.model}")
    model = whisper.load_model(args.model)

    # 音声を文字起こし
    print(f"Transcribing audio: {args.audio}")
    result = model.transcribe(args.audio, language=args.lang)

    # 結果表示
    print("=== Transcribed Text ===")
    print(result["text"])

    # セグメントごとの詳細
    print("\n=== Segments ===")
    for seg in result["segments"]:
        print(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}")

if __name__ == "__main__":
    main()