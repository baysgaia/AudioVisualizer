#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
音声ファイルからピッチ情報を抽出するモジュール。

このモジュールは、音声ファイルから基本周波数（F0）を抽出し、
MIDIノート情報に変換する機能を提供します。
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional

import crepe
import librosa
import numpy as np
from scipy.ndimage import median_filter


@dataclass
class NoteEvent:
    """ノートイベントを表すデータクラス"""
    start_time: float  # 開始時間（秒）
    end_time: float    # 終了時間（秒）
    midi_note: float   # MIDIノート番号（連続値）
    velocity: int = 100  # ベロシティ（音の強さ）
    confidence: float = 1.0  # ピッチ推定の信頼度


def extract_pitch_crepe(
    wav_path: str,
    sr_desired: int = 16000,  # CREPEは16kHzを推奨
    confidence_threshold: float = 0.6,  # 信頼度の閾値
    model: str = 'full',  # CREPEモデルサイズ
    step_size: int = 5,  # 分析フレームのステップサイズ（ms）
    top_db: float = 35.0  # 無音判定の閾値
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """
    CREPEを用いて音声ファイルの基本周波数(F0)を推定し、
    MIDIノートに変換した配列を返します。

    Parameters
    ----------
    wav_path : str
        対象の音声ファイルパス
    sr_desired : int, optional
        希望するサンプリングレート（デフォルト: 16000 Hz）
    confidence_threshold : float, optional
        信頼度の閾値（デフォルト: 0.6）
    model : str, optional
        CREPEモデルサイズ ('tiny', 'small', 'medium', 'large', 'full')
    step_size : int, optional
        分析フレームのステップサイズ（ms）（デフォルト: 5）
    top_db : float, optional
        無音判定の閾値（デフォルト: 35.0 dB）

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray, int]
        - midi_notes: フレームごとのMIDIノート番号（NaN含む可能性あり）
        - confidence: フレームごとの信頼度スコア
        - time: 時間軸の配列（秒）
        - sr_used: 実際に使用されたサンプリングレート
    """
    print(f"\nCREPEピッチ抽出デバッグ情報:")
    print(f"入力ファイル: {wav_path}")
    print(f"パラメータ設定:")
    print(f"- サンプリングレート: {sr_desired}Hz")
    print(f"- モデルサイズ: {model}")
    print(f"- ステップサイズ: {step_size}ms")
    print(f"- 信頼度閾値: {confidence_threshold}")
    print(f"- 無音判定閾値: {top_db}dB")

    # 音声ファイルの読み込みと正規化
    audio_signal, sr_used = librosa.load(wav_path, sr=sr_desired)
    print(f"\n音声データ情報:")
    print(f"- 実際のサンプリングレート: {sr_used}Hz")
    print(f"- 音声長: {len(audio_signal) / sr_used:.2f}秒")
    
    # 正規化処理
    audio_signal = librosa.util.normalize(audio_signal)
    
    # 無音区間のトリミング
    audio_signal_trimmed, trim_indexes = librosa.effects.trim(audio_signal, top_db=top_db)
    trim_start = trim_indexes[0] / sr_used
    trim_end = trim_indexes[1] / sr_used
    print(f"\n無音トリミング:")
    print(f"- トリミング前の長さ: {len(audio_signal) / sr_used:.2f}秒")
    print(f"- トリミング後の長さ: {len(audio_signal_trimmed) / sr_used:.2f}秒")
    print(f"- トリミング範囲: {trim_start:.2f}秒 - {trim_end:.2f}秒")

    # CREPEによるピッチ推定
    time, frequency, confidence, _ = crepe.predict(
        audio_signal_trimmed,
        sr_used,
        model_capacity=model,
        step_size=step_size,
        viterbi=True,
        verbose=1
    )
    
    # 周波数(Hz) → MIDIノート変換
    midi_notes = librosa.hz_to_midi(frequency)
    
    # 信頼度が低い部分をNaNに
    midi_notes[confidence < confidence_threshold] = np.nan
    
    # ピッチ検出結果の統計
    valid_notes = ~np.isnan(midi_notes)
    if np.any(valid_notes):
        print(f"\nピッチ検出結果:")
        print(f"- 有効なピッチフレーム: {np.sum(valid_notes)} / {len(midi_notes)} ({100 * np.sum(valid_notes) / len(midi_notes):.1f}%)")
        print(f"- 検出された音域: {np.min(midi_notes[valid_notes]):.1f} - {np.max(midi_notes[valid_notes]):.1f} (MIDI note)")
        print(f"- 平均信頼度: {np.mean(confidence):.3f}")
    else:
        print("\n警告: 有効なピッチが検出されませんでした")
    
    return midi_notes, confidence, time, sr_used


def cluster_notes_with_confidence(
    time_axis: np.ndarray,
    midi_values: np.ndarray,
    confidence_values: np.ndarray,
    cent_tolerance: float = 40.0,  # より厳密な半音の幅
    min_note_length: float = 0.1,  # 最小ノート長
    smooth_window: int = 5,  # 平滑化窓幅
    confidence_threshold: float = 0.6,  # 信頼度閾値
    vibrato_window: float = 0.2,  # ビブラート検出の時間窓
    vibrato_tolerance: float = 200.0  # ビブラート検出の音程差閾値
) -> List[NoteEvent]:
    """
    CREPEの信頼度を考慮してノートイベントを生成します。

    Parameters
    ----------
    time_axis : np.ndarray
        時間軸の配列（秒）
    midi_values : np.ndarray
        MIDIノート値の配列
    confidence_values : np.ndarray
        信頼度値の配列
    cent_tolerance : float, optional
        同一ノートとみなすセント差の閾値（デフォルト: 40セント = 半音の半分）
    min_note_length : float, optional
        最小ノート長（秒）（デフォルト: 0.1秒）
    smooth_window : int, optional
        平滑化の窓幅（デフォルト: 5フレーム）
    confidence_threshold : float, optional
        信頼度の閾値（デフォルト: 0.6）
    vibrato_window : float, optional
        ビブラート検出の時間窓（秒）（デフォルト: 0.2秒）
    vibrato_tolerance : float, optional
        ビブラート検出の音程差閾値（セント）（デフォルト: 200セント）

    Returns
    -------
    List[NoteEvent]
        抽出されたノートイベントのリスト
    """
    # デバッグ情報の出力
    print(f"Input shape: {midi_values.shape}")
    print(f"Valid notes: {np.sum(~np.isnan(midi_values))}/{len(midi_values)}")
    
    # ピッチの平滑化前にNaNを補間
    valid_indices = ~np.isnan(midi_values)
    if np.any(valid_indices):
        midi_values_filled = np.interp(
            np.arange(len(midi_values)),
            np.arange(len(midi_values))[valid_indices],
            midi_values[valid_indices]
        )
    else:
        print("Warning: No valid pitch values found")
        return []

    # メディアンフィルタによる平滑化
    midi_smooth = median_filter(midi_values_filled, size=smooth_window)
    
    # 初期ノートイベントの生成
    note_events: List[NoteEvent] = []
    current_note: Optional[float] = None
    note_start_time: Optional[float] = None
    current_confidence_sum = 0.0
    current_frame_count = 0
    
    for t, note_val, conf in zip(time_axis, midi_smooth, confidence_values):
        if conf < confidence_threshold or np.isnan(note_val):
            if current_note is not None:
                duration = t - note_start_time
                if duration >= min_note_length:
                    avg_confidence = current_confidence_sum / current_frame_count
                    note_events.append(
                        NoteEvent(
                            start_time=note_start_time,
                            end_time=t,
                            midi_note=current_note,
                            confidence=avg_confidence
                        )
                    )
                current_note = None
                current_confidence_sum = 0.0
                current_frame_count = 0
            continue
        
        if current_note is None:
            current_note = note_val
            note_start_time = t
            current_confidence_sum = conf
            current_frame_count = 1
        else:
            cent_diff = 100 * (note_val - current_note)
            if abs(cent_diff) > cent_tolerance:
                duration = t - note_start_time
                if duration >= min_note_length:
                    avg_confidence = current_confidence_sum / current_frame_count
                    note_events.append(
                        NoteEvent(
                            start_time=note_start_time,
                            end_time=t,
                            midi_note=current_note,
                            confidence=avg_confidence
                        )
                    )
                current_note = note_val
                note_start_time = t
                current_confidence_sum = conf
                current_frame_count = 1
            else:
                # 重み付き平均でノートを更新
                current_note = (current_note * current_frame_count + note_val) / (current_frame_count + 1)
                current_confidence_sum += conf
                current_frame_count += 1

    # 最後のノートの処理
    if current_note is not None:
        duration = time_axis[-1] - note_start_time
        if duration >= min_note_length:
            avg_confidence = current_confidence_sum / current_frame_count
            note_events.append(
                NoteEvent(
                    start_time=note_start_time,
                    end_time=time_axis[-1],
                    midi_note=current_note,
                    confidence=avg_confidence
                )
            )

    # ノートイベントをタプルのリストに変換
    note_tuples = [(n.start_time, n.end_time, n.midi_note) for n in note_events]

    # 短いノートのマージと削除
    from .note_utils import merge_short_notes, smooth_vibrato
    merged_notes = merge_short_notes(note_tuples, min_note_length, cent_tolerance)
    
    # ビブラートの平滑化
    smoothed_notes = smooth_vibrato(merged_notes, vibrato_window, vibrato_tolerance)
    
    # 最終的なノートイベントの生成
    final_note_events = []
    for start, end, note in smoothed_notes:
        final_note_events.append(
            NoteEvent(
                start_time=start,
                end_time=end,
                midi_note=note,
                confidence=1.0  # マージ後は信頼度を1.0とする
            )
        )

    # デバッグ情報の出力
    print(f"Generated {len(final_note_events)} note events")
    if final_note_events:
        print(f"Average confidence: {np.mean([n.confidence for n in final_note_events]):.3f}")
    
    return final_note_events


def extract_melody(
    wav_path: str,
    sr_desired: int = 22050,
    fmin: str = 'C2',
    fmax: str = 'C6',
    cent_tolerance: float = 50.0,
    min_note_length: float = 0.05,
    smooth_window: int = 3
) -> Tuple[List[NoteEvent], np.ndarray, np.ndarray, float]:
    """
    音声ファイルからメロディを抽出し、ノートイベントとして返します。

    Parameters
    ----------
    wav_path : str
        対象の音声ファイルパス
    sr_desired : int, optional
        希望するサンプリングレート（デフォルト: 22050 Hz）
    fmin : str, optional
        最低音のノート名（デフォルト: 'C2'）
    fmax : str, optional
        最高音のノート名（デフォルト: 'C6'）
    cent_tolerance : float, optional
        同一ノートとみなすセント差の閾値（デフォルト: 50セント）
    min_note_length : float, optional
        最小ノート長（秒）（デフォルト: 0.05秒）
    smooth_window : int, optional
        平滑化の窓幅（デフォルト: 3フレーム）

    Returns
    -------
    Tuple[List[NoteEvent], np.ndarray, np.ndarray, float]
        - ノートイベントのリスト
        - 時間軸の配列
        - 元のMIDIノート値の配列
        - サンプリングレート
    """
    # ピッチ抽出
    midi_notes, confidence, time, sr = extract_pitch_crepe(
        wav_path, sr_desired
    )
    
    # ノートイベントの抽出
    note_events = cluster_notes_with_confidence(
        time,
        midi_notes,
        confidence,
        cent_tolerance,
        min_note_length,
        smooth_window
    )
    
    return note_events, time, midi_notes, sr