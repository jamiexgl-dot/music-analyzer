# Music Analyzer

音乐分析工具集 - 用于分析音频特征、识别风格、生成专辑封面。

## 功能

- **音频分析**: 提取节奏、调性、频谱特征
- **风格识别**: 推断音乐风格，推荐相似乐队
- **专辑封面生成**: AI 生成符合乐队风格的视觉作品

## 目录结构

```
├── src/                    # 源代码
│   ├── analyzer.py         # 基础分析
│   ├── analyzer_simple.py  # 简化版
│   ├── analyzer_m4a.py     # M4A 专用
│   └── analyzer_advanced.py # 高级分析（和弦、结构）
├── examples/               # 示例输出
│   └── monolith_band/      # 莫诺利斯乐队分析
├── generated_images/       # 生成的图片
│   └── album_covers/       # 专辑封面
├── tests/                  # 测试
└── requirements.txt        # 依赖

## 使用方法

### 音乐分析

```bash
cd src
python analyzer_m4a.py "音频文件.m4a"
```

### 生成专辑封面

```bash
python generate_image.py "描述文字"
```

## 示例

见 `examples/monolith_band/` 目录。

## 乐队信息

**莫诺利斯 (Monolith)**
- 主唱/吉他/合成器: 许光利
- 风格: 电子迷幻摇滚
