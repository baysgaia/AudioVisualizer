# プロジェクト名: AudioVisualizer

![Build Status](https://img.shields.io/github/actions/workflow/status/username/audio2midi/build-and-upload-video.yml)
![License](https://img.shields.io/badge/license-MIT-blue)

## 概要 (Overview)
本プロジェクトは、**ボーカル音源の解析**によるピッチ推定や歌詞抽出、MIDIファイル生成、さらに可視化用の連番画像と音声を組み合わせた**動画の自動生成**までを一貫して行うサンプルです。

- Whisper を利用した歌詞解析  
- Librosa / CREPE を利用したピッチ検出  
- MIDI 化 → Synthesizer V Studio Pro などでの再編集を想定  
- Node.js + FFmpeg で連番画像と音声を合成した動画を出力  
- GitHub Actions による短期開発向け自動ビルド（Artifacts で成果物を共有）

---

## デモ / スクリーンショット (Demo)
解析結果の一例として、下記のような **ピアノロール**と **字幕** を重ねた動画を自動生成します。

> **(ここに GIFアニメ or スクリーンショットを差し込む)**  
> ![demo_screenshot](docs/images/demo_screenshot.png)

また、解析したボーカルピッチを **MIDI ファイル (vocal.mid)** としてエクスポートし、Synthesizer V Studio や DAW ソフトに読み込むことも可能です。

---

## 目次 (Table of Contents)
1. [機能一覧 (Features)](#機能一覧-features)  
2. [インストール (Installation)](#インストール-installation)  
3. [使い方 (Usage)](#使い方-usage)  
4. [ディレクトリ構成 (Directory Structure)](#ディレクトリ構成-directory-structure)  
5. [Contributing](#contributing)  
6. [ライセンス (License)](#ライセンス-license)  
7. [連絡先 (Contact)](#連絡先-contact)  
8. [サードパーティライセンス (Third-Party Licenses)](#サードパーティライセンス-third-party-licenses)  

---

## 機能一覧 (Features)
- **ボーカル音源解析**  
  - [Demucs](https://github.com/facebookresearch/demucs) を利用してボーカル抽出 (混合音源から vocals.wav を分離)  
- **歌詞解析 (Whisper)**  
  - OpenAI Whisper で歌詞を文字起こしし、タイムスタンプ情報を取得  
- **ピッチ解析 & MIDI 生成**  
  - [Librosa](https://github.com/librosa/librosa) の pyin / [CREPE](https://github.com/marl/crepe) を利用して f0 推定  
  - Python で [mido](https://github.com/mido/mido) を使い、ノートオン/オフ情報と歌詞を MIDI のメタイベントに変換  
- **動画可視化**  
  - Node.js + [canvas](https://github.com/Automattic/node-canvas) で連番画像を生成（音程レーンや歌詞テロップの描画）  
  - [FFmpeg](https://ffmpeg.org/) を使って画像列と音声ファイルを合成し MP4 / WebM / GIF に書き出し  
- **CI/CD (GitHub Actions) 連携**  
  - Lint & 型チェック  
  - 動画自動生成 → Artifacts としてダウンロード  
- **Docker / AWS** (オプション)  
  - Dockerfile を用意し、AWS 等のサーバーにデプロイ可能

---

## インストール (Installation)

### 前提環境
- **Python 3.8+** (Whisper, Librosa, mido, CREPE などが動作可能なバージョン)  
- **Node.js 16+** (または 18+)  
- **FFmpeg** インストール済みであること（CLI コマンドが利用できる状態）

#### 1. ソースコード取得
```bash
git clone https://github.com/username/audio2midi.git
cd audio2midi
```

#### 2. Python パッケージのインストール
```bash
pip install -r requirements.txt
# whisper, demucs, librosa, crepe, mido, etc...
```

#### 3. Node.js パッケージのインストール
```bash
npm install
# fluent-ffmpeg, canvas, etc...
```

#### 4. Docker (任意)
Docker で動かす場合は、以下のような構成を用意しています（docker/ フォルダ参照）。

```bash
# イメージをビルド
docker build -t audio2midi:latest -f docker/Dockerfile .
# コンテナ起動（例：ポート3000）
docker run --rm -it -p 3000:3000 audio2midi:latest
```

---

## 使い方 (Usage)

1. **音源の準備**
   - 入力ファイル (例: original_mix.wav / vocals.wav / midi_input.mid) を input/ フォルダなどに配置
   - ボーカル抽出が必要なら Demucs を使う

   ```bash
   demucs input/original_mix.wav
   # vocals.wav, drums.wav, bass.wav, other.wav が生成
   ```

2. **Python スクリプトで解析 → MIDI 生成**
   1. 歌詞解析 (Whisper)

   ```bash
   python scripts/whisper_transcribe.py --input vocals.wav --lang ja
   # テキストやタイムスタンプが出力される
   ```

   2. ピッチ解析 & MIDI 化

   ```bash
   python scripts/generate_midi.py --input vocals.wav --output vocal.mid
   # f0 推定し、ノート情報 + 歌詞を MIDI メタイベントとして出力
   ```

3. **連番画像生成 (Node.js + canvas) [任意]**
   - 解析結果をもとに、ピアノロールや歌詞テロップを描画した連番 PNG 画像を作成

   ```bash
   npm run generate-frames
   # frames/frame_00000.png ~ frame_00xxx.png が作られる
   ```

4. **FFmpeg で動画合成**

   ```bash
   npm run build-video
   # scripts/build-video.js が実行され、FFmpegで output/video.mp4 を生成
   ```

5. **出力物の確認**
   - vocal.mid を DAW や Synthesizer V Studio にインポートしてピッチ・歌詞を確認
   - output/video.mp4 を任意のプレーヤーで再生して可視化を確認

---

## ディレクトリ構成 (Directory Structure)

```
audio2midi/
  ├─ .github/workflows/
  │    ├─ lint-and-typecheck.yml       # ESLint & TypeScriptチェック (Node.js部分)
  │    └─ build-and-upload-video.yml   # 動画ビルド & Artifactsアップロード
  ├─ docker/                           # Dockerfileや関連スクリプト
  ├─ frames/                           # 連番画像出力先 (gitignore推奨)
  ├─ output/                           # MIDIや動画ファイルの出力先 (gitignore推奨)
  ├─ scripts/
  │    ├─ whisper_transcribe.py       # Whisperで歌詞解析
  │    ├─ generate_midi.py            # ピッチ解析 & MIDI生成 (Librosa/CREPE + mido)
  │    ├─ build-video.js              # FFmpegで連番画像 + 音声を合成
  │    └─ ...
  ├─ src/                              # Node.jsやPythonのコアロジック (任意)
  ├─ package.json                      # Node.js依存管理
  ├─ requirements.txt                  # Python依存管理
  └─ README.md                         # ← このファイル
```

- 必要に応じて config ディレクトリで各種パラメータ(yaml/json)を管理すると便利です。

---

## Contributing

ご協力いただける場合は、以下のガイドラインに従って Pull Request を送ってください。

1. **Issue か Discussions でアイデア共有**
   - バグ報告や機能提案は Issue にて
   - 大きな機能追加案は Discussions へ

2. **ローカル開発環境の準備**
   - `npm install` / `pip install -r requirements.txt`
   - ESLint & TypeScript チェックが通ること、Python スクリプトが正常に動作することを確認

3. **PR 作成時**
   - 変更内容・動作確認方法を記載
   - テストやサンプルがあれば合わせてアップ

4. **Code of Conduct**
   - コミュニティ内での言動にはご配慮を。差別的・攻撃的な発言は禁止です。

---

## ライセンス (License)

このプロジェクトは MIT License のもとで公開しています。詳細は LICENSE ファイル をご確認ください。

---

## 連絡先 (Contact)

何か質問やバグ報告があれば、以下の方法でご連絡ください。

- Issue: GitHub Issues
- メール: developer@example.com

---

## サードパーティライセンス (Third-Party Licenses)

本プロジェクトでは以下の OSS を活用しています。一部主要ライセンスは MIT/Apache/ISC 等の寛容なライセンスです。

- Whisper (Apache License 2.0)
- Demucs (MIT)
- Librosa (ISC)
- CREPE (MIT)
- mido (MIT)
- fluent-ffmpeg (MIT)
- node-canvas (MIT)
- FFmpeg (LGPL or GPL ビルドオプションに依存)

ライブラリごとの詳細な著作権表示およびライセンス本文は、third_party_licenses/ フォルダなどに同梱しています。各ライブラリのライセンス要件を遵守し、著作権表示を削除しないでください。

---

以上の内容をもとに、音源解析から MIDI 化、動画生成までの一連フローを短期間・少人数で効率的に進められます。ぜひご活用ください！

---

## 使い方のポイント

1. **プロジェクト名やデモ GIF のパス**などは、実際のファイル構造に合わせて修正してください。  
2. **依存ライブラリのバージョンやライセンス表記**はプロジェクトで使用している実際のものを確認して追記してください。  
3. **Contributing ガイドライン**をチーム運用方針に合わせて詳細化すると、外部からのコントリビューションが円滑になります。  
4. **Docker / AWS** の利用ガイド、CI/CD のワークフロー設定例は各環境に合わせて具体的に追記してください。

本サンプルをベースに、より洗練された README.md を作成し、プロジェクトの理解・利用・貢献をスムーズに促進してください。
