from flask import Flask, request, render_template_string, send_file, jsonify
import os
import tempfile
import subprocess
import threading
import re

def get_duration(audio_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        return float(result.stdout.strip())
    except Exception:
        return None

def run_ffmpeg_with_progress(audio_path, image_path, mp4_path, progress_data):
    duration = get_duration(audio_path)
    if not duration:
        progress_data['progress'] = 1.0
        progress_data['status'] = 'error'
        return
    cmd = [
        'ffmpeg', '-y', '-loop', '1', '-i', image_path, '-i', audio_path,
        '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', '-pix_fmt', 'yuv420p', mp4_path
    ]
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
    for line in process.stderr:
        match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
        if match:
            h, m, s = map(float, match.groups())
            current = h * 3600 + m * 60 + s
            progress = min(current / duration, 1.0)
            progress_data['progress'] = progress
    process.wait()
    progress_data['progress'] = 1.0
    progress_data['status'] = 'done'

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション用

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_AUDIO = {'.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg'}
ALLOWED_IMAGE = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}

progress_data = {'progress': 0.0, 'status': 'idle'}

HTML = '''
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>mp3tomp4 Web変換</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex flex-col items-center justify-center">
  <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 w-full max-w-md">
    <h1 class="text-2xl font-bold mb-6 text-center">音声＋画像→mp4変換</h1>
    <form id="convertForm" enctype=multipart/form-data class="space-y-6">
      <div class="mb-4">
        <label for="audioInput" class="cursor-pointer w-full block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded text-center transition">音声ファイルを選択</label>
        <input type="file" name="audio" id="audioInput" accept="audio/*" required class="hidden" />
        <span id="audioFileName" class="block mt-1 text-sm text-gray-600"></span>
        <audio id="audioPreview" controls class="mt-2 w-full hidden"></audio>
      </div>
      <div class="mb-4">
        <label for="imageInput" class="cursor-pointer w-full block bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded text-center transition">画像ファイルを選択</label>
        <input type="file" name="image" id="imageInput" accept="image/*" required class="hidden" />
        <div id="imageCard" class="relative mt-2 w-full max-w-xs mx-auto hidden">
          <img id="imagePreview" class="rounded-lg shadow-lg border object-contain w-full h-48 bg-gray-50 cursor-pointer" alt="選択した画像のプレビュー" />
          <button id="removeImageBtn" type="button" class="absolute top-2 right-2 bg-white bg-opacity-80 rounded-full p-1 shadow hover:bg-red-500 hover:text-white transition text-lg" aria-label="画像を削除">&times;</button>
          <div class="mt-2 text-center text-sm text-gray-700" id="imageInfo"></div>
        </div>
      </div>
      <div id="progressContainer" class="w-full bg-gray-200 rounded-full h-3 mb-2 hidden">
        <div id="progressBar" class="bg-blue-500 h-3 rounded-full transition-all duration-300" style="width:0%"></div>
      </div>
      <button type=submit class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">変換</button>
      <div id="loading" class="text-center text-blue-600 mt-2 hidden">
        <svg class="animate-spin h-5 w-5 inline-block mr-2 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg>
        変換中...お待ちください
      </div>
      <div id="errorMsg" class="text-red-500 mt-2 hidden"></div>
    </form>
    <div id="downloadSection" class="mt-4 text-center hidden">
      <button id="downloadBtn" class="w-full bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">変換後のmp4をダウンロード</button>
    </div>
  </div>
  <script>
    let mp4BlobUrl = null;
    let progressInterval = null;
    // 音声プレビューとファイル名
    document.getElementById('audioInput').addEventListener('change', function(e) {
      const file = e.target.files[0];
      const audio = document.getElementById('audioPreview');
      const nameSpan = document.getElementById('audioFileName');
      if (file) {
        audio.src = URL.createObjectURL(file);
        audio.classList.remove('hidden');
        audio.load();
        nameSpan.textContent = file.name;
      } else {
        audio.classList.add('hidden');
        audio.src = '';
        nameSpan.textContent = '';
      }
    });
    // 画像プレビュー・情報・削除
    const imageInput = document.getElementById('imageInput');
    const imageCard = document.getElementById('imageCard');
    const imagePreview = document.getElementById('imagePreview');
    const imageInfo = document.getElementById('imageInfo');
    const removeImageBtn = document.getElementById('removeImageBtn');
    imageInput.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        const url = URL.createObjectURL(file);
        imagePreview.src = url;
        imagePreview.alt = file.name;
        imageInfo.textContent = `${file.name}（${(file.size/1024).toFixed(1)} KB, ${file.type}）`;
        imageCard.classList.remove('hidden');
      } else {
        imageCard.classList.add('hidden');
        imagePreview.src = '';
        imageInfo.textContent = '';
      }
    });
    removeImageBtn.addEventListener('click', function() {
      imageInput.value = '';
      imageCard.classList.add('hidden');
      imagePreview.src = '';
      imageInfo.textContent = '';
    });
    // Ajaxで変換リクエスト
    document.getElementById('convertForm').addEventListener('submit', async function(e) {
      e.preventDefault();
      document.getElementById('loading').classList.remove('hidden');
      document.getElementById('errorMsg').classList.add('hidden');
      document.getElementById('downloadSection').classList.add('hidden');
      document.getElementById('progressContainer').classList.remove('hidden');
      document.getElementById('progressBar').style.width = '0%';
      if (mp4BlobUrl) {
        window.URL.revokeObjectURL(mp4BlobUrl);
        mp4BlobUrl = null;
      }
      // 進捗バー監視開始
      progressInterval = setInterval(async () => {
        const res = await fetch('/progress');
        const data = await res.json();
        document.getElementById('progressBar').style.width = (data.progress * 100) + '%';
        if (data.progress >= 1.0 || data.status === 'done' || data.status === 'error') {
          clearInterval(progressInterval);
          setTimeout(() => document.getElementById('progressContainer').classList.add('hidden'), 1000);
        }
      }, 1000);
      const formData = new FormData(this);
      try {
        const response = await fetch('/convert', { method: 'POST', body: formData });
        if (response.ok) {
          const blob = await response.blob();
          mp4BlobUrl = window.URL.createObjectURL(blob);
          document.getElementById('downloadSection').classList.remove('hidden');
        } else {
          const err = await response.json();
          document.getElementById('errorMsg').textContent = err.error || '変換に失敗しました';
          document.getElementById('errorMsg').classList.remove('hidden');
        }
      } catch (err) {
        document.getElementById('errorMsg').textContent = '通信エラーが発生しました';
        document.getElementById('errorMsg').classList.remove('hidden');
      }
      document.getElementById('loading').classList.add('hidden');
    });
    // DLボタンの動作
    document.getElementById('downloadBtn').addEventListener('click', function() {
      if (mp4BlobUrl) {
        const a = document.createElement('a');
        a.href = mp4BlobUrl;
        a.download = 'output.mp4';
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    });
  </script>
</body>
</html>
'''

def allowed_file(filename, allowed_exts):
    return '.' in filename and os.path.splitext(filename)[1].lower() in allowed_exts

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

@app.route('/convert', methods=['POST'])
def convert():
    audio = request.files.get('audio')
    image = request.files.get('image')
    if not (audio and allowed_file(audio.filename, ALLOWED_AUDIO)):
        return jsonify({'error': '音声ファイルの拡張子が不正です'}), 400
    if not (image and allowed_file(image.filename, ALLOWED_IMAGE)):
        return jsonify({'error': '画像ファイルの拡張子が不正です'}), 400
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, audio.filename)
        image_path = os.path.join(tmpdir, image.filename)
        mp4_path = os.path.join(tmpdir, 'output.mp4')
        audio.save(audio_path)
        image.save(image_path)
        # 進捗リセット
        progress_data['progress'] = 0.0
        progress_data['status'] = 'running'
        # ffmpegをスレッドで実行
        thread = threading.Thread(target=run_ffmpeg_with_progress, args=(audio_path, image_path, mp4_path, progress_data))
        thread.start()
        thread.join()  # 完了まで待つ
        if progress_data['status'] == 'error':
            return jsonify({'error': 'ffmpeg実行エラー'}), 500
        return send_file(mp4_path, as_attachment=True, download_name='output.mp4')

@app.route('/progress')
def progress():
    return jsonify(progress=progress_data['progress'], status=progress_data['status'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
    