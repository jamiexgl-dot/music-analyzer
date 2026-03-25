#!/usr/bin/env python3
"""
简化版音乐分析 - 直接下载 B站 音频分析
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

def download_bilibili_audio(url, output_dir="."):
    """下载 B站 视频音频"""
    try:
        import yt_dlp
    except ImportError:
        print("Installing yt-dlp...")
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
        import yt_dlp
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # 替换扩展名为 wav
        wav_file = filename.rsplit('.', 1)[0] + '.wav'
        return wav_file

def analyze_audio_simple(audio_path):
    """简化版音频分析"""
    import numpy as np
    
    try:
        import librosa
    except ImportError:
        print("Installing librosa...")
        subprocess.run([sys.executable, "-m", "pip", "install", "librosa", "-q"])
        import librosa
    
    # 加载音频（只加载前30秒，加快速度）
    y, sr = librosa.load(audio_path, sr=22050, duration=30)
    
    # 基础特征
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # 频谱特征
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    
    # 梅尔频谱用于能量分析
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # 能量分布
    low_energy = np.mean(mel_db[:40])
    mid_energy = np.mean(mel_db[40:80])
    high_energy = np.mean(mel_db[80:])
    
    # 色度分析调性
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    key_idx = np.argmax(chroma_mean)
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key = keys[key_idx]
    
    # 判断明暗
    centroid_mean = np.mean(spectral_centroids)
    if centroid_mean > 3000:
        brightness = "明亮/高频突出"
    elif centroid_mean < 1500:
        brightness = "暗沉/低频为主"
    else:
        brightness = "均衡"
    
    # 风格推断
    style_tags = []
    
    # 节奏
    if tempo > 130:
        style_tags.append("快节奏")
    elif tempo < 85:
        style_tags.append("慢速/氛围感")
    else:
        style_tags.append("中速")
    
    # 频谱特征
    if high_energy > mid_energy and high_energy > low_energy:
        style_tags.append("高频主导/迷幻感")
    if low_energy > mid_energy:
        style_tags.append("低频厚重/电子感")
    if centroid_mean > 2500:
        style_tags.append("明亮音色/流行感")
    if centroid_mean < 2000:
        style_tags.append("暗沉音色/实验感")
    
    return {
        'duration': round(duration, 2),
        'tempo': round(float(tempo), 1),
        'key': key,
        'brightness': brightness,
        'spectral_centroid': round(float(centroid_mean), 2),
        'energy': {
            'low': round(float(low_energy), 2),
            'mid': round(float(mid_energy), 2),
            'high': round(float(high_energy), 2),
        },
        'style_tags': style_tags
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_simple.py <bilibili_url_or_audio_file>")
        print("Example: python analyze_simple.py 'https://www.bilibili.com/video/BV13aAFzGETB'")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # 判断是 URL 还是本地文件
    if input_path.startswith('http'):
        print(f"Downloading from: {input_path}")
        try:
            audio_path = download_bilibili_audio(input_path)
            print(f"Downloaded: {audio_path}")
        except Exception as e:
            print(f"Download failed: {e}")
            print("Trying direct audio analysis...")
            sys.exit(1)
    else:
        audio_path = input_path
    
    print("Analyzing audio...")
    result = analyze_audio_simple(audio_path)
    
    print("\n" + "="*50)
    print("🎵 音乐分析结果")
    print("="*50)
    print(f"\n📊 基础信息:")
    print(f"  时长: {result['duration']}秒")
    print(f"  速度: {result['tempo']} BPM")
    print(f"  调性: {result['key']}")
    
    print(f"\n🎸 音色特征:")
    print(f"  亮度: {result['brightness']}")
    print(f"  频谱中心: {result['spectral_centroid']} Hz")
    
    print(f"\n🔊 能量分布:")
    print(f"  低频: {result['energy']['low']} dB")
    print(f"  中频: {result['energy']['mid']} dB")
    print(f"  高频: {result['energy']['high']} dB")
    
    print(f"\n🏷️ 风格标签:")
    for tag in result['style_tags']:
        print(f"  • {tag}")
    
    # 保存结果
    output_file = Path(audio_path).stem + '_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n💾 详细结果保存至: {output_file}")

if __name__ == '__main__':
    main()
