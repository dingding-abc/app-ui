# 复用与边界

下载完整 ZIP 后，打开 `index.html` 浏览；在解压后的根目录运行 Python 3.12 的 `skill/scripts/rebuild.py` 重建。仅复制 `skill/` 无法构建。

颜色以 `design-tokens.json` 的 `themes.<ID>.<mode>` 为权威。网页可将 `accent` 用于按钮填充、`on_accent` 用于按钮文字；正文背景上的文字操作用 `accent_text`。例如：

```css
.action { background: var(--accent); color: var(--on-accent); }
.action-link { color: var(--accent-text); }
```

原生项目需将这些语义角色映射到系统动态颜色，并用实际 size class、安全区和系统无障碍设置验收。这里的 HTML 是规范及交互演示，不是 SwiftUI 或 WidgetKit 组件包；Duo 容器尺寸只用于压力演示。图标 SVG 如需抽取，应检查项目许可及目标平台的资产规则，不将 Apple 字体、SF Symbols 或设备图形视为本库 MIT 资产。项目使用系统字体栈，ZIP 不打包字体。

本地演示没有服务端与用户数据存储。自愿支持信息尚无真实微信收款码，所以不展示二维码或收款链接；使用、反馈和贡献同样是支持。
