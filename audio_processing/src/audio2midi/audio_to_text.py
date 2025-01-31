#!/usr/bin/env python
# -*- coding: utf-8 -*-
# audio_processing/src/audio2midi/audio_to_text.py
"""
audio_to_text.py
---------------
Whisperを使って音声ファイルを文字起こしし、結果を表示します。

Usage:
    python audio_to_text.py --audio /path/to/audio.wav [--model small --lang ja]
"""

import os
import argparse
import whisper
import audio2midi.pitch_extraction  # 将来的に使用予定
import audio2midi.note_utils       # 将来的に使用予定
import torch

import sys

# 音声ファイルを文字起こしする函数
def transcribe_audio(audio_path: str, model_name: str = "small", device: str = "cpu") -> str:
    """
    音声ファイルからテキストを取得するための関数。
    日本語のコメントはそのまま残す。
    """
    # Whisperモデルの読み込み
    model = whisper.load_model(model_name, device=device)
    # 実際の文字起こし
    result = model.transcribe(audio_path)
    return result["text"]

def main(audio_path: str, model_name: str = "small", device: str = "cpu"):
    """
    メイン関数。
    日本語のコメントはそのまま残す。
    """
    transcription = transcribe_audio(audio_path, model_name, device)
    print("Transcription:", transcription)

# parse_argumentsを不要であればコメントアウト
# def parse_arguments():
#     # main()が主に使用されるなら、この関数はコメントアウト
#     import argparse
#     parser = argparse.ArgumentParser(description="音声文字起こしの引数処理")
#     parser.add_argument("--audio_path", type=str, required=True)
#     parser.add_argument("--model_name", type=str, default="small")
#     parser.add_argument("--device", type=str, default="cpu")
#     return parser.parse_args()

if __name__ == "__main__":
    # 日本語のコメント: メイン関数を呼び出してCLIからも動作可能にする
    # ここではサンプル引数を直接指定
    main("vocals.wav", "small", "cuda")