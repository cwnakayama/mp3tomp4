import os
import glob
import shutil
import subprocess
import random
from typing import List, Optional

# 定数
AUDIO_DIR = 'audio'
COMITTED_DIR = os.path.join(AUDIO_DIR, 'comitted')
PICT_DIR = 'pict'
MP4_DIR = 'mp4'
AUDIO_EXTS = ('.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg')
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')


def get_files_by_ext(directory: str, exts: tuple) -> List[str]:
    """指定ディレクトリから指定拡張子のファイル一覧を返す"""
    files = glob.glob(os.path.join(directory, '*'))
    return [f for f in files if os.path.isfile(f) and f.lower().endswith(exts)]


def get_audio_files() -> List[str]:
    """変換対象の音声ファイル一覧を取得（comitted除外）"""
    files = get_files_by_ext(AUDIO_DIR, AUDIO_EXTS)
    return [f for f in files if os.path.basename(f) != 'comitted']


def get_image_files() -> List[str]:
    """画像ファイル一覧を取得"""
    return get_files_by_ext(PICT_DIR, IMAGE_EXTS)


def select_image(image_files: List[str]) -> Optional[str]:
    """画像ファイルをランダムに1つ選択"""
    return random.choice(image_files) if image_files else None


def convert_to_mp4(audio_path: str, image_path: str, mp4_path: str) -> bool:
    """ffmpegで画像+音声からmp4を生成"""
    cmd = [
        'ffmpeg', '-y', '-loop', '1', '-i', image_path, '-i', audio_path,
        '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', '-pix_fmt', 'yuv420p', mp4_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f'[ERROR] 変換失敗: {audio_path} -> {e.stderr.decode()}')
        return False


def ensure_directories():
    """必要なディレクトリを作成"""
    os.makedirs(COMITTED_DIR, exist_ok=True)
    os.makedirs(MP4_DIR, exist_ok=True)


def process_all():
    """全音声ファイルをmp4に変換し、元音声をcomittedへ移動"""
    audio_files = get_audio_files()
    image_files = get_image_files()

    if not audio_files:
        print(f'[WARN] audio/ 直下に変換対象の音声ファイルが見つかりません。')
        return

    if not image_files:
        print('[ERROR] pict/ に画像ファイルがありません。処理を中断します。')
        return

    ensure_directories()

    for audio_path in audio_files:
        audio_name = os.path.splitext(os.path.basename(audio_path))[0]
        image_path = select_image(image_files)
        if not image_path:
            print(f'[WARN] 画像ファイルが見つかりません: {audio_path}')
            continue
        mp4_path = os.path.join(MP4_DIR, f'{audio_name}.mp4')
        print(f'[INFO] 変換中: {audio_path} + {image_path} -> {mp4_path}')
        if convert_to_mp4(audio_path, image_path, mp4_path):
            shutil.move(audio_path, os.path.join(COMITTED_DIR, os.path.basename(audio_path)))
            print(f'[INFO] 変換完了: {mp4_path}')


def main():
    """エントリーポイント"""
    process_all()


if __name__ == '__main__':
    main() 