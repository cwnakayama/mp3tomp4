# mp3tomp4 Webアプリ（Flask+Docker）

## 起動方法

1. Dockerイメージをビルド

```sh
docker build -t mp3tomp4-webapp .
```

2. コンテナを起動

```sh
docker run --rm -p 5000:5000 mp3tomp4-webapp
```

3. ブラウザでアクセス

```
http://localhost:5000/
```

## 機能
- 音声ファイル（mp3等）と画像ファイル（jpg等）をアップロードし、mp4動画に変換
- 変換後のmp4をダウンロード可能 