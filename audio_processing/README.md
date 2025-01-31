# Audio2MIDI 音声処理パイプライン

このプロジェクトは、音声ファイルから歌詞とメロディーを抽出し、MIDIファイルを生成するPythonパイプラインを提供します。

## 主な機能

1. 音声文字起こし（Whisperを使用）
   - ノイズ削減オプション
   - 複数言語対応
   - タイムスタンプ付きセグメント出力

2. ピッチ抽出（librosaを使用）
   - 音高範囲の指定
   - 最小ノート長の設定
   - ボイス/無音区間の検出

3. 歌詞とピッチのマッチング
   - タイムスタンプベースの同期
   - 精密な音符分割

4. 複数の出力形式
   - MIDI（歌詞付き）
   - JSON
   - CSV

## インストール

```bash
# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Unix系
# または
.\venv\Scripts\activate  # Windows

# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使用方法

### コマンドライン

基本的な使用方法:
```bash
python src/main.py audio_file.wav
```

詳細なオプション指定:
```bash
python src/main.py audio_file.wav \
    --model-name large \
    --device cuda \
    --language ja \
    --noise-reduction \
    --min-pitch C2 \
    --max-pitch C6 \
    --min-duration 0.1 \
    --output-format midi \
    --output-path output.mid \
    --tempo 120 \
    --velocity 100
```

### オプション説明

#### Whisper関連
- `--model-name`: Whisperモデル名（tiny/base/small/medium/large）
- `--device`: 使用するデバイス（cpu/cuda）
- `--language`: 文字起こしの言語（例: ja）
- `--noise-reduction`: ノイズ削減を適用

#### ピッチ抽出
- `--min-pitch`: 最低音高（例: C2）
- `--max-pitch`: 最高音高（例: C6）
- `--min-duration`: 最小ノート長（秒）

#### 出力設定
- `--output-format`: 出力形式（midi/json/csv）
- `--output-path`: 出力ファイルパス
- `--tempo`: MIDIテンポ（BPM）
- `--velocity`: MIDIベロシティ（0-127）

## 出力形式

### MIDI
- メロディートラック（音符情報）
- 歌詞トラック（テキスト情報）
- テンポ情報

### JSON
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "歌詞",
      "notes": [
        {"pitch": 60, "start": 0.0, "end": 1.2},
        {"pitch": 62, "start": 1.2, "end": 2.5}
      ]
    }
  ]
}
```

### CSV
```csv
start,end,pitch,text
0.0,1.2,60,歌
1.2,2.5,62,詞
```

## 注意事項

- GPUを使用する場合は、CUDAがインストールされていることを確認してください
- 大きな音声ファイルの処理には時間がかかる場合があります
- 最適な結果を得るために、クリアな音声録音を使用することを推奨します

## ライセンス

MITライセンス