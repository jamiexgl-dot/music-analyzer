#!/usr/bin/env python3
"""
高级音乐分析 - 和弦、结构、情绪
"""

import sys
import json
import numpy as np
from pathlib import Path

def analyze_advanced(audio_path):
    import librosa
    
    print("Loading audio...")
    y, sr = librosa.load(audio_path, sr=22050, duration=120, mono=True)
    
    print("Analyzing...")
    
    # 1. 和弦检测
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # 简化和弦识别（每2秒一个和弦）
    hop_length = 512
    frames_per_sec = sr / hop_length
    chord_interval = int(2 * frames_per_sec)  # 2秒
    
    chords = []
    chord_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    for i in range(0, chroma.shape[1], chord_interval):
        segment = chroma[:, i:i+chord_interval]
        chroma_mean = np.mean(segment, axis=1)
        root = np.argmax(chroma_mean)
        
        # 简单判断大三/小三
        third_major = chroma_mean[(root + 4) % 12]
        third_minor = chroma_mean[(root + 3) % 12]
        quality = '' if third_major > third_minor else 'm'
        
        time = i / frames_per_sec
        chords.append({
            'time': round(time, 1),
            'chord': f"{chord_names[root]}{quality}"
        })
    
    # 2. 段落分割（基于频谱变化）
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # 计算 MFCC 变化率
    mfcc_delta = np.diff(mfcc, axis=1)
    change_points = []
    
    # 找变化大的点
    threshold = np.mean(np.abs(mfcc_delta)) * 2
    for i in range(mfcc_delta.shape[1]):
        if np.mean(np.abs(mfcc_delta[:, i])) > threshold:
            time = i / frames_per_sec
            if not change_points or time - change_points[-1] > 5:  # 至少间隔5秒
                change_points.append(time)
    
    # 3. 情绪分析（基于音频特征）
    
    # 提取特征
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    rms = librosa.feature.rms(y=y)[0]
    
    # 情绪推断规则
    emotions = []
    
    # 基于速度
    if tempo > 130:
        emotions.append(('energetic', 0.8))
    elif tempo < 90:
        emotions.append(('melancholic', 0.7))
    else:
        emotions.append(('calm', 0.6))
    
    # 基于亮度
    centroid_mean = np.mean(spectral_centroids)
    if centroid_mean < 1500:
        emotions.append(('dark', 0.8))
    elif centroid_mean > 3000:
        emotions.append(('bright', 0.7))
    
    # 基于动态
    rms_mean = np.mean(rms)
    rms_std = np.std(rms)
    if rms_std > 0.05:
        emotions.append(('dynamic', 0.9))
    if rms_mean < 0.1:
        emotions.append(('intimate', 0.6))
    
    # 4. 乐器/音色推测
    timbre_tags = []
    
    # 零交叉率（判断是否有大量高频/噪音）
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_mean = np.mean(zcr)
    
    # 频谱对比度
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    contrast_mean = np.mean(contrast)
    
    if zcr_mean > 0.1:
        timbre_tags.append('distorted guitars' if contrast_mean > 20 else 'clean guitars')
    
    if centroid_mean > 2000 and np.std(spectral_centroids) > 500:
        timbre_tags.append('synthesizers')
    
    if np.mean(rms) > 0.15 and tempo > 120:
        timbre_tags.append('driving drums')
    
    # 5. 生成描述
    description = generate_description(tempo, centroid_mean, emotions, timbre_tags)
    
    return {
        'chords': chords[:10],  # 前10个和弦
        'structure': {
            'change_points': [round(t, 1) for t in change_points[:5]],
            'estimated_sections': len(change_points) + 1
        },
        'emotions': emotions,
        'timbre': timbre_tags,
        'description': description
    }

def generate_description(tempo, centroid, emotions, timbre):
    """生成文字描述"""
    parts = []
    
    # 速度描述
    if tempo > 140:
        parts.append("快节奏")
    elif tempo > 110:
        parts.append("中快节奏")
    elif tempo < 80:
        parts.append("慢速氛围")
    else:
        parts.append("中速")
    
    # 情绪描述
    emotion_words = [e[0] for e in emotions[:2]]
    if 'dark' in emotion_words:
        parts.append("暗沉")
    if 'energetic' in emotion_words:
        parts.append("充满能量")
    if 'melancholic' in emotion_words:
        parts.append("忧郁")
    
    # 乐器描述
    if 'synthesizers' in timbre:
        parts.append("电子合成器主导")
    if 'distorted guitars' in timbre:
        parts.append("失真吉他")
    
    return "、".join(parts) + "的风格"

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_advanced.py <audio_file>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    try:
        result = analyze_advanced(audio_path)
        
        print("\n" + "="*60)
        print("🎵 高级音乐分析")
        print("="*60)
        
        print(f"\n🎼 和弦进行（前20秒）:")
        for c in result['chords'][:5]:
            print(f"  {c['time']}s: {c['chord']}")
        
        print(f"\n📐 结构分析:")
        print(f"  估计段落数: {result['structure']['estimated_sections']}")
        print(f"  变化点: {result['structure']['change_points']}s")
        
        print(f"\n🎭 情绪色彩:")
        for emotion, conf in result['emotions']:
            bar = "█" * int(conf * 10)
            print(f"  {emotion}: {bar} {conf:.0%}")
        
        print(f"\n🎸 音色推测:")
        for t in result['timbre']:
            print(f"  • {t}")
        
        print(f"\n📝 一句话描述:")
        print(f"  {result['description']}")
        
        # 保存
        output = Path(audio_path).stem + '_advanced.json'
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 {output}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
