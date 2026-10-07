"""Generated component inventory and offline download entry."""
from html import escape
from site_support import all_themes, prepare_page
from component_catalog import CONTRACT

def components_page():
    rows=''.join(f'<tr><td>{escape(t["jp"])}</td><td><a href="{t["file"]}#components-light">浅色交互</a></td><td><a href="{t["file"].replace(".html","-ext.html")}#components-dark">深色交互</a></td></tr>' for t in all_themes())
    controls='、'.join(CONTRACT['controls'])
    content=f'''<h1>组件索引</h1><p>基础及扩展样张包含按钮、表单、列表、日历、Sheet、Alert、空／离线状态、引导、图表、小时与分钟滚轮及 WidgetKit 外观。可操作的 HTML 演示包括：{controls}。</p><p>基础页面展示浅色，扩展页面展示深色；系统增强对比度偏好切换到各自 HC Token。既有外观样张仍只表示静态规范，不能按类名计数视作可交互组件。原生 SwiftUI / WidgetKit 实现待项目接入。</p><div class="kit-table-wrap"><table><thead><tr><th>主题</th><th>浅色演示</th><th>深色演示</th></tr></thead><tbody>{rows}</tbody></table></div><h2>行为边界</h2><p>选择控件使用原生 HTML 输入语义；禁用项不可修改。弹窗支持 Esc 和取消恢复焦点，选择 Sheet 在保存前只保留暂选值。搜索、加载及进度均是固定的本地演示数据；失败明确显示并可重试。</p>'''
    html='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>组件索引</title><style>body{margin:0;background:#F1EEE8;color:#2A2723;font-family:system-ui,sans-serif}a{color:#654631}</style></head><body><div class="board"><main class="kit-doc">'+content+'</main></div></body></html>'
    return prepare_page(html,'components.html')

def reuse_page():
    content='''<h1>复用与下载</h1><p>下载完整源码、HTML 预览、语义 Token 和图标目录。归档包含 MIT 许可与 SHA256 文件清单；解压后打开 <code>index.html</code>，在根目录用 Python 3.10–3.14 执行 <code>python skill/scripts/rebuild.py</code> 可重建。无需第三方依赖。</p><p><a href="dist/jp-min-ui-kit-5.1.zip" download>下载完整离线 ZIP</a> · <a href="dist/jp-min-ui-kit-5.1.zip.sha256" download>下载 ZIP SHA256</a> · <a href="LICENSE">查看 MIT 许可</a> · <a href="docs/reuse-guide.md">阅读复用指南</a></p><p>网页调用语义颜色时，主按钮使用 <code>accent / on_accent</code>，背景上的文字操作使用 <code>accent_text</code>。原生应用需另行映射系统动态颜色、安全区和无障碍行为。此包是 HTML 规范及可操作演示，不是可安装的 SwiftUI、WidgetKit 或 React Native 组件库。</p><p>源码采用 MIT 许可。下载包不包含系统字体或 SF Symbols 文件。</p>'''
    html='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>复用与下载</title><style>body{margin:0;background:#F1EEE8;color:#2A2723;font-family:system-ui,sans-serif}a{color:#654631}</style></head><body><div class="board"><main class="kit-doc">'+content+'</main></div></body></html>'
    return prepare_page(html,'reuse.html')
