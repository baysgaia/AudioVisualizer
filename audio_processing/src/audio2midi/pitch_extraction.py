# audio_processing/src/audio2midi/pitch_extraction.py

import librosa
import numpy as np
from typing import Tuple

def extract_pitch_librosa(wav_path: str,
                          sr_desired: int = 22050,
                          fmin: str = 'C2',
                          fmax: str = 'C6'
                          ) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Librosaのpyinを用いて音声ファイルの基本周波数(F0)を推定し、
    MIDIノートに変換した配列を返すサンプル関数。

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
    y, sr_used = librosa.load(wav_path, sr=sr_desired)
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz(fmin),
        fmax=librosa.note_to_hz(fmax),
        sr=sr_used
    )
    # 周波数(Hz) → MIDIノート
    midi_notes = 69 + 12 * np.log2(f0 / 440.0)  # A4=440Hz基準
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