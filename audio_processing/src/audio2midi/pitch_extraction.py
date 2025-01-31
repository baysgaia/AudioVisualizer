#!/usr/bin/env python
# -*- coding: utf-8 -*-
# /audio_processing/src/audio2midi/pitch_extraction.py
"""
音声ファイルからピッチ情報を抽出するモジュール
"""

import librosa
import numpy as np
from typing import Tuple

def extract_pitch_librosa(
    wav_path: str,
    sr_desired: int = 22050,
    fmin: str = 'C2',
    fmax: str = 'C6'
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Librosaのpyinを用いて音声ファイルの基本周波数(F0)を推定し、
    MIDIノートに変換した配列を返します。

    Parameters
    ----------
    wav_path : str
        対象の音声ファイルパス
    sr_desired : int
        希望するサンプリングレート
    fmin : str
        pYINの下限音程ノート (例: 'C2')
    fmax : str
        pYINの上限音程ノート (例: 'C6')

    Returns
    -------
    midi_notes : ndarray (float)
        フレームごとのMIDIノート番号 (NaN含む可能性あり)
    voiced_flag : ndarray(bool)
        フレームごとの有声音判定 (True/False)
    sr_used : int
        実際に使用されたサンプリングレート
    """
    # 音声ファイルの読み込み
    y, sr_used = librosa.load(wav_path, sr=sr_desired)
    
    # pYINによるピッチ推定
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz(fmin),
        fmax=librosa.note_to_hz(fmax),
        sr=sr_used
    )
    
    # 周波数(Hz) → MIDIノート変換
    midi_notes = librosa.hz_to_midi(f0)
    
    return midi_notes, voiced_flag, sr_used

# def extract_pitch_librosa(audio_path):
#     """
#     重複定義のためコメントアウト
#     """
#     pass

def extract_pitch_librosa(audio_path):
    """
    Librosaを使って音高を抽出する関数
    日本語コメントをそのまま残す
    """
    y, sr = librosa.load(audio_path)
    # 実際の処理を記述
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    # 必要に応じて更なる処理を実装
    return pitches  # 仮返り値の例