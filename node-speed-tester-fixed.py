#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 增强版节点测速工具 V2.1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
自动安装pip和依赖 | 美化界面 | 智能测速
"""

import sys
import os
import time
import json
import base64
import socket
import ssl
import argparse
from datetime import datetime
import subprocess
import importlib

# ═══════════════════════════════════════════════════════════════
# PIP 安装检测
# ═══════════════════════════════════════════════════════════════

def ensure_pip():
    """确保pip已安装"""
    try:
        import pip
        return True
    except ImportError:
        print("⚠️  未检测到pip，正在尝试自动安装...")
        print("─" * 50)
        
        # 尝试不同的方法安装pip
        methods = [
            # 方法1: 使用ensurepip
            ([sys.executable, "-m", "ensurepip", "--default-pip"], "使用ensurepip"),
            # 方法2: 使用apt-get (Debian/Ubuntu)
            (["apt-get", "update"], "更新apt源"),
            (["apt-get", "install", "-y", "python3-pip"], "使用apt安装pip"),
            # 方法3: 使用yum (CentOS/RHEL)
            (["yum", "install", "-y", "python3-pip"], "使用yum安装pip"),
            # 方法4: 使用dnf (Fedora)
            (["dnf", "install", "-y", "python3-pip"], "使用dnf安装pip"),
        ]
        
        for cmd, desc in methods:
            try:
                print(f"尝试: {desc}...")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    # 检查pip是否成功安装
                    try:
                        import pip
                        print(f"✅ {desc} 成功!")
                        return True
                    except ImportError:
                        continue
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        # 如果所有方法都失败，提供手动安装指导
        print("\n❌ 自动安装pip失败，请手动安装:")
        print("─" * 50)
        print("📝 Debian/Ubuntu系统:")
        print("   sudo apt-get update")
        print("   sudo apt-get install python3-pip")
        print("\n📝 CentOS/RHEL系统:")
        print("   sudo yum install python3-pip")
        print("\n📝 通用方法:")
        print("   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
        print("   python3 get-pip.py")
        print("─" * 50)
        return False

# ═══════════════════════════════════════════════════════════════
# 依赖检测与自动安装
# ═══════════════════════════════════════════════════════════════

def install_dependencies():
    """自动检测并安装缺失的依赖"""
    # 首先确保pip已安装
    if not ensure_pip():
        print("\n⚠️  由于pip未安装，将以基础模式运行（功能受限）")
        return False
    
    dependencies = {
        'requests': '2.31.0',
        'colorama': '0.4.6',
        'tqdm': '4.66.1',
        'rich': '13.7.0'
    }
    
    print("\n🔍 正在检查依赖...")
    print("─" * 50)
    
    missing_deps = []
    for package, version in dependencies.items():
        try:
            importlib.import_module(package)
            print(f"✅ {package:15} 已安装")
        except ImportError:
            missing_deps.append(f"{package}=={version}")
            print(f"❌ {package:15} 未安装")
    
    if missing_deps:
        print("\n📦 正在自动安装缺失的依赖包...")
        print("─" * 50)
        
        # 尝试升级pip到最新版本
        try:
            print("⏳ 升级pip到最新版本...", end=' ')
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", "pip", "--quiet"
            ])
            print("✅")
        except:
            print("⚠️  (跳过)")
        
        for dep in missing_deps:
            pkg_name = dep.split('==')[0]
            print(f"⏳ 安装 {pkg_name}...", end=' ')
            try:
                # 尝试多个pip源
                sources = [
                    [],  # 默认源
                    ["-i", "https://pypi.org/simple"],  # 官方源
                    ["-i", "https://mirrors.aliyun.com/pypi/simple/"],  # 阿里云源
                    ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"],  # 清华源
                ]
                
                installed = False
                for source in sources:
                    try:
                        cmd = [sys.executable, "-m", "pip", "install", dep, "--quiet"] + source
                        subprocess.check_call(cmd, timeout=60)
                        installed = True
                        break
                    except:
                        continue
                
                if installed:
                    print("✅")
                else:
                    raise Exception("所有源都失败")
                    
            except Exception as e:
                print(f"❌")
                print(f"   安装失败！请手动执行: pip install {dep}")
                # 继续安装其他包，不立即退出
        
        print("\n🔄 正在重新加载模块...")
        time.sleep(1)
        
        # 重新导入
        for package in dependencies.keys():
            try:
                globals()[package] = importlib.import_module(package)
            except ImportError:
                pass
    else:
        print("\n✨ 所有依赖已就绪！")
    
    print("═" * 50)
    time.sleep(0.5)
    return True

# 先安装依赖
dependencies_ok = install_dependencies()

# ═══════════════════════════════════════════════════════════════
# 导入已安装的库（带fallback）
# ═══════════════════════════════════════════════════════════════

try:
    import requests
    from requests.exceptions import RequestException, ConnectionError, Timeout
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  requests库未安装，将使用urllib进行网络请求")

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # 定义空的颜色常量
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ''

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

# Python版本兼容
import urllib.parse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Optional

# ═══════════════════════════════════════════════════════════════
# 美化输出函数
# ═══════════════════════════════════════════════════════════════

def print_banner():
    """显示程序横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                  🚀 节点测速工具 V2.1 🚀                  ║
    ╠══════════════════════════════════════════════════════════╣
    ║  支持自动安装依赖 | 多种测速模式 | 智能筛选              ║
    ╚══════════════════════════════════════════════════════════╝
    """
    
    if HAS_RICH:
        console.print(Panel(banner, style="bold cyan"))
    else:
        print(Fore.CYAN + banner if HAS_COLOR else banner)

def print_info(message, level="info"):
    """美化的信息输出"""
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "loading": "⏳"
    }
    
    colors = {
        "info": Fore.BLUE,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "loading": Fore.CYAN
    }
    
    icon = icons.get(level, "")
    color = colors.get(level, "") if HAS_COLOR else ""
    
    if HAS_RICH and console:
        style_map = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "loading": "cyan"
        }
        console.print(f"{icon} {message}", style=style_map.get(level, ""))
    else:
        print(f"{color}{icon} {message}{Style.RESET_ALL if HAS_COLOR else ''}")

def create_progress_bar(total, desc="Processing"):
    """创建进度条"""
    if HAS_TQDM:
        return tqdm(total=total, desc=desc, ncols=80, 
                   bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
    else:
        # 简单的文字进度提示
        class SimpleProgress:
            def __init__(self, total, desc):
                self.total = total
                self.current = 0
                self.desc = desc
                
            def update(self, n=1):
                self.current += n
                if self.current % max(1, self.total // 20) == 0 or self.current == self.total:
                    percent = (self.current / self.total) * 100
                    print(f"\r{self.desc}: {self.current}/{self.total} ({percent:.1f}%)", end='', flush=True)
            
            def close(self):
                print()  # 换行
        
        return SimpleProgress(total, desc)

# ═══════════════════════════════════════════════════════════════
# 主测速类
# ═══════════════════════════════════════════════════════════════

class NodeSpeedTester:
    def __init__(self, config=None):
        # 默认配置
        self.config = {
            'timeout': 5,
            'max_workers': 50,
            'max_latency': 1000,
            'test_mode': 'standard',
            'output_format': 'txt',
            'save_unavailable': False,
            'ping_count': 3,
            'http_test_timeout': 10,
            'tls_test_host': 'www.google.com',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if config:
            self.config.update(config)
        
        self.available_nodes = []
        self.unavailable_nodes = []
        self.total_nodes = 0
        self.tested_nodes = 0
        self.start_time = None
        self.end_time = None
        self.progress_bar = None
        
        self.stats = {
            'by_type': {},
            'by_country': {},
            'avg_latency': 0,
            'min_latency': float('inf'),
            'max_latency': 0
        }
    
    def read_subscribe_links(self, filename="subscribe.txt"):
        """读取订阅链接文件"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f.readlines() 
                        if line.strip() and not line.strip().startswith('#')]
            return links
        except FileNotFoundError:
            print_info(f"找不到文件 {filename}", "error")
            print_info("正在创建示例文件...", "info")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 在此文件中添加订阅链接，每行一个\n")
                f.write("# 以#开头的行将被忽略\n")
                f.write("# 示例: https://example.com/subscribe\n")
            
            print_info(f"已创建 {filename}，请添加订阅链接后重新运行", "success")
            return []
        except Exception as e:
            print_info(f"读取文件时发生错误: {str(e)}", "error")
            return []
    
    def decode_subscribe_link(self, link, max_retries=3):
        """解码订阅链接"""
        nodes = []
        
        try:
            if link.startswith('http'):
                if HAS_REQUESTS:
                    for attempt in range(max_retries):
                        try:
                            response = requests.get(
                                link, 
                                timeout=self.config['http_test_timeout'],
                                headers={'User-Agent': self.config['user_agent']}
                            )
                            response.raise_for_status()
                            content = response.text
                            
                            try:
                                decoded = base64.b64decode(content).decode('utf-8')
                                nodes = decoded.split('\n')
                            except:
                                nodes = content.split('\n')
                            
                            if nodes:
                                break
                        except Exception as e:
                            if attempt < max_retries - 1:
                                time.sleep(2 ** attempt)
                            else:
                                print_info(f"获取订阅失败: {str(e)}", "warning")
                else:
                    # urllib fallback
                    req = urllib.request.Request(link, headers={'User-Agent': self.config['user_agent']})
                    with urllib.request.urlopen(req, timeout=self.config['http_test_timeout']) as response:
                        content = response.read().decode('utf-8')
                    
                    try:
                        decoded = base64.b64decode(content).decode('utf-8')
                        nodes = decoded.split('\n')
                    except:
                        nodes = content.split('\n')
            else:
                # base64 encoded
                try:
                    decoded = base64.b64decode(link).decode('utf-8')
                    nodes = decoded.split('\n')
                except:
                    nodes = [link]
                    
        except Exception as e:
            print_info(f"解码订阅链接时发生错误: {str(e)}", "error")
            
        return [node.strip() for node in nodes if node.strip()]
    
    def parse_node_info(self, node):
        """解析节点信息"""
        info = {
            'type': '',
            'name': '',
            'server': '',
            'port': 0,
            'raw': node,
            'country': '',
            'network': ''
        }
        
        try:
            if node.startswith('vmess://'):
                info['type'] = 'vmess'
                encoded = node[8:]
                decoded = base64.b64decode(encoded + '=' * (4 - len(encoded) % 4)).decode('utf-8')
                data = json.loads(decoded)
                
                info['name'] = data.get('ps', data.get('add', ''))
                info['server'] = data.get('add', '')
                info['port'] = int(data.get('port', 0))
                
                # 国家识别
                name_lower = info['name'].lower()
                country_map = {
                    ('hk', 'hongkong', '香港'): 'HK',
                    ('jp', 'japan', '日本'): 'JP',
                    ('kr', 'korea', '韩国'): 'KR',
                    ('sg', 'singapore', '新加坡'): 'SG',
                    ('us', 'america', '美国'): 'US',
                    ('tw', 'taiwan', '台湾'): 'TW'
                }
                
                for keywords, code in country_map.items():
                    if any(kw in name_lower or kw in info['name'] for kw in keywords):
                        info['country'] = code
                        break
                        
            elif node.startswith(('vless://', 'trojan://', 'ss://', 'hysteria2://', 'hy2://')):
                protocol_map = {
                    'vless://': 'vless',
                    'trojan://': 'trojan',
                    'ss://': 'shadowsocks',
                    'hysteria2://': 'hysteria2',
                    'hy2://': 'hysteria2'
                }
                
                for prefix, proto in protocol_map.items():
                    if node.startswith(prefix):
                        info['type'] = proto
                        break
                
                parsed = urllib.parse.urlparse(node)
                info['server'] = parsed.hostname or ''
                info['port'] = parsed.port or 443
                info['name'] = urllib.parse.unquote(parsed.fragment or '')
                    
        except Exception as e:
            pass
            
        return info
    
    def test_tcp_latency(self, host, port):
        """测试TCP延迟"""
        if not host or not port:
            return None
            
        latencies = []
        
        for _ in range(self.config['ping_count']):
            try:
                start_time = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.config['timeout'])
                
                result = sock.connect_ex((str(host), int(port)))
                
                if result == 0:
                    latency = (time.time() - start_time) * 1000
                    latencies.append(latency)
                sock.close()
                
            except Exception:
                pass
        
        return sum(latencies) / len(latencies) if latencies else None
    
    def test_tls_handshake(self, host, port):
        """测试TLS握手"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.config['timeout'])
            sock.connect((str(host), int(port)))
            
            secure_sock = context.wrap_socket(sock, server_hostname=self.config['tls_test_host'])
            cipher = secure_sock.cipher()
            secure_sock.close()
            
            return cipher is not None
        except:
            return False
    
    def test_node_availability(self, node_info):
        """测试节点可用性"""
        if not node_info['server'] or not node_info['port']:
            return None, False
        
        latency = self.test_tcp_latency(node_info['server'], node_info['port'])
        if latency is None:
            return None, False
        
        is_available = True
        
        if self.config['test_mode'] in ['standard', 'deep']:
            if node_info['port'] in [443, 2053, 2083, 2087, 2096, 8443]:
                is_available = self.test_tls_handshake(node_info['server'], node_info['port'])
        
        is_available = is_available and latency <= self.config['max_latency']
        
        return latency, is_available
    
    def process_single_node(self, node):
        """处理单个节点"""
        node_info = self.parse_node_info(node)
        latency, is_available = self.test_node_availability(node_info)
        
        self.tested_nodes += 1
        
        # 更新进度条
        if self.progress_bar:
            self.progress_bar.update(1)
        
        # 更新统计
        if node_info['type']:
            self.stats['by_type'][node_info['type']] = self.stats['by_type'].get(node_info['type'], 0) + 1
        
        if node_info['country']:
            self.stats['by_country'][node_info['country']] = self.stats['by_country'].get(node_info['country'], 0) + 1
        
        if latency:
            if self.stats['avg_latency'] == 0:
                self.stats['avg_latency'] = latency
            else:
                self.stats['avg_latency'] = (self.stats['avg_latency'] * (self.tested_nodes - 1) + latency) / self.tested_nodes
            
            self.stats['min_latency'] = min(self.stats['min_latency'], latency)
            self.stats['max_latency'] = max(self.stats['max_latency'], latency)
        
        node_info['latency'] = latency
        return node_info, latency, is_available
    
    def save_results(self):
        """保存测试结果"""
        self.available_nodes.sort(key=lambda x: x.get('latency', float('inf')))
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存TXT
        if self.config['output_format'] in ['txt', 'all']:
            try:
                with open('node.txt', 'w', encoding='utf-8') as f:
                    f.write(f"# 可用节点列表 (共 {len(self.available_nodes)} 个)\n")
                    f.write(f"# 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# 测试模式: {self.config['test_mode']}\n")
                    f.write(f"# 最大延迟: {self.config['max_latency']}ms\n\n")
                    
                    for node in self.available_nodes:
                        f.write(f"{node['raw']}\n")
                
                print_info("已保存可用节点到 node.txt", "success")
            except Exception as e:
                print_info(f"保存TXT文件失败: {str(e)}", "error")
    
    def print_summary(self):
        """打印测试摘要"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
        
        if HAS_RICH and console:
            # 使用Rich创建漂亮的表格
            table = Table(title="📊 测试结果摘要", show_header=True, header_style="bold magenta")
            table.add_column("指标", style="cyan", width=20)
            table.add_column("数值", style="green")
            
            table.add_row("总节点数", str(self.total_nodes))
            table.add_row("可用节点", f"{len(self.available_nodes)} ({len(self.available_nodes)/self.total_nodes*100:.1f}%)")
            table.add_row("不可用节点", str(len(self.unavailable_nodes)))
            table.add_row("测试耗时", f"{duration:.1f}秒")
            
            if self.stats['avg_latency'] > 0:
                table.add_row("平均延迟", f"{self.stats['avg_latency']:.0f}ms")
                if self.stats['min_latency'] != float('inf'):
                    table.add_row("最低延迟", f"{self.stats['min_latency']:.0f}ms")
                if self.stats['max_latency'] > 0:
                    table.add_row("最高延迟", f"{self.stats['max_latency']:.0f}ms")
            
            console.print(table)
            
            # 显示最快节点
            if self.available_nodes:
                fast_table = Table(title="🏆 最快的10个节点", show_header=True, header_style="bold yellow")
                fast_table.add_column("#", style="cyan", width=3)
                fast_table.add_column("节点名称", style="white", width=30)
                fast_table.add_column("地区", style="green", width=5)
                fast_table.add_column("延迟", style="yellow", width=10)
                
                for i, node in enumerate(self.available_nodes[:10], 1):
                    name = node.get('name', '') or f"{node.get('server', '')}:{node.get('port', '')}"
                    country = node.get('country', 'N/A')
                    latency = f"{node.get('latency', 0):.0f}ms" if node.get('latency') else "N/A"
                    fast_table.add_row(str(i), name[:30], country, latency)
                
                console.print(fast_table)
        else:
            # 普通输出
            print("\n" + "═" * 50)
            print("📊 测试完成!")
            print("═" * 50)
            print(f"总节点数: {self.total_nodes}")
            print(f"可用节点: {len(self.available_nodes)} ({len(self.available_nodes)/self.total_nodes*100:.1f}%)")
            print(f"不可用节点: {len(self.unavailable_nodes)}")
            print(f"测试耗时: {duration:.1f}秒")
            
            if self.stats['avg_latency'] > 0:
                print(f"平均延迟: {self.stats['avg_latency']:.0f}ms")
                if self.stats['min_latency'] != float('inf'):
                    print(f"最低延迟: {self.stats['min_latency']:.0f}ms")
                if self.stats['max_latency'] > 0:
                    print(f"最高延迟: {self.stats['max_latency']:.0f}ms")
            
            if self.available_nodes:
                print("\n🏆 最快的10个节点:")
                for i, node in enumerate(self.available_nodes[:10], 1):
                    name = node.get('name', '') or f"{node.get('server', '')}:{node.get('port', '')}"
                    country = f" [{node['country']}]" if node.get('country') else ""
                    latency = f"{node.get('latency', 0):.0f}ms" if node.get('latency') else "N/A"
                    print(f"{i:2d}. {name[:30]:<30}{country} - {latency}")
    
    def run(self):
        """主运行函数"""
        self.start_time = datetime.now()
        
        print_banner()
        print_info(f"Python版本: {sys.version.split()[0]}", "info")
        print_info(f"测试模式: {self.config['test_mode']}", "info")
        
        if not dependencies_ok:
            print_info("运行在基础模式（部分功能可能受限）", "warning")
        
        print("")
        
        # 读取订阅链接
        print_info("正在读取订阅链接...", "loading")
        subscribe_links = self.read_subscribe_links()
        if not subscribe_links:
            print_info("没有找到订阅链接", "error")
            return
        
        print_info(f"找到 {len(subscribe_links)} 个订阅链接", "success")
        
        # 解析所有节点
        all_nodes = []
        for i, link in enumerate(subscribe_links, 1):
            print_info(f"正在解析订阅 {i}/{len(subscribe_links)}...", "loading")
            nodes = self.decode_subscribe_link(link)
            if nodes:
                all_nodes.extend(nodes)
                print_info(f"  获取到 {len(nodes)} 个节点", "success")
        
        self.total_nodes = len(all_nodes)
        if self.total_nodes == 0:
            print_info("没有找到可用的节点", "error")
            return
        
        print_info(f"共解析出 {self.total_nodes} 个节点", "success")
        print_info("开始测速...\n", "loading")
        
        # 创建进度条
        self.progress_bar = create_progress_bar(self.total_nodes, "测速进度")
        
        # 并发测速
        results = []
        
        with ThreadPoolExecutor(max_workers=min(self.config['max_workers'], self.total_nodes)) as executor:
            future_to_node = {
                executor.submit(self.process_single_node, node): node 
                for node in all_nodes
            }
            
            for future in as_completed(future_to_node):
                try:
                    result = future.result(timeout=self.config['timeout'] * 2)
                    results.append(result)
                except Exception:
                    pass
        
        if self.progress_bar:
            self.progress_bar.close()
        
        # 处理结果
        for node_info, latency, is_available in results:
            if is_available and latency is not None:
                self.available_nodes.append(node_info)
            else:
                if self.config['save_unavailable']:
                    self.unavailable_nodes.append(node_info)
        
        self.end_time = datetime.now()
        
        # 保存结果
        if self.available_nodes:
            self.save_results()
        
        # 打印摘要
        self.print_summary()

# ═══════════════════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='🚀 增强版节点测速工具')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='连接超时时间（秒）')
    parser.add_argument('-w', '--workers', type=int, default=50, help='并发线程数')
    parser.add_argument('-m', '--mode', choices=['fast', 'standard', 'deep'], default='standard', 
                       help='测试模式')
    parser.add_argument('-f', '--format', choices=['txt', 'json', 'csv', 'all'], default='txt',
                       help='输出格式')
    parser.add_argument('-l', '--max-latency', type=int, default=1000, help='最大延迟（毫秒）')
    parser.add_argument('--skip-deps', action='store_true', help='跳过依赖检查')
    
    args = parser.parse_args()
    
    config = {
        'timeout': args.timeout,
        'max_workers': args.workers,
        'test_mode': args.mode,
        'output_format': args.format,
        'max_latency': args.max_latency
    }
    
    tester = NodeSpeedTester(config)
    tester.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\n\n程序被用户中断", "warning")
        sys.exit(0)
    except Exception as e:
        print_info(f"\n发生未预期的错误: {str(e)}", "error")
        import traceback
        traceback.print_exc()
        sys.exit(1)
