# 使用 curl
```curl -s https://raw.githubusercontent.com/Fmmx/nodespeedtest/refs/heads/main/node-speed-tester-fixed.py | python3```

# 或使用 wget
```wget -qO- https://raw.githubusercontent.com/Fmmx/nodespeedtest/refs/heads/main/node-speed-tester-fixed.py | python3```


## 🔧 主要更新内容：

### 1. **自动安装pip** 
- 检测系统是否安装pip，如果没有会尝试多种方法自动安装
- 支持 Debian/Ubuntu (apt-get)、CentOS/RHEL (yum)、Fedora (dnf) 等系统
- 如果自动安装失败，提供详细的手动安装指导

### 2. **更智能的依赖安装**
- 尝试多个pip源（官方源、阿里云源、清华源）以提高成功率
- 即使部分依赖安装失败，程序也能以基础模式运行
- 自动升级pip到最新版本

### 3. **更好的错误处理**
- 所有关键功能都有fallback机制
- 没有安装美化库时，使用简单文本输出
- 没有进度条库时，使用简单的百分比提示

### 4. **兼容性改进**
- 移除了Python 2的兼容代码（因为Python 3专用）
- 更好的异常处理和错误提示

## 📝 使用方法：

1. **首次运行（自动安装依赖）：**
```bash
python3 node-speed-tester-fixed.py
```

2. **如果系统没有pip，脚本会提示手动安装：**
```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install python3-pip

# CentOS/RHEL
sudo yum install python3-pip

# 或使用通用方法
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

3. **跳过依赖检查（如果已安装）：**
```bash
python3 node-speed-tester-fixed.py --skip-deps
```

4. **其他参数：**
```bash
# 设置超时时间
python3 node-speed-tester-fixed.py -t 10

# 设置并发数
python3 node-speed-tester-fixed.py -w 100

# 快速模式
python3 node-speed-tester-fixed.py -m fast
```

现在脚本应该能够正确处理pip未安装的情况，并提供清晰的解决方案。即使在最基础的环境中也能运行（虽然功能会受限）。
