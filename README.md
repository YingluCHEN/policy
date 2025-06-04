# 徐汇区人才政策爬虫

## 项目简介
专门爬取上海市徐汇区人才相关政策，重点提取企业申报要求的智能爬虫工具。

## 主要功能
- 🎯 智能识别人才政策（人才引进、创业扶持、AI政策等）
- 💼 精准提取企业申报要求
- 📊 自动分类和数据分析
- 📁 多格式数据导出（JSON、CSV、Excel）

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行爬虫
```bash
python main.py
```

### 3. 查看结果
- 详细数据：`data/talent_policies.json`
- 申报要求：`data/application_requirements.txt`
- 分析报告：`data/analysis_report.txt`

## 文件结构
```
├── main.py              # 主程序
├── crawler.py           # 爬虫核心
├── analyzer.py          # 数据分析
├── config.py            # 配置文件
├── data/                # 数据输出目录
└── logs/                # 日志目录
```

## 注意事项
- 请遵守robots.txt协议
- 建议设置合理的爬取间隔
- 数据仅供研究和学习使用 