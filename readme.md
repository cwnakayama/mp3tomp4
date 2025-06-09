# mp3tomp4 Project

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![ffmpeg](https://img.shields.io/badge/ffmpeg-required-brightgreen)](https://ffmpeg.org/)

---

このプロジェクトは、音声ファイル（例: mp3, wav）と画像ファイルを組み合わせて、mp4動画ファイルを作成するためのものです。

## 導入方法

### 1. 必要なソフトウェアのインストール

- **Python 3.7以上** がインストールされていることを確認してください。
- **ffmpeg** がインストールされている必要があります。
    - Ubuntu/Debianの場合:
      ```sh
      sudo apt update
      sudo apt install ffmpeg
      ```
    - Macの場合（Homebrew使用）:
      ```sh
      brew install ffmpeg
      ```
    - Windowsの場合:
      1. [公式サイト](https://ffmpeg.org/download.html)からダウンロードし、パスを通してください。

### 2. プロジェクトのクローン・ダウンロード

```sh
git clone <このリポジトリのURL>
cd mp3tomp4
```

### 3. ディレクトリ構成の準備

以下のディレクトリが存在しない場合は作成してください。

```sh
mkdir -p audio/comitted pict mp4
```

### 4. 音声・画像ファイルの配置
- 変換したい音声ファイル（.mp3, .wavなど）を `audio/` フォルダに入れてください。
- mp4作成時に使う画像ファイル（.png, .jpgなど）を `pict/` フォルダに入れてください。

### 5. プログラムの実行

```sh
python main.py
```

- 変換が完了すると、mp4ファイルが `mp4/` フォルダに保存されます。
- 変換済みの音声ファイルは `audio/comitted/` に自動で移動されます。

### 6. トラブルシュート
- `ffmpeg: command not found` などのエラーが出る場合は、ffmpegが正しくインストールされているか、パスが通っているか確認してください。
- Pythonのバージョンや依存パッケージの問題がある場合は、`python --version` でバージョンを確認し、必要に応じて仮想環境の利用も検討してください。

---

## ディレクトリ構成と役割

- `audio/` : mp4変換前の音声ファイルを格納します。
    - `comitted/` : mp4ファイルに変換済みの元音声ファイルを移動します。
- `pict/` : mp4作成時に使用する画像ファイルを格納します。
- `mp4/` : 生成されたmp4ファイルを格納します。

## ワークフロー
1. `audio/` 配下に音声ファイル（例: .mp3, .wav）を配置します。
2. `pict/` 配下に画像ファイル（例: .png, .jpg）を配置します。
3. 音声ファイルと画像ファイルを組み合わせてmp4ファイルを生成し、`mp4/` フォルダに保存します。
4. mp4に変換した元の音声ファイルは `audio/comitted/` フォルダに移動します。

## 注意事項
- 画像ファイルはmp4作成時のサムネイルや背景として使用されます。
- 変換後のmp4ファイルは必ず `mp4/` フォルダに保存してください。
- 変換済みの音声ファイルは `audio/comitted/` に移動し、`audio/` からは削除してください。
