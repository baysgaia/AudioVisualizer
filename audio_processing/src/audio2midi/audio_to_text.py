#!/usr/bin/env python
# -*- coding: utf-8 -*-
# /audio_processing/src/audio2midi/audio_to_text.py
"""
音声ファイルをテキストに変換するモジュール

このモジュールは、Whisperライブラリを使用して音声ファイルから
テキストを抽出するための機能を提供します。ノイズ削減やゲイン調整の
前処理オプションも含まれています。

Usage:
    from audio2midi.audio_to_text import transcribe_audio
    
    text = transcribe_audio(
        audio_path="../../audio.wav",
        model_name="large",
        device="cpu",
        language="ja",
        noise_reduction=True
    )

Command line:
    python audio_to_text.py --audio ../../audio.wav [--model large --device cpu --language ja --noise-reduction]
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any

import torch
import whisper
from pydub import AudioSegment
from pydub.effects import normalize

class AudioTranscriptionError(Exception):
    """音声文字起こし処理中のエラーを表すカスタム例外クラス"""
    pass

def preprocess_audio(
    audio_path: str,
    output_path: Optional[str] = None,
    noise_reduction: bool = False
) -> str:
    """
    音声ファイルの前処理を行います。

    Args:
        audio_path (str): 入力音声ファイルのパス
        output_path (str, optional): 出力音声ファイルのパス
        noise_reduction (bool): ノイズ削減を適用するかどうか

    Returns:
        str: 処理済み音声ファイルのパス

    Raises:
        AudioTranscriptionError: 音声処理に失敗した場合
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        
        if noise_reduction:
            # ノーマライズして音量を調整
            audio = normalize(audio)
            
            # 必要に応じて他のノイズ削減処理を追加可能
            # 例: ローパスフィルター、ハイパスフィルターなど
        
        if output_path is None:
            output_path = str(Path(audio_path).with_suffix('.processed.wav'))
        
        audio.export(output_path, format='wav')
        return output_path
    
    except Exception as e:
        raise AudioTranscriptionError(f"音声前処理中にエラーが発生しました: {str(e)}")

def transcribe_audio(
    audio_path: str,
    model_name: str = "large",
    device: str = "cpu",
    language: Optional[str] = None,
    noise_reduction: bool = False
) -> Dict[str, Any]:
    """
    音声ファイルからテキストを抽出します。

    Args:
        audio_path (str): 音声ファイルのパス
        model_name (str): 使用するWhisperモデル名. Defaults to "large".
        device (str): 使用するデバイス ("cpu" or "cuda"). Defaults to "cpu".
        language (str, optional): 文字起こしの言語 (例: "ja" for 日本語). Defaults to None.
        noise_reduction (bool): ノイズ削減を適用するかどうか. Defaults to False.

    Returns:
        Dict[str, Any]: Whisperの転写結果オブジェクト。以下のキーを含みます：
            - text: 完全な転写テキスト
            - segments: タイムスタンプ付きのセグメントリスト
            - language: 検出された言語

    Raises:
        FileNotFoundError: 音声ファイルが見つからない場合
        AudioTranscriptionError: モデルの読み込みまたは処理に失敗した場合
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_path}")

    try:
        # 必要に応じて音声の前処理を実行
        if noise_reduction:
            audio_path = preprocess_audio(str(audio_path), noise_reduction=True)
        
        # Whisperモデルの読み込み
        model = whisper.load_model(model_name, device=device)
        
        # 文字起こしオプションの設定
        transcribe_options: Dict[str, Any] = {}
        if language:
            transcribe_options["language"] = language
        
        # 実際の文字起こし
        result = model.transcribe(str(audio_path), **transcribe_options)
        return result
    except Exception as e:
        raise AudioTranscriptionError(f"文字起こし処理中にエラーが発生しました: {str(e)}")

def main() -> None:
    """
    コマンドライン引数を解析し、音声文字起こしを実行します。
    """
    parser = argparse.ArgumentParser(description="音声文字起こしツール")
    parser.add_argument("--audio", type=str, required=True, help="音声ファイルのパス")
    parser.add_argument("--model", type=str, default="large", help="Whisperモデル名")
    parser.add_argument("--device", type=str, default="cpu", help="使用するデバイス (cpu/cuda)")
    parser.add_argument("--language", type=str, help="文字起こしの言語 (例: ja)")
    parser.add_argument("--noise-reduction", action="store_true", help="ノイズ削減を適用する")
    
    args = parser.parse_args()
    
    try:
        transcription = transcribe_audio(
            args.audio,
            args.model,
            args.device,
            args.language,
            args.noise_reduction
        )
        print("文字起こし結果:", transcription)
    except (FileNotFoundError, AudioTranscriptionError) as e:
        print(f"エラーが発生しました: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # 日本語のコメント: メイン関数を呼び出してCLIからも動作可能にする
    main()