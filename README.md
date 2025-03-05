# Normal Map Blender

一个用于混合多个法线贴图的工具，支持多种混合模式和权重控制。

## 功能特点

- 支持多任务管理
- 每个任务可包含多个法线贴图
- 支持多种混合模式（Normal、Multiply、Add、Overlay）
- 实时预览混合效果
- 支持通过配置文件批量创建任务

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 图形界面操作

1. 创建任务
   - 点击"添加任务"按钮创建新任务
   - 双击任务名称或按F2可重命名任务

2. 添加法线贴图
   - 选择任务后点击"添加子项"
   - 选择要混合的法线贴图文件

3. 调整参数
   - 在参数表格中设置每个贴图的权重（0-1）
   - 选择混合模式
   - 可启用/禁用单个贴图

4. 导出结果
   - 选择输出目录
   - 点击"导出全部混合图"
   - 混合结果将以任务名称命名

### 配置文件

支持通过 JSON 配置文件批量创建任务，配置文件格式如下：

```json
{
  "tasks": [
    {
      "name": "金属材质混合",
      "enabled": true,
      "items": [
        {
          "name": "base_normal.png",
          "path": "textures/base_normal.png",
          "weight": 1.0,
          "blend_mode": "Normal",
          "enabled": true
        },
        {
          "name": "detail_normal.png",
          "path": "textures/detail_normal.png",
          "weight": 0.5,
          "blend_mode": "Overlay",
          "enabled": true
        }
      ]
    },
    {
      "name": "布料材质混合",
      "enabled": true,
      "items": [
        {
          "name": "fabric_base.png",
          "path": "textures/fabric_base.png",
          "weight": 1.0,
          "blend_mode": "Normal",
          "enabled": true
        }
      ]
    }
  ]
}
```

#### 配置项说明

任务配置：
- `name`: 任务名称，将用作输出文件名
- `enabled`: 是否启用该任务
- `items`: 法线贴图项目列表

贴图项配置：
- `name`: 显示名称（通常为文件名）
- `path`: 贴图文件路径（支持相对路径和绝对路径）
- `weight`: 混合权重（0-1）
- `blend_mode`: 混合模式，支持：
  - `"Normal"`: 普通混合
  - `"Multiply"`: 正片叠底
  - `"Add"`: 叠加
  - `"Overlay"`: 覆盖
- `enabled`: 是否启用该贴图

#### 路径说明

- 配置文件中的贴图路径可以使用相对路径或绝对路径
- 相对路径将相对于配置文件所在目录解析
- 导出配置时会尽可能使用相对路径以提高可移植性

#### 使用配置文件

1. 导入配置
   - 从"文件"菜单选择"导入任务配置"
   - 选择JSON配置文件
   - 程序将根据配置创建所有任务

2. 导出配置
   - 从"文件"菜单选择"导出任务配置"
   - 选择保存位置
   - 当前所有任务将被保存为JSON配置文件

## 注意事项

- 建议使用相同分辨率的法线贴图
- 如果分辨率不同，将自动缩放至第一张贴图的分辨率
- 任务名称将用作输出文件名，请避免使用非法字符
- 建议使用相对路径以提高配置文件的可移植性

## 开发环境

- Python 3.x
- PyQt6
- OpenCV
- NumPy
 
