import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                            QSpinBox, QDoubleSpinBox, QListWidget, QMessageBox,
                            QTreeWidget, QTreeWidgetItem, QTableWidget, 
                            QTableWidgetItem, QComboBox, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import cv2
import numpy as np
from PIL import Image

class BlendTask:
    def __init__(self, name):
        self.name = name
        self.items = []  # 存储BlendItem对象
        self.enabled = True

class BlendItem:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.weight = 1.0
        self.blend_mode = "Normal"  # 混合模式
        self.enabled = True

class NormalMapBlender(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("法线贴图混合工具")
        self.setMinimumSize(1200, 800)
        
        # 数据存储
        self.tasks = []  # 存储BlendTask对象
        self.output_dir = ""
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板 - 任务树
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 任务树
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["混合任务"])
        left_layout.addWidget(QLabel("任务列表："))
        left_layout.addWidget(self.task_tree)
        
        # 任务控制按钮
        task_btn_layout = QHBoxLayout()
        btn_add_task = QPushButton("添加任务")
        btn_add_task.clicked.connect(self.add_task)
        btn_remove_task = QPushButton("删除任务")
        btn_remove_task.clicked.connect(self.remove_task)
        task_btn_layout.addWidget(btn_add_task)
        task_btn_layout.addWidget(btn_remove_task)
        left_layout.addLayout(task_btn_layout)
        
        # 子项控制按钮
        item_btn_layout = QHBoxLayout()
        btn_add_item = QPushButton("添加子项")
        btn_add_item.clicked.connect(self.add_item)
        btn_remove_item = QPushButton("删除子项")
        btn_remove_item.clicked.connect(self.remove_item)
        item_btn_layout.addWidget(btn_add_item)
        item_btn_layout.addWidget(btn_remove_item)
        left_layout.addLayout(item_btn_layout)
        
        main_layout.addWidget(left_panel)
        
        # 中间面板 - 参数表格
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        
        # 参数表格
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(4)
        self.param_table.setHorizontalHeaderLabels(["名称", "权重", "混合模式", "启用"])
        middle_layout.addWidget(QLabel("参数设置："))
        middle_layout.addWidget(self.param_table)
        
        main_layout.addWidget(middle_panel)
        
        # 右侧面板 - 预览和控制
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 预览区域
        right_layout.addWidget(QLabel("预览："))
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.preview_label)
        
        # 预览控制
        preview_controls = QHBoxLayout()
        btn_reset = QPushButton("重置")
        btn_reset.clicked.connect(self.reset_preview)
        btn_update = QPushButton("更新预览")
        btn_update.clicked.connect(self.update_preview)
        preview_controls.addWidget(btn_reset)
        preview_controls.addWidget(btn_update)
        right_layout.addLayout(preview_controls)
        
        # 输出控制
        output_controls = QVBoxLayout()
        btn_output = QPushButton("选择输出目录")
        btn_output.clicked.connect(self.select_output_dir)
        btn_blend = QPushButton("导出全部混合图")
        btn_blend.clicked.connect(self.export_all_blended_maps)
        output_controls.addWidget(btn_output)
        output_controls.addWidget(btn_blend)
        right_layout.addLayout(output_controls)
        
        main_layout.addWidget(right_panel)
        
        # 在 init_ui 中添加树的选择变更信号连接
        self.task_tree.itemSelectionChanged.connect(self.on_selection_changed)
        # 添加双击编辑支持
        self.task_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def on_selection_changed(self):
        """当选择改变时更新参数表格和预览"""
        self.update_param_table()
        self.update_preview()

    def on_item_double_clicked(self, item, column):
        """处理项目双击事件"""
        if not item.parent():  # 只允许编辑任务名称
            current_name = item.text(0)
            new_name, ok = QInputDialog.getText(
                self,
                "重命名任务",
                "请输入新的任务名称：",
                text=current_name
            )
            
            if ok and new_name:
                # 更新树项显示
                item.setText(0, new_name)
                # 更新数据模型
                task_index = self.task_tree.indexOfTopLevelItem(item)
                if task_index >= 0 and task_index < len(self.tasks):
                    self.tasks[task_index].name = new_name  # 确保更新任务对象的名称
                    print(f"Task renamed to: {new_name}")  # 添加调试输出

    def add_task(self):
        task_name = f"blende-task-{len(self.tasks) + 1}"
        task = BlendTask(task_name)  # 确保创建任务时设置了名称
        self.tasks.append(task)
        
        task_item = QTreeWidgetItem(self.task_tree)
        task_item.setText(0, task_name)
        task_item.setFlags(task_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.task_tree.addTopLevelItem(task_item)
        
        # 选中新添加的任务
        self.task_tree.setCurrentItem(task_item)
        print(f"New task created: {task_name}")  # 添加调试输出
    
    def add_item(self):
        current_task = self.get_selected_task()
        if not current_task:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
            
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择法线贴图",
            "",
            "图像文件 (*.png *.jpg *.jpeg)"
        )
        
        if not files:
            return
            
        current_tree_item = self.task_tree.currentItem()
        # 如果当前选中的是子项，获取其父项
        if current_tree_item.parent():
            current_tree_item = current_tree_item.parent()
            
        for file in files:
            # 使用文件名作为项目名称
            file_name = os.path.basename(file)
            blend_item = BlendItem(file_name, file)
            current_task.items.append(blend_item)
            
            # 创建新的树项目，只显示文件名
            item = QTreeWidgetItem(current_tree_item)
            item.setText(0, file_name)
    
        # 更新界面
        self.update_param_table()
        self.update_preview()
    
    def remove_task(self):
        current_row = self.task_tree.currentRow()
        if current_row >= 0:
            self.task_tree.takeTopLevelItem(current_row)
            self.tasks.pop(current_row)
    
    def remove_item(self):
        """删除选中的任务或子项"""
        current_item = self.task_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的项目")
            return
        
        # 获取父项（如果是子项的话）
        parent_item = current_item.parent()
        
        if parent_item:  # 如果是子项
            # 找到对应的任务
            task_index = self.task_tree.indexOfTopLevelItem(parent_item)
            if task_index >= 0 and task_index < len(self.tasks):
                task = self.tasks[task_index]
                # 获取子项在父项中的索引
                item_index = parent_item.indexOfChild(current_item)
                if item_index >= 0 and item_index < len(task.items):
                    # 从数据模型中移除
                    task.items.pop(item_index)
                    # 从树中移除
                    parent_item.removeChild(current_item)
        else:  # 如果是任务项
            task_index = self.task_tree.indexOfTopLevelItem(current_item)
            if task_index >= 0:
                # 从数据模型中移除
                self.tasks.pop(task_index)
                # 从树中移除
                self.task_tree.takeTopLevelItem(task_index)
        
        # 更新参数表格
        self.update_param_table()

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            ""
        )
        if dir_path:
            self.output_dir = dir_path
    
    def export_all_blended_maps(self):
        """导出所有任务的混合结果"""
        if not self.tasks:
            QMessageBox.warning(self, "警告", "没有可导出的任务")
            return
        
        if not self.output_dir:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return
        
        try:
            success_count = 0
            export_info = []  # 用于收集导出信息
            
            for task in self.tasks:
                if not task.items:
                    continue
                
                # 生成该任务的混合结果
                result = self.blend_task_maps(task)
                if result is not None:
                    # 使用任务名称作为文件名，确保文件名合法
                    safe_name = "".join(c for c in task.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    if not safe_name:
                        safe_name = f"blende-task-{self.tasks.index(task) + 1}"
                    
                    output_filename = f"{safe_name}.png"
                    output_path = os.path.join(self.output_dir, output_filename)
                    
                    # 保存混合结果
                    cv2.imwrite(output_path, result)
                    success_count += 1
                    export_info.append(f"任务 '{task.name}' => {output_filename}")
                    print(f"Exporting task '{task.name}' to {output_filename}")  # 添加调试输出
            
            if success_count > 0:
                export_details = "\n".join(export_info)
                QMessageBox.information(
                    self,
                    "导出成功",
                    f"成功导出 {success_count} 个混合图像：\n\n{export_details}\n\n保存位置：\n{self.output_dir}"
                )
            else:
                QMessageBox.warning(self, "警告", "没有可导出的混合结果")
            
        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"导出过程中出错：{str(e)}")

    def blend_task_maps(self, task):
        """混合指定任务的所有法线贴图"""
        if not task.items:
            return None
        
        try:
            # 读取第一张图确定尺寸
            first_map = cv2.imread(task.items[0].path)
            if first_map is None:
                raise Exception(f"无法读取图像: {task.items[0].path}")
            
            height, width = first_map.shape[:2]
            
            # 初始化结果数组
            result = np.zeros_like(first_map, dtype=np.float32)
            total_weight = 0
            
            # 混合所有启用的法线贴图
            for item in task.items:
                if not item.enabled:
                    continue
                
                img = cv2.imread(item.path)
                if img is None:
                    continue
                
                if img.shape[:2] != (height, width):
                    img = cv2.resize(img, (width, height))
                
                # 根据混合模式处理
                if item.blend_mode == "Normal":
                    weighted_img = img.astype(np.float32) * item.weight
                elif item.blend_mode == "Multiply":
                    weighted_img = (img.astype(np.float32) / 255.0) * result
                    weighted_img *= item.weight
                elif item.blend_mode == "Add":
                    weighted_img = result + (img.astype(np.float32) * item.weight)
                elif item.blend_mode == "Overlay":
                    mask = result <= 127
                    weighted_img = np.where(mask,
                                          (2 * result * img.astype(np.float32)) / 255.0,
                                          255 - (2 * (255 - result) * (255 - img.astype(np.float32))) / 255.0)
                    weighted_img *= item.weight
                else:
                    weighted_img = img.astype(np.float32) * item.weight
                
                result += weighted_img
                total_weight += item.weight
            
            # 归一化
            if total_weight > 0:
                result = np.clip(result / total_weight, 0, 255)
            
            return result.astype(np.uint8)
        
        except Exception as e:
            QMessageBox.critical(self, "混合错误", f"混合过程中出错：{str(e)}")
            return None

    def get_selected_task(self):
        """获取当前选中的任务"""
        current_item = self.task_tree.currentItem()
        if not current_item:
            return None
        
        # 如果选中的是子项，获取其父任务项
        parent = current_item.parent()
        task_item = parent if parent else current_item
        
        # 获取任务索引
        task_index = self.task_tree.indexOfTopLevelItem(task_item)
        if task_index >= 0 and task_index < len(self.tasks):
            return self.tasks[task_index]
        
        return None

    def update_param_table(self):
        """更新参数表格"""
        self.param_table.setRowCount(0)  # 清空表格
        
        current_task = self.get_selected_task()
        if not current_task:
            return
        
        # 更新表格内容
        for index, item in enumerate(current_task.items):
            self.param_table.insertRow(index)
            
            # 名称（使用文件名）
            name_item = QTableWidgetItem(os.path.basename(item.path))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 禁止编辑
            self.param_table.setItem(index, 0, name_item)
            
            # 权重
            weight_spin = QDoubleSpinBox()
            weight_spin.setRange(0, 1)
            weight_spin.setSingleStep(0.1)
            weight_spin.setValue(item.weight)
            weight_spin.valueChanged.connect(lambda value, row=index: self.update_item_weight(row, value))
            self.param_table.setCellWidget(index, 1, weight_spin)
            
            # 混合模式
            blend_mode_combo = QComboBox()
            blend_modes = ["Normal", "Multiply", "Add", "Overlay"]
            blend_mode_combo.addItems(blend_modes)
            blend_mode_combo.setCurrentText(item.blend_mode)
            blend_mode_combo.currentTextChanged.connect(lambda text, row=index: self.update_item_blend_mode(row, text))
            self.param_table.setCellWidget(index, 2, blend_mode_combo)
            
            # 启用状态
            enabled_item = QTableWidgetItem()
            enabled_item.setCheckState(Qt.CheckState.Checked if item.enabled else Qt.CheckState.Unchecked)
            enabled_item.setFlags(enabled_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            self.param_table.setItem(index, 3, enabled_item)
        
        self.param_table.resizeColumnsToContents()

    def update_item_weight(self, row, value):
        """更新子项权重"""
        current_task = self.get_selected_task()
        if current_task and row < len(current_task.items):
            current_task.items[row].weight = value
            self.update_preview()

    def update_item_blend_mode(self, row, mode):
        """更新子项混合模式"""
        current_task = self.get_selected_task()
        if current_task and row < len(current_task.items):
            current_task.items[row].blend_mode = mode
            self.update_preview()

    def reset_preview(self):
        """重置所有参数到默认值"""
        current_task = self.get_selected_task()
        if not current_task:
            return
        
        for item in current_task.items:
            item.weight = 1.0
            item.blend_mode = "Normal"
            item.enabled = True
        
        self.update_param_table()
        self.update_preview()

    def update_preview(self):
        """更新预览图像"""
        current_task = self.get_selected_task()
        if not current_task or not current_task.items:
            self.preview_label.clear()
            return
        
        try:
            # 使用通用的混合方法获取结果
            result = self.blend_task_maps(current_task)
            if result is None:
                self.preview_label.clear()
                return
            
            # 转换为RGB格式（OpenCV使用BGR格式）
            result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            
            # 创建QImage并显示
            height, width = result.shape[:2]
            bytes_per_line = 3 * width
            q_img = QImage(result.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            
            # 保持纵横比缩放到预览区域
            scaled_pixmap = QPixmap.fromImage(q_img).scaled(
                400, 400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.preview_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            QMessageBox.critical(self, "预览错误", f"更新预览时出错：{str(e)}")
            self.preview_label.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NormalMapBlender()
    window.show()
    sys.exit(app.exec())