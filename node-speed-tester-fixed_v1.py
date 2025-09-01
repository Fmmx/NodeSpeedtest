#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 超高性能节点测速工具 V1.0 - 炫彩可视化版
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
炫彩界面 | 实时动画 | 智能仪表盘 | 视觉盛宴
"""

import sys
import os
import time
import json
import base64
import socket
import ssl
import argparse
from datetime import datetime, timedelta
import subprocess
import gc
import signal
import threading
import queue
import urllib.parse
import urllib.request
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import random
from collections import deque
import statistics
import re

# ═══════════════════════════════════════════════════════════════
# 终端颜色和样式定义
# ═══════════════════════════════════════════════════════════════

class Colors:
    """终端颜色类 - 友好配色方案"""
    # 基础颜色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 友好配色主题
    PRIMARY = '\033[38;2;64;150;250m'      # 柔和蓝色
    SUCCESS = '\033[38;2;76;175;80m'       # 柔和绿色  
    WARNING = '\033[38;2;255;152;0m'       # 柔和橙色
    ERROR = '\033[38;2;244;67;54m'         # 柔和红色
    INFO = '\033[38;2;100;181;246m'        # 淡蓝色
    SECONDARY = '\033[38;2;156;163;175m'   # 柔和灰色
    ACCENT = '\033[38;2;149;117;205m'      # 柔和紫色
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'
    
    # 重置
    RESET = '\033[0m'
    
    # 渐变色（使用256色）
    @staticmethod
    def rgb(r, g, b):
        """RGB颜色"""
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def gradient_text(text, start_color=(255, 0, 0), end_color=(0, 255, 0)):
        """渐变文字"""
        result = ""
        length = len(text)
        for i, char in enumerate(text):
            ratio = i / max(length - 1, 1)
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            result += Colors.rgb(r, g, b) + char
        return result + Colors.RESET

# ═══════════════════════════════════════════════════════════════
# UI组件类
# ═══════════════════════════════════════════════════════════════

class UIComponents:
    """UI组件库"""
    
    @staticmethod
    def clear_screen():
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def move_cursor(x, y):
        """移动光标"""
        print(f'\033[{y};{x}H', end='')
    
    @staticmethod
    def hide_cursor():
        """隐藏光标"""
        print('\033[?25l', end='')
    
    @staticmethod
    def show_cursor():
        """显示光标"""
        print('\033[?25h', end='')
    
    @staticmethod
    def progress_bar(current, total, width=50, style='gradient'):
        """友好的进度条样式"""
        if total == 0:
            percent = 0
        else:
            percent = current / total
        
        filled = int(width * percent)
        empty = width - filled
        
        if style == 'gradient':
            # 柔和渐变进度条
            bar = ""
            for i in range(filled):
                ratio = i / max(width - 1, 1)
                # 使用更柔和的颜色过渡
                if ratio < 0.33:
                    # 从浅蓝到蓝
                    intensity = int(100 + ratio * 3 * 155)
                    bar += Colors.rgb(100, intensity, 246) + "█"
                elif ratio < 0.67:
                    # 从蓝到绿
                    sub_ratio = (ratio - 0.33) * 3
                    r = int(100 * (1 - sub_ratio))
                    g = int(181 + sub_ratio * 74)
                    b = int(246 * (1 - sub_ratio) + 80 * sub_ratio)
                    bar += Colors.rgb(r, g, b) + "█"
                else:
                    # 从绿到亮绿
                    sub_ratio = (ratio - 0.67) * 3
                    intensity = int(175 + sub_ratio * 50)
                    bar += Colors.rgb(76, intensity, 80) + "█"
            # 使用更柔和的空白字符
            bar += Colors.SECONDARY + "░" * empty + Colors.RESET
        elif style == 'simple':
            # 简洁进度条
            bar = Colors.PRIMARY + "█" * filled + Colors.SECONDARY + "░" * empty + Colors.RESET
        elif style == 'smooth':
            # 平滑进度条
            bar = Colors.SUCCESS + "▓" * filled + Colors.SECONDARY + "░" * empty + Colors.RESET
        else:
            # 普通进度条
            bar = Colors.SUCCESS + "█" * filled + Colors.SECONDARY + "░" * empty + Colors.RESET
        
        # 使用更友好的百分比颜色
        if percent >= 1.0:
            percent_color = Colors.SUCCESS
        elif percent >= 0.7:
            percent_color = Colors.INFO
        elif percent >= 0.3:
            percent_color = Colors.WARNING
        else:
            percent_color = Colors.SECONDARY
        
        return f"{bar} {percent_color}{percent*100:.1f}%{Colors.RESET}"
    
    @staticmethod
    def spinner(index):
        """加载动画"""
        spinners = {
            'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'line': ['|', '/', '-', '\\'],
            'circle': ['◐', '◓', '◑', '◒'],
            'square': ['◰', '◳', '◲', '◱'],
            'arrow': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
            'bounce': ['⠁', '⠂', '⠄', '⠂'],
            'wave': [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂'],
            'pulse': ['•', '○', '◉', '◎', '◉', '○'],
        }
        spinner = spinners['dots']
        return spinner[index % len(spinner)]
    
    @staticmethod
    def box(title, content, width=60, color=Colors.CYAN):
        """绘制边框盒子"""
        lines = []
        lines.append(color + "╔" + "═" * (width - 2) + "╗" + Colors.RESET)
        
        # 标题
        if title:
            title_line = color + "║ " + Colors.BOLD + Colors.BRIGHT_WHITE + title.center(width - 4) + Colors.RESET + color + " ║" + Colors.RESET
            lines.append(title_line)
            lines.append(color + "╠" + "═" * (width - 2) + "╣" + Colors.RESET)
        
        # 内容
        for line in content.split('\n'):
            if len(line) > width - 4:
                line = line[:width - 7] + "..."
            lines.append(color + "║ " + Colors.RESET + line.ljust(width - 4) + color + " ║" + Colors.RESET)
        
        lines.append(color + "╚" + "═" * (width - 2) + "╝" + Colors.RESET)
        return '\n'.join(lines)
    
    @staticmethod
    def status_icon(status):
        """状态图标"""
        icons = {
            'success': Colors.BRIGHT_GREEN + '✅',
            'error': Colors.BRIGHT_RED + '❌',
            'warning': Colors.BRIGHT_YELLOW + '⚠️ ',
            'info': Colors.BRIGHT_BLUE + 'ℹ️ ',
            'loading': Colors.BRIGHT_CYAN + '⏳',
            'complete': Colors.BRIGHT_GREEN + '✨',
            'rocket': '🚀',
            'fire': '🔥',
            'star': '⭐',
            'trophy': '🏆',
            'lightning': '⚡',
            'shield': '🛡️',
            'globe': '🌍',
            'chart': '📊',
        }
        return icons.get(status, '') + Colors.RESET

    @staticmethod
    def get_display_width(text):
        """计算字符串的显示宽度（汉字占2，英文占1）"""
        width = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                width += 2
            else:
                width += 1
        return width

    @staticmethod
    def truncate_by_width(text, max_width):
        """按显示宽度截断字符串"""
        original_width = UIComponents.get_display_width(text)
        if original_width <= max_width:
            return text

        width = 0
        result = ""
        for char in text:
            char_width = 2 if '\u4e00' <= char <= '\u9fff' else 1
            if width + char_width > max_width - 3: # Reserve space for "..."
                return result + "..."
            width += char_width
            result += char
        return result

# ═══════════════════════════════════════════════════════════════
# 可视化仪表盘
# ═══════════════════════════════════════════════════════════════

class Dashboard:
    """实时仪表盘"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.last_update = time.time()
        self.spinner_index = 0
        self.animation_frame = 0
        self.stats = {
            'total': 0,
            'tested': 0,
            'success': 0,
            'failed': 0,
            'speed': 0,
            'eta': 'N/A',
            'memory': 0,
            'threads': 0,
            'avg_latency': 0,
            'min_latency': float('inf'),
            'max_latency': 0,
        }
        self.recent_nodes = deque(maxlen=5)
        self.speed_history = deque(maxlen=20)
        self.latency_history = deque(maxlen=100)
        
    def update_stats(self, **kwargs):
        """更新统计数据"""
        self.stats.update(kwargs)
        
        # 计算速度
        if self.stats['tested'] > 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if elapsed > 0:
                self.stats['speed'] = self.stats['tested'] / elapsed
                self.speed_history.append(self.stats['speed'])
        
        # 计算ETA
        if self.stats['speed'] > 0 and self.stats['total'] > self.stats['tested']:
            remaining = self.stats['total'] - self.stats['tested']
            eta_seconds = remaining / self.stats['speed']
            self.stats['eta'] = str(timedelta(seconds=int(eta_seconds)))
        
        # 计算平均延迟
        if self.latency_history:
            self.stats['avg_latency'] = statistics.mean(self.latency_history)
    
    def add_recent_node(self, node_info):
        """添加最近测试的节点"""
        self.recent_nodes.append(node_info)
        if 'latency' in node_info:
            self.latency_history.append(node_info['latency'])
            self.stats['min_latency'] = min(self.stats['min_latency'], node_info['latency'])
            self.stats['max_latency'] = max(self.stats['max_latency'], node_info['latency'])
    
    def render(self):
        """渲染仪表盘"""
        self.animation_frame += 1
        self.spinner_index += 1
        
        # 清屏并隐藏光标
        UIComponents.clear_screen()
        UIComponents.hide_cursor()
        
        # 渲染标题
        self._render_header()
        
        # 渲染主要统计
        self._render_main_stats()
        
        # 渲染进度条
        self._render_progress()
        
        # 渲染性能图表
        self._render_performance()
        
        # 渲染延迟分布
        self._render_latency_distribution()
        
        # 渲染最近节点
        self._render_recent_nodes()
        
        # 渲染底部信息
        self._render_footer()
    
    def _render_header(self):
        """渲染标题 - 简洁样式"""
        title = "节点测速仪表盘 V1.0"
        
        # 使用更柔和的渐变
        gradient_title = Colors.gradient_text(title, (64, 150, 250), (149, 117, 205))
        
        width = 72
        print("\n")
        
        # 使用更简洁的边框
        print("  " + Colors.PRIMARY + "━" * width + Colors.RESET)
        
        clean_title = re.sub(r'\033\[[0-9;]*m', '', title)
        padding_total = width - len(clean_title)
        pad_left = padding_total // 2
        pad_right = padding_total - pad_left
        
        print(f"  {' ' * pad_left}{gradient_title}{' ' * pad_right}")
        
        print("  " + Colors.PRIMARY + "━" * width + Colors.RESET)
        print()
    
    def _render_main_stats(self):
        """渲染主要统计"""
        # 第一行：基础统计
        print(f"  {UIComponents.status_icon('rocket')} {Colors.BOLD}测试进度{Colors.RESET}")
        print()
        
        # 使用不同颜色显示数字
        tested_color = Colors.BRIGHT_CYAN if self.stats['tested'] < self.stats['total'] else Colors.BRIGHT_GREEN
        success_color = Colors.BRIGHT_GREEN if self.stats['success'] > 0 else Colors.BRIGHT_RED
        
        stats_line1 = (
            f"  {Colors.BRIGHT_WHITE}总节点:{Colors.RESET} {Colors.BRIGHT_YELLOW}{self.stats['total']:,}{Colors.RESET}  "
            f"{Colors.BRIGHT_WHITE}已测试:{Colors.RESET} {tested_color}{self.stats['tested']:,}{Colors.RESET}  "
            f"{Colors.BRIGHT_WHITE}成功:{Colors.RESET} {success_color}{self.stats['success']:,}{Colors.RESET}  "
            f"{Colors.BRIGHT_WHITE}失败:{Colors.RESET} {Colors.BRIGHT_RED}{self.stats['failed']:,}{Colors.RESET}"
        )
        print(stats_line1)
        
        # 第二行：性能统计
        speed_color = Colors.BRIGHT_GREEN if self.stats['speed'] > 10 else Colors.BRIGHT_YELLOW if self.stats['speed'] > 5 else Colors.BRIGHT_RED
        
        stats_line2 = (
            f"  {Colors.BRIGHT_WHITE}速度:{Colors.RESET} {speed_color}{self.stats['speed']:.1f}/s{Colors.RESET}  "
            f"{Colors.BRIGHT_WHITE}线程:{Colors.RESET} {Colors.BRIGHT_MAGENTA}{self.stats['threads']}{Colors.RESET}  "
            f"{Colors.BRIGHT_WHITE}剩余时间:{Colors.RESET} {Colors.BRIGHT_CYAN}{self.stats['eta']}{Colors.RESET}  "
            f"{UIComponents.spinner(self.spinner_index)}"
        )
        print(stats_line2)
        
        # 第三行：延迟统计
        if self.stats['avg_latency'] > 0:
            avg_color = Colors.BRIGHT_GREEN if self.stats['avg_latency'] < 100 else Colors.BRIGHT_YELLOW if self.stats['avg_latency'] < 300 else Colors.BRIGHT_RED
            stats_line3 = (
                f"  {Colors.BRIGHT_WHITE}平均延迟:{Colors.RESET} {avg_color}{self.stats['avg_latency']:.0f}ms{Colors.RESET}  "
                f"{Colors.BRIGHT_WHITE}最低:{Colors.RESET} {Colors.BRIGHT_GREEN}{self.stats['min_latency']:.0f}ms{Colors.RESET}  "
                f"{Colors.BRIGHT_WHITE}最高:{Colors.RESET} {Colors.BRIGHT_RED}{self.stats['max_latency']:.0f}ms{Colors.RESET}"
            )
            print(stats_line3)
        print()
    
    def _render_progress(self):
        """渲染进度条"""
        print(f"  {UIComponents.status_icon('chart')} {Colors.BOLD}整体进度{Colors.RESET}")
        
        # 主进度条
        progress = UIComponents.progress_bar(
            self.stats['tested'], 
            self.stats['total'], 
            width=60, 
            style='gradient'
        )
        print(f"  {progress}")
        
        # 成功率进度条
        if self.stats['tested'] > 0:
            success_rate = self.stats['success'] / self.stats['tested']
            success_bar = UIComponents.progress_bar(
                self.stats['success'],
                self.stats['tested'],
                width=60,
                style='rainbow'
            )
            print(f"  {Colors.DIM}成功率: {success_bar}{Colors.RESET}")
        print()
    
    def _render_performance(self):
        """渲染性能图表"""
        if len(self.speed_history) > 1:
            print(f"  {UIComponents.status_icon('lightning')} {Colors.BOLD}速度趋势{Colors.RESET} (节点/秒)")
            
            # 简单的ASCII图表
            max_speed = max(self.speed_history) if self.speed_history else 1
            height = 5
            width = min(len(self.speed_history), 60)
            
            # 创建图表
            chart = []
            for h in range(height, 0, -1):
                line = "  "
                threshold = (h / height) * max_speed
                for i in range(width):
                    if i < len(self.speed_history):
                        speed_val = self.speed_history[-(width - i)]
                        if speed_val >= threshold:
                            # 动态颜色
                            ratio = speed_val / max_speed
                            if ratio > 0.8:
                                color = Colors.rgb(0, 255, 0)
                            elif ratio > 0.5:
                                color = Colors.rgb(255, 255, 0)
                            else:
                                color = Colors.rgb(255, 0, 0)
                            line += color + "█" + Colors.RESET
                        else:
                            line += " "
                chart.append(line)
            
            for line in chart:
                print(line)
            
            # 添加坐标轴
            print("  " + Colors.DIM + "└" + "─" * width + Colors.RESET)
            print()
    
    def _render_latency_distribution(self):
        """渲染延迟分布"""
        if len(self.latency_history) > 5:
            print(f"  {UIComponents.status_icon('globe')} {Colors.BOLD}延迟分布{Colors.RESET}")
            
            # 创建延迟分组
            ranges = [(0, 50, '极快', Colors.BRIGHT_GREEN),
                      (50, 100, '快速', Colors.GREEN),
                      (100, 200, '正常', Colors.YELLOW),
                      (200, 300, '较慢', Colors.rgb(255, 165, 0)),
                      (300, 500, '很慢', Colors.RED)]
            
            # 统计每个范围的节点数
            distribution = {}
            for min_lat, max_lat, label, color in ranges:
                count = sum(1 for lat in self.latency_history if min_lat <= lat < max_lat)
                if count > 0:
                    distribution[label] = (count, color)
            
            # 绘制条形图
            if distribution:
                max_count = max(v[0] for v in distribution.values())
                for label, (count, color) in distribution.items():
                    bar_width = int((count / max_count) * 40)
                    bar = color + "█" * bar_width + Colors.RESET
                    percentage = (count / len(self.latency_history)) * 100
                    print(f"  {label:6} {bar} {count:3} ({percentage:.1f}%)")
            print()
    
    def _render_recent_nodes(self):
        """渲染最近测试的节点"""
        if self.recent_nodes:
            print(f"  {UIComponents.status_icon('star')} {Colors.BOLD}最新发现的优质节点{Colors.RESET}")
            
            # 获取最好的节点
            best_nodes = sorted(list(self.recent_nodes), key=lambda x: x.get('latency', 999999))[:3]
            
            for i, node in enumerate(best_nodes):
                latency = node.get('latency', 0)
                name = node.get('name', 'Unknown')
                
                # 根据延迟选择颜色和图标
                if latency < 50:
                    latency_color = Colors.rgb(0, 255, 100)
                    icon = "🏆"
                    badge = Colors.BG_GREEN + Colors.BLACK + " 极速 " + Colors.RESET
                elif latency < 100:
                    latency_color = Colors.BRIGHT_GREEN
                    icon = "🎯"
                    badge = Colors.BG_BLUE + Colors.WHITE + " 优秀 " + Colors.RESET
                elif latency < 200:
                    latency_color = Colors.BRIGHT_YELLOW
                    icon = "✓"
                    badge = Colors.BG_YELLOW + Colors.BLACK + " 良好 " + Colors.RESET
                else:
                    latency_color = Colors.BRIGHT_CYAN
                    icon = "•"
                    badge = ""
                
                # 创建延迟条
                latency_bar_width = int((latency / 500) * 20)
                latency_bar = latency_color + "▰" * min(latency_bar_width, 20) + Colors.DIM + "▱" * (20 - min(latency_bar_width, 20)) + Colors.RESET
                
                max_name_width = 30
                truncated_name = UIComponents.truncate_by_width(name, max_name_width)
                display_width = UIComponents.get_display_width(truncated_name)
                padding = ' ' * (max_name_width - display_width)
                
                print(f"  {icon} {truncated_name}{padding} {latency_bar} {latency_color}{latency:.0f}ms{Colors.RESET} {badge}")
            print()
    
    def _render_footer(self):
        """渲染底部信息"""
        runtime = str(datetime.now() - self.start_time).split('.')[0]
        
        # 添加装饰性分隔线
        separator = Colors.gradient_text("─" * 74, (100, 100, 255), (255, 100, 100))
        print("  " + separator)
        
        # 底部信息带图标
        print(f"  {UIComponents.status_icon('shield')} {Colors.DIM}运行时间: {runtime}  |  "
              f"按 {Colors.BRIGHT_YELLOW}Ctrl+C{Colors.DIM} 保存并退出  |  "
              f"自动保存: 每5000个节点{Colors.RESET}")
        print()

# ═══════════════════════════════════════════════════════════════
# 依赖安装
# ═══════════════════════════════════════════════════════════════

def quick_install_deps():
    """快速安装最小依赖"""
    required = ['requests', 'psutil']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"{Colors.BRIGHT_YELLOW}⏳ 安装必需依赖: {', '.join(missing)}...{Colors.RESET}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing + ["--quiet"])
            print(f"{Colors.BRIGHT_GREEN}✅ 依赖安装完成{Colors.RESET}")
            for pkg in missing:
                try:
                    globals()[pkg] = __import__(pkg)
                except:
                    pass
        except:
            print(f"{Colors.BRIGHT_RED}⚠️  依赖安装失败，继续运行...{Colors.RESET}")
    
    return len(missing) == 0

# 先安装依赖
deps_ok = quick_install_deps()

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False

try:
    import math
except:
    import math

# ═══════════════════════════════════════════════════════════════
# 系统资源管理
# ═══════════════════════════════════════════════════════════════

class SystemResourceManager:
    """系统资源管理器"""
    
    @staticmethod
    def get_optimal_thread_count():
        """智能计算最优线程数"""
        try:
            cpu_count = multiprocessing.cpu_count()
            
            if HAS_PSUTIL:
                mem = psutil.virtual_memory()
                mem_available_gb = mem.available / (1024**3)
                max_threads_by_memory = int(mem_available_gb * 1024 / 10)
            else:
                max_threads_by_memory = 50
            
            optimal = min(
                cpu_count * 5,
                max_threads_by_memory,
                100
            )
            
            optimal = max(optimal, 4)
            
            return optimal
            
        except:
            return 10

# ═══════════════════════════════════════════════════════════════
# 可视化节点测速类
# ═══════════════════════════════════════════════════════════════

class VisualNodeTester:
    def __init__(self, config=None):
        optimal_workers = SystemResourceManager.get_optimal_thread_count()
        
        self.config = {
            'timeout': 3,
            'max_workers': optimal_workers,
            'max_latency': 500,
            'batch_size': 1000,
            'max_nodes': 100000,
            'save_interval': 5000,
            'visual_mode': True,  # 可视化模式
            'update_interval': 0.5,  # UI更新间隔
        }
        
        if config:
            self.config.update(config)
        
        self.available_nodes = []
        self.total_nodes = 0
        self.tested_nodes = 0
        self.success_nodes = 0
        self.failed_nodes = 0
        self.start_time = None
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self.actual_workers = 0
        
        # 仪表盘
        self.dashboard = Dashboard()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理中断信号"""
        UIComponents.show_cursor()
        print(f"\n\n{Colors.BRIGHT_YELLOW}⚠️  收到中断信号，正在安全退出...{Colors.RESET}")
        self.stop_flag.set()
        self.save_results(final=True)
        print(f"{Colors.BRIGHT_GREEN}✅ 已保存当前结果{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}📊 测试统计：{Colors.RESET}")
        print(f"    • 总共测试: {self.tested_nodes:,} 个节点")
        print(f"    • 发现可用: {self.success_nodes:,} 个节点")
        print(f"    • 成功率: {(self.success_nodes/max(self.tested_nodes,1)*100):.1f}%")
        sys.exit(0)
    
    def read_subscribe_links(self, filename="subscribe.txt"):
        """读取订阅链接"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return links
        except FileNotFoundError:
            print(f"{Colors.BRIGHT_RED}❌ 找不到文件 {filename}{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}📝 正在创建示例文件 {filename}...{Colors.RESET}")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 添加订阅链接，每行一个\n")
                f.write("# 支持多种格式：vmess://, vless://, trojan://, ss://, hy2://\n")
                f.write("# 也可以直接添加HTTP/HTTPS订阅链接\n")
            return []
    
    def save_valid_subscribe_links(self, links, filename="subscribe.txt"):
        """保存有效的订阅链接"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 有效的订阅链接\n")
                f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for link in links:
                    f.write(f"{link}\n")
            print(f"{Colors.BRIGHT_GREEN}✅ 有效的订阅链接已保存回 {filename}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}❌ 保存有效订阅链接失败: {e}{Colors.RESET}")
    
    def decode_subscribe_fast(self, link):
        """快速解码订阅"""
        nodes = []
        try:
            if link.startswith('http'):
                if HAS_REQUESTS:
                    response = requests.get(link, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    content = response.text
                else:
                    req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        content = response.read().decode('utf-8')
                
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                    nodes = decoded.split('\n')
                except:
                    nodes = content.split('\n')
            else:
                try:
                    decoded = base64.b64decode(link).decode('utf-8')
                    nodes = decoded.split('\n')
                except:
                    nodes = [link]
        except:
            pass
        
        return [n.strip() for n in nodes if n.strip()]
    
    def parse_node_minimal(self, node):
        """最小化节点解析"""
        info = {'raw': node, 'server': '', 'port': 0, 'name': ''}
        
        try:
            if node.startswith('vmess://'):
                encoded = node[8:]
                decoded = base64.b64decode(encoded + '=' * (4 - len(encoded) % 4)).decode('utf-8')
                data = json.loads(decoded)
                info['server'] = data.get('add', '')
                info['port'] = int(data.get('port', 0))
                info['name'] = data.get('ps', '')[:30]
            elif node.startswith(('vless://', 'trojan://', 'ss://', 'hy2://')):
                parsed = urllib.parse.urlparse(node)
                info['server'] = parsed.hostname or ''
                info['port'] = parsed.port or 443
                # 解析节点名称
                if '#' in node:
                    info['name'] = urllib.parse.unquote(node.split('#')[1])[:30]
                else:
                    info['name'] = f"{parsed.scheme}://{info['server']}"[:30]
        except:
            pass
        
        return info
    
    def test_gfw_real_latency(self, host, port, sni=None):
        """通过测试TLS握手延迟来模拟GFW环境下的真实延迟"""
        if not host or not port:
            return None
        
        sni_host = sni if sni else host

        try:
            start_time = time.time()
            
            sock = socket.create_connection((host, port), timeout=self.config['timeout'])
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with context.wrap_socket(sock, server_hostname=sni_host) as ssock:
                latency = (time.time() - start_time) * 1000
                return latency
        except (socket.timeout, ssl.SSLError, ConnectionRefusedError, OSError):
            return None
        except Exception:
            return None
    
    def process_node(self, node):
        """处理单个节点"""
        if self.stop_flag.is_set():
            return None
        
        info = self.parse_node_minimal(node)
        if info['server'] and info['port']:
            latency = self.test_gfw_real_latency(info['server'], info['port'], info.get('sni'))
            
            with self.lock:
                self.tested_nodes += 1
                
                if latency and latency <= self.config['max_latency']:
                    info['latency'] = latency
                    self.success_nodes += 1
                    self.dashboard.add_recent_node(info)
                    return info
                else:
                    self.failed_nodes += 1
        else:
            with self.lock:
                self.tested_nodes += 1
                self.failed_nodes += 1
        
        return None
    
    def ui_update_thread(self):
        """UI更新线程"""
        while not self.stop_flag.is_set():
            with self.lock:
                self.dashboard.update_stats(
                    total=self.total_nodes,
                    tested=self.tested_nodes,
                    success=self.success_nodes,
                    failed=self.failed_nodes,
                    threads=self.actual_workers
                )
            
            if self.config['visual_mode']:
                self.dashboard.render()
            
            time.sleep(self.config['update_interval'])
    
    def save_results(self, final=False):
        """保存结果"""
        if not self.available_nodes:
            return
        
        # 按延迟排序
        self.available_nodes.sort(key=lambda x: x.get('latency', 999999))
        
        filename = 'node.txt' if final else 'node_temp.txt'
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# 可用节点 (共 {len(self.available_nodes)} 个)\n")
                f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 测试统计: 总测试 {self.tested_nodes} 个，成功 {self.success_nodes} 个\n")
                f.write("#" + "="*50 + "\n\n")
                
                # 按延迟分组保存
                groups = [
                    (0, 50, "极速节点 (0-50ms)"),
                    (50, 100, "优质节点 (50-100ms)"),
                    (100, 200, "良好节点 (100-200ms)"),
                    (200, 300, "普通节点 (200-300ms)"),
                    (300, 500, "备用节点 (300-500ms)")
                ]
                
                for min_lat, max_lat, group_name in groups:
                    group_nodes = [n for n in self.available_nodes 
                                   if min_lat <= n.get('latency', 999999) < max_lat]
                    if group_nodes:
                        f.write(f"# {group_name} - {len(group_nodes)} 个\n")
                        f.write("#" + "-"*50 + "\n")
                        for node in group_nodes:
                            f.write(f"# {node.get('name', 'Unknown')} - {node.get('latency', 0):.0f}ms\n")
                            f.write(f"{node['raw']}\n")
                        f.write("\n")
            
            if final:
                print(f"{Colors.BRIGHT_GREEN}✅ 结果已保存到 {filename}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}❌ 保存失败: {e}{Colors.RESET}")
    
    def test_batch(self, nodes):
        """批量测试节点"""
        batch_results = []
        
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            self.actual_workers = self.config['max_workers']
            futures = [executor.submit(self.process_node, node) for node in nodes]
            
            for future in as_completed(futures):
                if self.stop_flag.is_set():
                    break
                
                try:
                    result = future.result(timeout=self.config['timeout'])
                    if result:
                        batch_results.append(result)
                        self.available_nodes.append(result)
                        
                        # 定期保存
                        if len(self.available_nodes) % self.config['save_interval'] == 0:
                            self.save_results(final=False)
                except:
                    pass
        
        return batch_results
    
    def run(self):
        """主运行函数"""
        self.start_time = datetime.now()
        
        # 打印欢迎界面
        self.print_welcome()
        
        # 读取订阅链接
        print(f"{Colors.BRIGHT_CYAN}📋 读取订阅链接...{Colors.RESET}")
        subscribe_links = self.read_subscribe_links()
        
        if not subscribe_links:
            print(f"{Colors.BRIGHT_RED}❌ 没有找到订阅链接！{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}请在 subscribe.txt 文件中添加订阅链接{Colors.RESET}")
            return
        
        print(f"{Colors.BRIGHT_GREEN}✅ 发现 {len(subscribe_links)} 个订阅链接{Colors.RESET}")
        
        # 解析所有节点
        all_nodes = []
        valid_subscribe_links = []
        print(f"{Colors.BRIGHT_CYAN}🔍 解析节点...{Colors.RESET}")
        
        for i, link in enumerate(subscribe_links, 1):
            print(f"  解析订阅 {i}/{len(subscribe_links)}...", end='\r')
            nodes = self.decode_subscribe_fast(link)
            if nodes:
                valid_subscribe_links.append(link)
                all_nodes.extend(nodes)
        
        self.save_valid_subscribe_links(valid_subscribe_links)
        
        # 去重
        all_nodes = list(set(all_nodes))
        self.total_nodes = len(all_nodes)
        
        if self.total_nodes == 0:
            print(f"{Colors.BRIGHT_RED}❌ 没有解析到任何节点！{Colors.RESET}")
            return
        
        print(f"{Colors.BRIGHT_GREEN}✅ 成功解析 {self.total_nodes:,} 个节点{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}⏳ 开始测试，请稍候...{Colors.RESET}\n")
        
        # 启动UI更新线程
        ui_thread = threading.Thread(target=self.ui_update_thread, daemon=True)
        ui_thread.start()
        
        # 分批处理节点
        for i in range(0, len(all_nodes), self.config['batch_size']):
            if self.stop_flag.is_set():
                break
            
            batch = all_nodes[i:i+self.config['batch_size']]
            self.test_batch(batch)
            
            # 内存清理
            if i % 10000 == 0:
                gc.collect()
        
        # 等待所有任务完成
        self.stop_flag.set()
        time.sleep(1)
        
        # 最终保存
        self.save_results(final=True)
        
        # 显示最终统计
        UIComponents.show_cursor()
        UIComponents.clear_screen()
        self._print_final_stats()

    def print_welcome(self):
        """打印欢迎界面"""
        UIComponents.clear_screen()
        
        print()
        print()
        
        # 简洁的标题
        title1 = "Node Speed Tester V1.0"
        title2 = "高性能节点测速工具"
        
        # 使用渐变色显示标题
        gradient_title1 = Colors.gradient_text(title1, (100, 181, 246), (149, 117, 205))
        gradient_title2 = Colors.gradient_text(title2, (149, 117, 205), (100, 181, 246))
        
        # 居中显示标题
        print(f"  {' ' * 25}{gradient_title1}")
        print(f"  {' ' * 27}{gradient_title2}")
        print()
        
        # 简单的分隔线
        print(f"  {Colors.PRIMARY}{'─' * 60}{Colors.RESET}")
        print()
        
        # 功能描述
        features = [
            ("并发测试", "多线程高速测试节点连接性"),
            ("智能筛选", "自动过滤无效节点"),
            ("实时监控", "动态显示测试进度和统计"),
            ("自动保存", "测试结果自动分类保存")
        ]
        
        for name, desc in features:
            print(f"  {Colors.INFO}▸{Colors.RESET} {Colors.BOLD}{name}{Colors.RESET}: {Colors.SECONDARY}{desc}{Colors.RESET}")
        
        print()
        print(f"  {Colors.PRIMARY}{'─' * 60}{Colors.RESET}")
        
        print()
        
        # System info (existing logic)
        print(f"  {UIComponents.status_icon('info')} {Colors.BOLD}系统信息{Colors.RESET}")
        print(f"  {Colors.BRIGHT_WHITE}CPU核心:{Colors.RESET} {multiprocessing.cpu_count()}")
        
        if HAS_PSUTIL:
            mem = psutil.virtual_memory()
            print(f"  {Colors.BRIGHT_WHITE}可用内存:{Colors.RESET} {mem.available / (1024**3):.1f}GB")
        
        print(f"  {Colors.BRIGHT_WHITE}推荐线程:{Colors.RESET} {self.config['max_workers']}")
        print()
        
        # Feature list (existing logic)
        print(f"  {UIComponents.status_icon('star')} {Colors.BOLD}功能特性{Colors.RESET}")
        features = [
            "🎨 炫彩动态界面，实时数据可视化",
            "⚡ 超高速并发测试，智能线程管理",
            "📊 实时性能监控，延迟分布分析",
            "💾 自动保存结果，支持断点续测",
            "🔥 智能节点筛选，自动排序优化"
        ]
        for feature in features:
            print(f"  {feature}")
        print()
        
        time.sleep(2)
    
    def _print_final_stats(self):
        """打印最终统计"""
        print()
        print(Colors.gradient_text("="*74, (0, 255, 255), (255, 0, 255)))
        print()
        print(f"  {UIComponents.status_icon('trophy')} {Colors.BOLD}测试完成！{Colors.RESET}")
        print()
        
        # 统计信息
        runtime = str(datetime.now() - self.start_time).split('.')[0]
        success_rate = (self.success_nodes / max(self.tested_nodes, 1)) * 100
        
        stats = [
            ("测试总数", f"{self.tested_nodes:,}"),
            ("成功节点", f"{self.success_nodes:,}"),
            ("失败节点", f"{self.failed_nodes:,}"),
            ("成功率", f"{success_rate:.1f}%"),
            ("运行时间", runtime),
            ("平均速度", f"{self.tested_nodes / max((datetime.now() - self.start_time).total_seconds(), 1):.1f} 节点/秒")
        ]
        
        for label, value in stats:
            print(f"  {Colors.BRIGHT_WHITE}{label}:{Colors.RESET} {Colors.BRIGHT_CYAN}{value}{Colors.RESET}")
        
        print()
        
        # 显示最优节点
        if self.available_nodes:
            print(f"  {UIComponents.status_icon('star')} {Colors.BOLD}Top 5 最优节点{Colors.RESET}")
            print()
            
            for i, node in enumerate(self.available_nodes[:5], 1):
                latency = node.get('latency', 0)
                name = node.get('name', 'Unknown')
                
                if latency < 50:
                    medal = "🥇"
                    color = Colors.rgb(255, 215, 0)
                elif latency < 100:
                    medal = "🥈"
                    color = Colors.rgb(192, 192, 192)
                else:
                    medal = "🥉"
                    color = Colors.rgb(205, 127, 50)
                
                max_name_width = 40
                truncated_name = UIComponents.truncate_by_width(name, max_name_width)
                display_width = UIComponents.get_display_width(truncated_name)
                padding = ' ' * (max_name_width - display_width)
                
                print(f"  {medal} {i}. {truncated_name}{padding} {color}{latency:.0f}ms{Colors.RESET}")
        
        print()
        print(Colors.gradient_text("="*74, (255, 0, 255), (0, 255, 255)))
        print()
        print(f"  {Colors.BRIGHT_GREEN}✅ 结果已保存到 node.txt{Colors.RESET}")
        print()

# ═══════════════════════════════════════════════════════════════
# 主程序入口
# ═══════════════════════════════════════════════════════════════

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='超高性能节点测速工具 V1.0')
    parser.add_argument('-t', '--timeout', type=int, default=3, help='连接超时时间(秒)')
    parser.add_argument('-w', '--workers', type=int, help='并发线程数')
    parser.add_argument('-m', '--max-latency', type=int, default=500, help='最大延迟(ms)')
    parser.add_argument('--no-visual', action='store_true', help='禁用可视化界面')
    parser.add_argument('-f', '--file', default='subscribe.txt', help='订阅文件路径')
    
    args = parser.parse_args()
    
    # 配置参数
    config = {
        'timeout': args.timeout,
        'max_latency': args.max_latency,
        'visual_mode': not args.no_visual,
    }
    
    if args.workers:
        config['max_workers'] = args.workers
    
    # 创建测试器并运行
    tester = VisualNodeTester(config)
    
    try:
        tester.run()
    except KeyboardInterrupt:
        UIComponents.show_cursor()
        print(f"\n{Colors.BRIGHT_YELLOW}⚠️  用户中断{Colors.RESET}")
    except Exception as e:
        UIComponents.show_cursor()
        print(f"\n{Colors.BRIGHT_RED}❌ 错误: {e}{Colors.RESET}")
    finally:
        UIComponents.show_cursor()

if __name__ == "__main__":
    main()