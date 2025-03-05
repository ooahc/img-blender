# 法线贴图混合工具

一个用于混合多张法线贴图的图形界面工具。

## 功能特点

- 支持2-3张法线贴图的混合
- 可调节每张贴图的混合权重
- 实时预览混合效果
- 批量处理支持
- 简单直观的用户界面

## 安装要求

- Python 3.8+
- 依赖包：见 requirements.txt

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/normal-blender.git
cd normal-blender
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python normal_blender.py
```

2. 使用界面：
   - 点击"添加贴图"选择要混合的法线贴图
   - 调整每张贴图的混合权重（0-1之间）
   - 选择输出目录
   - 点击"开始混合"生成结果

## 注意事项

- 支持的图片格式：PNG、JPG
- 所有输入图片会被自动缩放至相同大小
- 建议使用标准的法线贴图格式
 
