# 下载后使用

下载完整 ZIP 后，打开 `index.html` 即可浏览。需要重建时，在解压后的根目录运行 `python skill/scripts/rebuild.py`，使用 Python 3.10–3.14。只复制 `skill/` 会缺少模板。

从 `design-tokens.json` 的 `themes.<ID>.<mode>` 读取颜色。主按钮底色用 `accent`，按钮文字用 `on_accent`；普通背景上的文字操作用 `accent_text`：

```css
.action { background: var(--accent); color: var(--on-accent); }
.action-link { color: var(--accent-text); }
```

接入原生 App 时，将这些字段映射到系统动态颜色，并按实际字号、安全区和屏幕尺寸检查布局。[React Native 接入说明](native-consumption.md)提供了现有适配器的用法。

页面里的组件只用于外观参考和本地交互演示。Widget 与 Duo 容器也是 HTML 示意，实际平台功能需要另行实现。演示数据只保存在当前页面，没有服务端或用户数据库。

图标和代码的许可见 `LICENSE`。ZIP 不包含字体；Apple 字体、SF Symbols 等系统资源不属于本库的 MIT 授权内容。
