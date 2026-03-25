#!/usr/bin/env python3
"""
直接分析 m4a 文件（无需 ffmpeg）
"""

import sys
import json
from pathlib import Path

def analyze_m4a(audio_path):
    """分析 m4a 音频"""
    import numpy as np
    
    try:
        import librosa
    except ImportError:
        print("Installing librosa...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "librosa", "-q"])
        import librosa
    
    print(f"Loading: {audio_path}")
    # 加载音频（只加载前60秒）
    y, sr = librosa.load(audio_path, sr=22050, duration=60, mono=True)
    
    print("Analyzing...")
    
    # 基础特征
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # 频谱特征
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    
    # 梅尔频谱
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    mel_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # 能量分布（低中高频）
    low_energy = np.mean(mel_db[:42])
    mid_energy = np.mean(mel_db[42:85])
    high_energy = np.mean(mel_db[85:])
    
    # 色度分析
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    key_idx = np.argmax(chroma_mean)
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key = keys[key_idx]
    
    # 判断大调小调
    major_third = chroma_mean[(key_idx + 4) % 12]
    minor_third = chroma_mean[(key_idx + 3) % 12]
    mode = '大调' if major_third > minor_third else '小调'
    
    # 亮度判断
    centroid_mean = np.mean(spectral_centroids)
    if centroid_mean > 3000:
        brightness = "明亮/高频突出"
    elif centroid_mean < 1500:
        brightness = "暗沉/低频为主"
    else:
        brightness = "均衡"
    
    # 动态范围
    rms = librosa.feature.rms(y=y)[0]
    dynamics = np.std(rms)
    
    # 风格推断
    style_tags = []
    similar_bands = []
    
    # 节奏分析
    if tempo > 140:
        style_tags.append("快节奏/激进")
    elif tempo > 120:
        style_tags.append("中快板")
    elif tempo < 85:
        style_tags.append("慢速/氛围感")
        similar_bands.extend(["Slowdive", "Cocteau Twins"])
    else:
        style_tags.append("中速")
    
    # 频谱特征分析
    if high_energy > mid_energy and high_energy > low_energy:
        style_tags.append("高频主导/迷幻感")
        similar_bands.extend(["My Bloody Valentine", "Ride"])
    
    if low_energy > mid_energy and low_energy > high_energy:
        style_tags.append("低频厚重/电子感")
        similar_bands.extend(["Massive Attack", "Portishead"])
    
    if centroid_mean > 2800:
        style_tags.append("明亮音色/梦幻感")
        similar_bands.extend(["M83", "Tame Impala"])
    
    if centroid_mean < 2000:
        style_tags.append("暗沉音色/实验感")
        similar_bands.extend(["Radiohead", "Sigur Rós"])
    
    # 动态分析
    if dynamics > 0.05:
        style_tags.append("动态丰富/情绪化")
    else:
        style_tags.append("平稳/氛围化")
    
    # 综合判断
    if "迷幻感" in str(style_tags) and "电子感" in str(style_tags):
        similar_bands.extend(["The Horrors", "Unknown Mortal Orchestra"])
    
    if "氛围感" in str(style_tags) and "梦幻感" in str(style_tags):
        similar_bands.extend(["Beach House", "M83"])
    
    return {
        'duration': round(duration, 2),
        'tempo': round(float(tempo), 1),
        'key': f"{key} {mode}",
        'brightness': brightness,
        'spectral_centroid': round(float(centroid_mean), 2),
        'dynamics': round(float(dynamics), 4),
        'energy': {
            'low': round(float(low_energy), 2),
            'mid': round(float(mid_energy), 2),
            'high': round(float(high_energy), 2),
        },
        'style_tags': style_tags,
        'similar_bands': list(set(similar_bands))  # 去重
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_m4a.py <audio_file>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    try:
        result = analyze_m4a(audio_path)
        
        print("\n" + "="*60)
        print("🎵 莫诺利斯乐队 - 音乐分析报告")
        print("="*60)
        print(f"\n📊 基础信息:")
        print(f"  分析时长: {result['duration']}秒")
        print(f"  BPM: {result['tempo']}")
        print(f"  调性: {result['key']}")
        
        print(f"\n🎸 音色特征:")
        print(f"  整体亮度: {result['brightness']}")
        print(f"  频谱中心: {result['spectral_centroid']} Hz")
        print(f"  动态范围: {result['dynamics']}")
        
        print(f"\n🔊 频谱能量分布:")
        print(f"  低频 (0-250Hz): {result['energy']['low']} dB")
        print(f"  中频 (250-2kHz): {result['energy']['mid']} dB")
        print(f"  高频 (2kHz+): {result['energy']['high']} dB")
        
        print(f"\n🏷️ 风格标签:")
        for tag in result['style_tags']:
            print(f"  • {tag}")
        
        print(f"\n🎧 相似风格乐队推荐:")
        for band in result['similar_bands']:
            print(f"  • {band}")
        
        # 保存结果
        output_file = Path(audio_path).stem + '_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 详细数据: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
