#!/bin/bash
# mp3tomp4-webapp用 Dockerビルド＆起動スクリプト

docker build -t mp3tomp4-webapp .
docker run --rm -p 5000:5000 mp3tomp4-webapp 