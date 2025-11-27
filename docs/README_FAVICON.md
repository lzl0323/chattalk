# 如何生成 favicon.ico

## 🚀 最简单的方法（推荐）

### 在线转换（无需安装任何工具）

1. **访问**: https://favicon.io/favicon-converter/
2. **上传**: `favicon.svg` 或 `favicon-simple.svg`
3. **下载**: 生成的 `favicon.ico`
4. **放置**: 将文件放到 `frontend/public/` 目录

完成！🎉

---

## 🐍 使用 Python 脚本生成

### 方法 1: 运行生成脚本

```bash
# 1. 安装依赖
pip install Pillow

# 2. 运行脚本
cd frontend/public
python generate_favicon.py
```

这将自动生成包含 16x16, 32x32, 48x48 三种尺寸的 `favicon.ico`

### 方法 2: 从 SVG 转换（需要额外工具）

```bash
# 安装 cairosvg 和 Pillow
pip install cairosvg Pillow

# 转换
python -c "
from cairosvg import svg2png
from PIL import Image
import io

# 读取 SVG
with open('favicon.svg', 'rb') as f:
    svg_data = f.read()

# 转换为不同尺寸的 PNG
sizes = [16, 32, 48]
images = []
for size in sizes:
    png_data = svg2png(bytestring=svg_data, output_width=size, output_height=size)
    images.append(Image.open(io.BytesIO(png_data)))

# 保存为 ICO
images[0].save('favicon.ico', format='ICO', 
               sizes=[(img.width, img.height) for img in images],
               append_images=images[1:])
print('✓ 生成成功!')
"
```

---

## 🌐 其他在线工具

1. **RealFaviconGenerator** (最专业)
   - https://realfavicongenerator.net/
   - 生成所有平台的图标

2. **CloudConvert**
   - https://cloudconvert.com/svg-to-ico
   - 批量转换

3. **Convertio**
   - https://convertio.co/zh/svg-ico/
   - 支持多种格式

---

## ✅ 验证图标

生成后，检查文件：

```bash
# Windows
dir favicon.ico

# Linux/Mac
ls -lh favicon.ico

# 应该显示文件存在且大小合理（通常 1-5KB）
```

启动服务器测试：

```bash
npm run dev
```

打开 http://localhost:5173，查看浏览器标签页图标。

**提示**: 如果看不到，按 `Ctrl+Shift+Delete` 清除浏览器缓存。

---

## 📁 最终文件结构

```
frontend/public/
├── favicon.ico           ← 生成这个
├── favicon.svg           ✓ 已有
├── favicon-simple.svg    ✓ 已有
├── generate_favicon.py   ✓ 已有
└── FAVICON_GUIDE.md      ✓ 已有
```

---

需要帮助？查看 `FAVICON_GUIDE.md` 获取更多信息。
