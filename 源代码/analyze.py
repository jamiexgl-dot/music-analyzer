#!/usr/bin/env python3
"""
音乐分析工具 - 提取音频特征、识别风格
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

# 依赖检查
def check_dependencies():
    deps = {
        'ffmpeg': 'brew install ffmpeg',
        'librosa': 'pip install librosa',
        'numpy': 'pip install numpy',
        'soundfile': 'pip install soundfile'
    }
    
    missing = []
    for dep, install_cmd in deps.items():
        try:
            if dep == 'ffmpeg':
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            else:
                __import__(dep)
        except (ImportError, subprocess.CalledProcessError):
            missing.append(f"{dep}: {install_cmd}")
    
    return missing

def extract_audio(video_path, output_audio=None):
    """从视频提取音频"""
    if output_audio is None:
        output_audio = tempfile.mktemp(suffix='.wav')
    
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vn', '-acodec', 'pcm_s16le',
        '-ar', '22050', '-ac', '1',
        '-y', output_audio
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_audio

def analyze_audio(audio_path):
    """分析音频特征"""
    import librosa
    import numpy as np
    
    # 加载音频
    y, sr = librosa.load(audio_path, sr=None)
    
    # 基础特征
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # 频谱特征
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    
    # 节奏特征
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
    
    # 响度
    rms = librosa.feature.rms(y=y)[0]
    
    # 色度
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    
    # 梅尔频谱
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
    
    # 调性检测
    chroma_mean = np.mean(chroma, axis=1)
    key_idx = np.argmax(chroma_mean)
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key = keys[key_idx]
    
    # 判断大调/小调（简化版）
    major_third = chroma_mean[(key_idx + 4) % 12]
    minor_third = chroma_mean[(key_idx + 3) % 12]
    mode = 'major' if major_third > minor_third else 'minor'
    
    # 能量分布（低频/中频/高频）
    mel_db = librosa.power_to_db(mel_spec, ref=np.max)
    low_energy = np.mean(mel_db[:mel_spec.shape[0]//3])
    mid_energy = np.mean(mel_db[mel_spec.shape[0]//3:2*mel_spec.shape[0]//3])
    high_energy = np.mean(mel_db[2*mel_spec.shape[0]//3:])
    
    return {
        'duration': round(duration, 2),
        'tempo': round(float(tempo), 1),
        'key': f"{key} {mode}",
        'spectral': {
            'centroid_mean': round(float(np.mean(spectral_centroids)), 2),
            'centroid_std': round(float(np.std(spectral_centroids)), 2),
            'rolloff_mean': round(float(np.mean(spectral_rolloff)), 2),
            'bandwidth_mean': round(float(np.mean(spectral_bandwidth)), 2),
        },
        'dynamics': {
            'rms_mean': round(float(np.mean(rms)), 4),
            'rms_std': round(float(np.std(rms)), 4),
            'zcr_mean': round(float(np.mean(zero_crossing_rate)), 4),
        },
        'energy_distribution': {
            'low': round(float(low_energy), 2),
            'mid': round(float(mid_energy), 2),
            'high': round(float(high_energy), 2),
        },
        'brightness': 'bright' if np.mean(spectral_centroids) > 3000 else 'dark' if np.mean(spectral_centroids) < 1500 else 'balanced',
        'complexity': 'high' if np.std(spectral_centroids) > 500 else 'low'
    }

def infer_genre(features):
    """根据特征推断风格"""
    genres = []
    
    tempo = features['tempo']
    brightness = features['brightness']
    energy = features['energy_distribution']
    
    # 基于节奏
    if tempo > 140:
        genres.append('fast-paced')
    elif tempo < 90:
        genres.append('slow/atmospheric')
    else:
        genres.append('mid-tempo')
    
    # 基于亮度
    if brightness == 'bright':
        genres.append('electronic/pop-influenced')
    elif brightness == 'dark':
        genres.append('psychedelic/dark')
    
    # 基于能量分布
    if energy['high'] > energy['low']:
        genres.append('treble-heavy/shoegaze-like')
    elif energy['low'] > energy['mid']:
        genres.append('bass-heavy/dub-influenced')
    
    # 基于复杂度
    if features['complexity'] == 'high':
        genres.append('experimental/complex')
    
    return genres

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <video_or_audio_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        print("Missing dependencies:")
        for m in missing:
            print(f"  {m}")
        print("\nPlease install them first.")
        sys.exit(1)
    
    # 判断文件类型
    ext = Path(input_file).suffix.lower()
    is_video = ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    
    try:
        if is_video:
            print(f"Extracting audio from {input_file}...")
            audio_path = extract_audio(input_file)
        else:
            audio_path = input_file
        
        print("Analyzing audio features...")
        features = analyze_audio(audio_path)
        
        print("\n" + "="*50)
        print("MUSIC ANALYSIS RESULT")
        print("="*50)
        print(f"\n📊 Basic Info:")
        print(f"  Duration: {features['duration']}s")
        print(f"  Tempo: {features['tempo']} BPM")
        print(f"  Key: {features['key']}")
        
        print(f"\n🎵 Spectral Features:")
        print(f"  Brightness: {features['brightness']}")
        print(f"  Complexity: {features['complexity']}")
        print(f"  Centroid: {features['spectral']['centroid_mean']} Hz")
        
        print(f"\n🔊 Energy Distribution:")
        print(f"  Low: {features['energy_distribution']['low']} dB")
        print(f"  Mid: {features['energy_distribution']['mid']} dB")
        print(f"  High: {features['energy_distribution']['high']} dB")
        
        genres = infer_genre(features)
        print(f"\n🎸 Inferred Style:")
        for g in genres:
            print(f"  - {g}")
        
        # 保存详细结果
        output_file = Path(input_file).stem + '_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(features, f, indent=2)
        print(f"\n💾 Detailed results saved to: {output_file}")
        
    finally:
        if is_video and 'audio_path' in locals():
            os.unlink(audio_path)

if __name__ == '__main__':
    main()
