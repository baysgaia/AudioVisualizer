#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
# 日本語コメント: argparseのインポート
# from audio_processing.src.audio2midi.pitch_extraction import extract_pitch  # 未使用ならコメントアウト
# ↓ 不要な場合はコメントアウト
# from audio_processing.src.audio2midi.some_unused_module import something_unused

# ↓ 「audio_processing」としてトップレベルではないなら、以下のように修正
# from audio2midi.audio_to_text import transcribe_audio
from audio2midi.audio_to_text import transcribe_audio  # インポート先を変更
import sys
# from some_unused_module import unused_function  # 未使用のためコメントアウト

# 日本語コメント: これはデバイスを取得するための関数
def get_device():
    # 日本語コメント: 本来はシステムのGPU/CPUなどをチェックするロジック
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"

def main():
    # 日本語コメント: メインのフローを行う
    if len(sys.argv) < 3:
        print("Usage: python main.py <audio_path> <model_name>")
        return

    audio_path = sys.argv[1]
    model_name = sys.argv[2]
    device = get_device()

    # 日本語コメント: transcribe_audio 関数を呼び出す
    # シグネチャは (audio_path, model_name, device) で統一
    result = transcribe_audio(audio_path, model_name, device)
    print("Transcription Result:", result)

if __name__ == "__main__":
    main() 