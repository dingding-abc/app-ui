# App UI

整理了一些 iPhone 界面样式：按钮、表单、列表、日历、弹窗和小组件。可以直接看 HTML 页面，也可以用附带的 Python 脚本生成自己的配色。

[在线预览](https://dingding-abc.github.io/app-ui/) · [下载离线包](dist/jp-min-ui-kit-5.1.zip) · [Skill](skill/SKILL.md)

## 样式预览

目前有 7 套配色。这里放两套，其余在[预览页](https://dingding-abc.github.io/app-ui/)里。

### 余白

米白底、棕色按钮，适合笔记、阅读或日程类界面。

![余白的按钮、表单和列表](docs/previews/yohaku.jpg)

[浅色](https://dingding-abc.github.io/app-ui/a-yohaku.html) / [深色及扩展组件](https://dingding-abc.github.io/app-ui/a-yohaku-ext.html)

### 晴日

蓝色按钮，搭配珊瑚色和黄色分类。组件与余白相同，可以对照着看配色的区别。

![晴日的按钮、表单和列表](docs/previews/sunny-day.jpg)

[浅色](https://dingding-abc.github.io/app-ui/theme-sunny-day.html) / [深色及扩展组件](https://dingding-abc.github.io/app-ui/theme-sunny-day-ext.html)

全部 7 套主题的图片已更新，含基础与深色扩展完整页：[查看图片目录](docs/previews/README.md)。

## 本地使用

下载后打开 `index.html` 就能浏览，不需要安装依赖。修改样式或新增配色时，使用 **Python 3.10–3.14**，无需固定到 3.12.14。`.python-version` 中的 3.12 只是默认开发版本。

```sh
git clone https://github.com/dingding-abc/app-ui.git
cd app-ui
python skill/scripts/rebuild.py
python skill/scripts/validate.py
```

生成新配色：

```sh
python skill/scripts/create_theme.py --id mist-blue --name 雾蓝 --accent "#6C8FA8"
python skill/scripts/rebuild.py
python skill/scripts/validate.py
```

颜色配置在 `themes.json`，组件模板在根目录的 Python 文件中。HTML 和 `design-tokens.json` 由脚本生成，修改它们会在下次构建时被覆盖。

## Skill

[skill/SKILL.md](skill/SKILL.md) 说明了如何选用已有样式、增加配色和修改组件。使用时让编程助手读取这个文件，例如：

```text
请按 skill/SKILL.md，给笔记 App 新增一套雾蓝配色，主色 #6C8FA8。
保留其他主题，生成页面后运行检查。
```

请保留整个仓库；只复制 `skill/` 会缺少生成页面所需的模板。

## 交互规范

日期／时间弹层、滚动隔离、键盘避让和数字输入对齐见[交互说明](docs/interaction-standard.md)及[在线规范](https://dingding-abc.github.io/app-ui/standards.html#picker-presentation)。HTML 滚轮演示展示展开内容，接入 App 后仍须验证系统键盘、真实手势和焦点恢复。

## 检查

```sh
python skill/scripts/check_all.py
```

这条命令在临时副本中检查所有有效 Python 文件，并运行构建、主题生成、打包和回归测试。完整检查还需要 Node.js；只检查 Python 部分可加 `--python-only`，跳过项会明确列出。

[Python 版本与文件清单](docs/python-support.md) · [检查记录](ACCEPTANCE_REPORT.md)

## 其他文件

| 内容 | 位置 |
| --- | --- |
| 组件范围、配色及用法 | [式样说明](docs/style-guide.md) |
| 字号、间距、按钮及交互规则 | [设计规范](https://dingding-abc.github.io/app-ui/standards.html) |
| 四模式颜色数据 | [design-tokens.json](design-tokens.json) |
| 原生颜色适配器与 React Native 示例 | [native/](native/)、[接入说明](docs/native-consumption.md) |
| 生成器与维护命令 | [PROJECT.md](PROJECT.md) |

这里提供的是 HTML 样张和本地交互演示，不包含完整 iOS App。接入实际项目时，还需要实现业务功能并检查真机效果。

[MIT License](LICENSE)。不包含 Apple 字体或 SF Symbols 文件。
