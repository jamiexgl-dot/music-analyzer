# Music Analyzer - 音乐分析工具集

为**莫诺利斯乐队 (Monolith)** 打造的音乐分析与创作工具集。

## 乐队信息

| 项目 | 内容 |
|------|------|
| **乐队名** | 莫诺利斯 (Monolith) |
| **主唱/吉他/合成器/电子制作** | 许光利 |
| **风格** | 电子迷幻摇滚 |
| **代表作品** | Twin of Thought、旅程、梦林、Within the Frame 等 |

## 功能模块

### 1. 音乐分析 🔬
深度分析音频特征：
- **基础信息**: BPM、调性、时长
- **旋律分析**: 走向、跳跃度、稳定性
- **氛围情绪**: 明亮/暗沉、紧张/放松
- **音色特征**: 频谱分布、乐器类型、失真度
- **结构分析**: 段落变化、动态范围

### 2. AI 生成 🎨
- **专辑封面**: 阿里云百炼通义万相
- **音乐生成**: Suno 自动化（开发中）

### 3. 乐队资料库 📚
已分析 **9 首歌曲**：
1. Twin of Thought
2. 旅程
3. 梦林
4. Dog Friend Disease
5. 尼莫圈
6. Under Her Sleeve
7. 寒焰
8. Food
9. Within the Frame

## 目录结构

```
music-analyzer/
├── 源代码/                    # 分析工具源代码
│   ├── analyze.py            # 基础分析
│   ├── analyze_simple.py     # 简化版
│   ├── analyze_m4a.py        # M4A/MP3 专用
│   ├── analyze_advanced.py   # 高级分析（和弦、结构）
│   └── deep_analyze.py       # 深度分析（旋律、氛围、音色）
│
├── 示例/                      # 分析示例
│   └── 莫诺利斯乐队/          # 乐队完整分析
│       ├── 9首歌曲音频
│       ├── 深度分析报告.md
│       └── *_analysis.json   # 详细数据
│
├── 生成图片/                  # AI 生成图片
│   └── 专辑封面/              # 专辑封面作品
│
├── 歌曲/                      # 乐队歌曲库
│   └── 莫诺利斯乐队/          # 音频文件+歌词
│
├── 测试/                      # 测试文件
├── requirements.txt           # Python 依赖
└── README.md                  # 本文件
```

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 分析歌曲
```bash
cd 源代码
python deep_analyze.py "歌曲文件.mp3"
```

### 生成专辑封面
```bash
cd ../tools/image-generator
python generate_image.py "描述文字"
```

## 分析结果示例

### Twin of Thought
- **BPM**: 117.5 | **调性**: A大调
- **旋律**: 平稳流畅，下行为主
- **氛围**: 均衡、中性、温暖
- **音色**: 温暖饱满，原声乐器/低音合成器
- **失真**: 低失真，纯净音色

### 整体风格特征
- **速度**: 112-161 BPM（平均 128）
- **调性偏好**: D大调、F大调、A大调
- **核心音色**: 低音合成器 + 清音吉他
- **氛围关键词**: 温暖 | 均衡 | 神秘 | 迷幻

## Suno 生成建议

### 标准 Prompt
```
[Style]
Warm electronic psychedelic rock, 128 BPM,
ambient synth bass, clean guitar tones,
atmospheric textures, mysterious mood,
low distortion, analog warmth

[Verse]
（你的歌词）
```

### 快速版
```
Electronic psychedelic rock, warm analog synth,
clean guitar, atmospheric, 128 BPM, mysterious mood
```

## 参考乐队
- Portishead
- Sigur Rós
- Massive Attack
- Radiohead
- Tame Impala

## 技术栈
- **音频分析**: Librosa, NumPy
- **AI 生成**: 阿里云百炼 (通义万相)
- **自动化**: Selenium, PyAutoGUI
- **版本控制**: GitHub

## 更新日志

### 2025-03-25
- ✅ 搭建 GitHub 仓库
- ✅ 完成 9 首歌曲深度分析
- ✅ 集成阿里云百炼生图
- ✅ 开发 Suno 自动化脚本
- ✅ 建立乐队资料库

## 联系
- **GitHub**: https://github.com/jamiexgl-dot/music-analyzer
- **乐队**: 莫诺利斯 (Monolith)

---
*为音乐创作而生 🎵*
