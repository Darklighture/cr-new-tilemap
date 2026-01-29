#!/usr/bin/env python
"""
Generate Clash Royale vector arena maps from CSV tilemaps.
"""

import csv
import os
import sys
import subprocess
import glob
from pathlib import Path
from typing import Dict, Tuple, List
import yaml
from reportlab.pdfgen import canvas
from reportlab.lib.units import pica


class Config:
    """配置类"""
    def __init__(self, config_dict):
        if config_dict is None:
            config_dict = {}
        for key, value in config_dict.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)


class TileMapGenerator:
    """Generate Clash Royale style arena maps from CSV tilemaps."""
    
    # 颜色定义
    colors = {
        '-1': (0.9, 0.9, 0.9),  # 默认灰色
        '0': (0.9, 0.9, 0.9),   # 空地
        '1': (0.5, 0.9, 0.9),   # 水域
        '2': (0.9, 0.9, 0.5),   # 沙滩
        '16': (0.7, 0.5, 0.5),  # 红砖
        '17': (0.5, 0.7, 0.5),  # 草地
        '18': (0.5, 0.5, 0.7),  # 蓝石
        '32': (0.7, 0.7, 0.7),  # 灰石
        '33': (0.4, 0.9, 0.6),  # 亮绿
        '34': (0.4, 0.7, 0.5),  # 暗绿
        '48': (0.2, 0.8, 0.8),  # 青色
        '49': (0.8, 0.2, 0.8),  # 紫色
        '50': (0.3, 0.6, 0.6),  # 深青
        '64': (0.6, 0.4, 0.6)   # 深紫
    }
    
    def __init__(self, config_path: str = None):
        """Initialize the generator with configuration."""
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Config:
        """加载配置"""
        if not config_path or not os.path.exists(config_path):
            # 如果配置文件不存在，创建默认配置
            return self._create_default_config()
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                if config_data is None:
                    config_data = {}
                return Config(config_data)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_config()
            
    def _create_default_config(self) -> Config:
        """创建默认配置"""
        default_config = {
            'pdf_folder': './output',
            'csv_folder': './data', 
            'openfile': False,
            'auto_scan': True  # 默认启用自动扫描
        }
        return Config(default_config)
    
    def run(self):
        """生成所有地图"""
        # 检查是否启用自动扫描
        auto_scan = getattr(self.config, 'auto_scan', True)
        
        if auto_scan:
            # 自动扫描data文件夹中的CSV文件
            tilemaps = self._scan_csv_files()
            print(f"Auto-scanned {len(tilemaps)} CSV files: {[name for name, _ in tilemaps]}")
        else:
            # 使用配置文件中指定的地图列表
            tilemaps = [(name, None) for name in getattr(self.config, 'tilemaps', [])]
            print(f"Using configured tilemaps: {[name for name, _ in tilemaps]}")
        
        if not tilemaps:
            print("No tilemaps found or specified")
            return
            
        success_count = 0
        for tilemap_name, csv_path in tilemaps:
            try:
                self.make_tilemap(tilemap_name, csv_path)
                print(f"✓ Generated: {tilemap_name}")
                success_count += 1
            except Exception as e:
                print(f"✗ Error generating {tilemap_name}: {e}")
        
        print(f"Generation completed: {success_count}/{len(tilemaps)} successful")
    
    def _scan_csv_files(self):
        """自动扫描data文件夹中的CSV文件"""
        csv_folder = getattr(self.config, 'csv_folder', './data')
        csv_dir = Path(csv_folder)
        
        if not csv_dir.exists():
            print(f"CSV folder does not exist: {csv_dir}")
            return []
        
        # 查找所有CSV文件
        csv_files = list(csv_dir.glob("*.csv"))
        tilemaps = []
        
        for csv_file in csv_files:
            # 使用文件名（不含扩展名）作为地图名称
            map_name = csv_file.stem
            tilemaps.append((map_name, csv_file))
        
        return tilemaps
    
    def make_tilemap(self, name: str, csv_path: Path = None):
        """生成单个地图"""
        pdf_folder = getattr(self.config, 'pdf_folder', './output')
        csv_folder = getattr(self.config, 'csv_folder', './data')
        
        # 创建输出目录
        pdf_dir = Path(pdf_folder)
        pdf_dir.mkdir(parents=True, exist_ok=True)
        
        # 确定CSV文件路径
        if csv_path is None:
            csv_dir = Path(csv_folder)
            csv_file = csv_dir / f"{name}.csv"
        else:
            csv_file = csv_path
        
        pdf_file = pdf_dir / f"{name}.pdf"
        
        print(f"Processing: {csv_file} -> {pdf_file}")
        
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        # 创建PDF画布
        c = canvas.Canvas(str(pdf_file), bottomup=0)
        
        # 解析CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            y = 0
            start = -10000  # 初始状态，不处理行
            
            for row in reader:
                x = 0
                
                # 遇到"Map"行后开始处理
                if row and row[0] == 'Map':
                    start = -2  # 跳过两行后开始处理数据
                    print(f"  Found 'Map' header in {name}")
                
                # 遇到"Layout"行后停止处理
                if row and row[0] == 'Layout':
                    start = -10000  # 停止处理
                    print(f"  Found 'Layout' header in {name}")
                
                # 处理数据行
                if start > 0:
                    for value in row:
                        if x > 0:  # 跳过第一列（可能是行号）
                            if value == '':
                                value = '-1'  # 空值使用默认颜色
                            self.draw_tile(c, x, start, value)
                        x += 1
                
                y += 1
                start += 1  # 源文件中的计数器递增
        
        c.showPage()
        c.save()
        print(f"  PDF created: {pdf_file}")
        
        # 如果需要，打开文件
        if getattr(self.config, 'openfile', False):
            self._open_file(pdf_file)
    
    def draw_tile(self, c, x, y, value):
        """严格按照源文件的绘制逻辑"""
        w = 1
        h = 1
        s = 1 * pica
        x0 = 1 * pica
        y0 = 1 * pica
        
        # 设置线条和填充颜色
        c.setLineWidth(0.3)
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        
        # 获取颜色值，如果不存在则使用默认值
        color = self.colors.get(value, self.colors['-1'])
        c.setFillColorRGB(*color)
        
        # 绘制矩形
        c.rect(x0 + x * s, y0 + y * s, w * s, h * s, fill=1)
    
    def _open_file(self, file_path: Path):
        """打开文件"""
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.call(['open', str(file_path)])
            elif sys.platform == 'win32':  # Windows
                os.startfile(str(file_path))
            else:  # Linux
                subprocess.call(['xdg-open', str(file_path)])
        except Exception as e:
            print(f"Could not open file: {e}")


def main():
    """主函数"""
    config_path = './config.yml'
    
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(config_path):
        default_config = {
            'pdf_folder': './output',
            'csv_folder': './data',
            'openfile': False,
            'auto_scan': True  # 启用自动扫描
        }
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
        print(f"Created default config at {config_path}")
    
    try:
        generator = TileMapGenerator(config_path)
        generator.run()
        print("Tilemap generation completed!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()