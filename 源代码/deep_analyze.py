#!/usr/bin/env python3
"""
深度音乐分析 - 旋律、氛围、音色
"""

import sys
import json
import numpy as np
from pathlib import Path

def deep_analyze(audio_path, lyrics_path=None):
    """深度分析音乐"""
    import librosa
    
    print(f"深度分析: {audio_path}")
    
    # 加载音频
    y, sr = librosa.load(audio_path, sr=22050, duration=120)
    
    # 1. 旋律分析
    print("分析旋律...")
    
    # 提取音高
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    # 获取主音高序列
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            pitch_values.append(pitch)
    
    # 旋律走向分析
    if len(pitch_values) > 10:
        pitch_diff = np.diff(pitch_values)
        ascending = np.sum(pitch_diff > 0)
        descending = np.sum(pitch_diff < 0)
        stable = np.sum(np.abs(pitch_diff) < 10)
        
        total = len(pitch_diff)
        melody_trend = "上行为主" if ascending > descending else "下行为主" if descending > ascending else "平稳"
        
        # 音程跳跃度
        large_jumps = np.sum(np.abs(pitch_diff) > 200)
        jump_ratio = large_jumps / total if total > 0 else 0
        
        melody_description = {
            "走向": melody_trend,
            "上行比例": f"{ascending/total*100:.1f}%",
            "下行比例": f"{descending/total*100:.1f}%",
            "平稳比例": f"{stable/total*100:.1f}%",
            "大跳比例": f"{jump_ratio*100:.1f}%",
            "特征": "旋律跳跃丰富" if jump_ratio > 0.3 else "旋律平稳流畅"
        }
    else:
        melody_description = {"特征": "无法分析旋律"}
    
    # 2. 氛围情绪分析
    print("分析氛围...")
    
    # 频谱对比度（明亮度）
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    contrast_mean = np.mean(spectral_contrast)
    
    # 色度分析（调性色彩）
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_std = np.std(chroma, axis=1)
    tonal_stability = np.mean(chroma_std)
    
    # 零交叉率（明亮/粗糙感）
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_mean = np.mean(zcr)
    
    # 情绪推断
    if contrast_mean > 20 and zcr_mean > 0.1:
        atmosphere = "明亮、清晰、积极"
    elif contrast_mean < 15 and zcr_mean < 0.05:
        atmosphere = "暗沉、朦胧、神秘"
    else:
        atmosphere = "均衡、中性、温暖"
    
    if tonal_stability < 0.1:
        atmosphere += "，调性稳定"
    else:
        atmosphere += "，调性游离"
    
    # 3. 音色分析
    print("分析音色...")
    
    # 频谱质心（明亮度）
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    centroid_mean = np.mean(spectral_centroids)
    
    # 频谱 rolloff（能量集中）
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    rolloff_mean = np.mean(rolloff)
    
    # 音色描述
    if centroid_mean > 3000:
        brightness = "明亮、尖锐、数字感"
        instrument_type = "合成器高频/失真效果"
    elif centroid_mean > 2000:
        brightness = "清晰、现代、通透"
        instrument_type = "清音电吉他/合成器"
    elif centroid_mean > 1000:
        brightness = "温暖、饱满、模拟感"
        instrument_type = "原声乐器/低音合成器"
    else:
        brightness = "暗沉、厚重、模糊"
        instrument_type = "贝斯/鼓/低音"
    
    # 失真度估算（基于频谱平坦度）
    flatness = librosa.feature.spectral_flatness(y=y)[0]
    flatness_mean = np.mean(flatness)
    
    if flatness_mean > 0.3:
        distortion = "高失真/噪音成分多"
    elif flatness_mean > 0.15:
        distortion = "中等失真/混合音色"
    else:
        distortion = "低失真/纯净音色"
    
    # 4. 结构分析
    print("分析结构...")
    
    # 检测段落变化（基于 RMS 能量变化）
    rms = librosa.feature.rms(y=y)[0]
    rms_diff = np.diff(rms)
    
    # 找显著变化点
    threshold = np.std(rms_diff) * 2
    change_points = np.where(np.abs(rms_diff) > threshold)[0]
    
    # 估算段落数
    estimated_sections = len(change_points) // 2 + 1
    
    structure = {
        "估计段落数": estimated_sections,
        "变化点数量": len(change_points),
        "动态范围": "丰富多变" if len(change_points) > 10 else "相对平稳"
    }
    
    # 5. 整体描述
    overall_description = f"""
【旋律】{melody_description.get('特征', '未知')}
【氛围】{atmosphere}
【音色】{brightness}，{instrument_type}
【失真度】{distortion}
【结构】{structure['动态范围']}
""".strip()
    
    # 6. Suno Prompt 建议
    suno_prompt = f"""
[Style]
{brightness.split('、')[0]} electronic psychedelic rock, 
{melody_description.get('走向', '中速').replace('为主', '')} melody,
{atmosphere.split('，')[0]} atmosphere,
{distortion.replace('高失真', 'heavy distortion').replace('低失真', 'clean tone')},
{centroid_mean/1000:.0f}kHz spectral focus
""".strip()
    
    result = {
        "文件": Path(audio_path).name,
        "旋律分析": melody_description,
        "氛围情绪": {
            "描述": atmosphere,
            "频谱对比度": round(float(contrast_mean), 2),
            "调性稳定性": round(float(tonal_stability), 4)
        },
        "音色分析": {
            "亮度": brightness,
            "乐器类型": instrument_type,
            "失真度": distortion,
            "频谱中心": round(float(centroid_mean), 2),
            "平坦度": round(float(flatness_mean), 4)
        },
        "结构": structure,
        "整体描述": overall_description,
        "Suno建议": suno_prompt
    }
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python deep_analyze.py <音频文件> [歌词文件]")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    lyrics_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = deep_analyze(audio_path, lyrics_path)
        
        print("\n" + "="*60)
        print("🎵 深度音乐分析报告")
        print("="*60)
        print(f"\n{result['整体描述']}")
        print(f"\n🎸 Suno 生成建议:")
        print(result['Suno建议'])
        
        # 保存详细结果
        output_file = Path(audio_path).stem + '_deep_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 详细报告: {output_file}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
