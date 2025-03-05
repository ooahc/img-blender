import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                            QSpinBox, QDoubleSpinBox, QListWidget, QMessageBox)
from PyQt6.QtCore import Qt
import cv2
import numpy as np
from PIL import Image

class NormalMapBlender(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("法线贴图混合工具")
        self.setMinimumSize(800, 600)
        
        # 数据存储
        self.normal_maps = []  # 存储法线贴图路径和权重
        self.output_dir = ""
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # 左侧面板 - 贴图列表和控制
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 贴图列表
        self.map_list = QListWidget()
        left_layout.addWidget(QLabel("法线贴图列表："))
        left_layout.addWidget(self.map_list)
        
        # 控制按钮
        btn_add = QPushButton("添加贴图")
        btn_add.clicked.connect(self.add_normal_map)
        btn_remove = QPushButton("移除贴图")
        btn_remove.clicked.connect(self.remove_normal_map)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        left_layout.addLayout(btn_layout)
        
        # 权重调节
        weight_widget = QWidget()
        weight_layout = QHBoxLayout(weight_widget)
        weight_layout.addWidget(QLabel("权重："))
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 1)
        self.weight_spin.setSingleStep(0.1)
        self.weight_spin.setValue(1.0)
        weight_layout.addWidget(self.weight_spin)
        left_layout.addWidget(weight_widget)
        
        # 输出控制
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        
        btn_output = QPushButton("选择输出目录")
        btn_output.clicked.connect(self.select_output_dir)
        output_layout.addWidget(btn_output)
        
        btn_blend = QPushButton("开始混合")
        btn_blend.clicked.connect(self.blend_normal_maps)
        output_layout.addWidget(btn_blend)
        
        left_layout.addWidget(output_widget)
        layout.addWidget(left_panel)
        
        # 右侧面板 - 预览
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("预览："))
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.preview_label)
        layout.addWidget(right_panel)
    
    def add_normal_map(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择法线贴图",
            "",
            "图像文件 (*.png *.jpg *.jpeg)"
        )
        
        for file in files:
            item_text = f"{os.path.basename(file)} - 权重: {self.weight_spin.value():.1f}"
            self.map_list.addItem(item_text)
            self.normal_maps.append({
                'path': file,
                'weight': self.weight_spin.value()
            })
    
    def remove_normal_map(self):
        current_row = self.map_list.currentRow()
        if current_row >= 0:
            self.map_list.takeItem(current_row)
            self.normal_maps.pop(current_row)
    
    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            ""
        )
        if dir_path:
            self.output_dir = dir_path
    
    def blend_normal_maps(self):
        if len(self.normal_maps) < 2:
            QMessageBox.warning(self, "警告", "请至少添加两张法线贴图")
            return
            
        if not self.output_dir:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return
        
        try:
            # 读取第一张图确定尺寸
            first_map = cv2.imread(self.normal_maps[0]['path'])
            height, width = first_map.shape[:2]
            
            # 初始化结果数组
            result = np.zeros_like(first_map, dtype=np.float32)
            total_weight = 0
            
            # 混合所有法线贴图
            for normal_map in self.normal_maps:
                img = cv2.imread(normal_map['path'])
                if img.shape[:2] != (height, width):
                    img = cv2.resize(img, (width, height))
                
                weight = normal_map['weight']
                result += img.astype(np.float32) * weight
                total_weight += weight
            
            # 归一化
            if total_weight > 0:
                result /= total_weight
            
            # 保存结果
            output_path = os.path.join(self.output_dir, "blended_normal.png")
            cv2.imwrite(output_path, result.astype(np.uint8))
            
            QMessageBox.information(self, "成功", f"混合完成！\n保存至：{output_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理过程中出现错误：{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NormalMapBlender()
    window.show()
    sys.exit(app.exec())