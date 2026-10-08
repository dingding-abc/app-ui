# 项目档案

## 目的与边界

维护日式简约 iPhone UI 规范，供设计者及后续 iOS 实现复用。交付 HTML 样张、图标目录、语义颜色和验收要求。无服务端、数据库、认证或用户数据处理。GitHub 仓库为 `dingding-abc/app-ui`，静态预览使用 GitHub Pages；发布范围与入口见根目录 `README.md`。

当前包含 A–F 六套主题：余白、藍染、若竹、紫硝子、青磁、桜色，另加一套三色“晴日”。每套有基础与扩展样张；全局入口为 `index.html`，共享页包括 `standards.html`、`icons.html`、`devices.html`、`components.html`、`adaptive.html` 和 `reuse.html`。

## 文件对应关系

| 内容 | 来源 | 产物 |
| --- | --- | --- |
| 原有色板 | `build.py` / `build_ext.py` / `build_d.py` | 各主题页面 |
| 新增色系 | `themes.json`，由 `theme_registry.py` 校验 | 自动加入所有共享页面 |
| 颜色语义与对比度 | `design_tokens.py` | `design-tokens.json` 与各页 CSS |
| 共用组件 | `build.py`、`build_ext.py` | 基础与扩展组件 |
| 小时/分钟滚轮契约、外观与演示交互 | `hour_picker.py` | 各主题 `#hour-picker` / `#time-picker`，导出 `components.hour_picker` / `components.time_picker` |
| 按钮形状 / WidgetKit标准与样张 | `shape_tokens.py` / `widget_spec.py` | 各主题 `#widgetkit`、规范页、导出 `components.button_shape` / `components.widgetkit` |
| 全局导航、规范与页面壳 | `site_support.py` | 总览、规范及共用 CSS |
| 图标 | `build.py` / `build_ext.py`，分类目录 `CATS` | `icons.html` |
| 可操作 HTML 演示 | `component_catalog.py` | 主题基础、扩展页及 `components.html` |
| Duo 容器压力示意 | `adaptive_demo.py` | `adaptive.html` |
| 离线归档 | `skill/scripts/package_release.py` | `dist/jp-min-ui-kit-5.1.zip` 与摘要 |
| 验收定义 / 实际结果 | `ACCEPTANCE.md` / `acceptance-results.json` | `ACCEPTANCE_REPORT.md` |

构建顺序由 `skill/scripts/rebuild.py` 管理：基础 → D 基础 → D 扩展 → 设备 → 扩展与共享页 → Token 导出。生成器之间是 Python 调用契约，不涉及跨进程业务 API。深色 HC 不允许回退到浅色。

## 环境与命令

命令均在项目根目录运行。支持 Python 3.10–3.14，构建只用标准库。`.python-version` 的 3.12 是供版本管理工具选择的默认版本，不要求 3.12.14。实际测试版本和各 Python 文件的用途见 `docs/python-support.md`。Windows 或 WSL 使用各自环境中的 Python。

```sh
python skill/scripts/check_all.py
```

上述命令在临时副本中执行全部检查，不改当前主题或页面。完整检查需要 Node.js；`--python-only` 会明确跳过 JavaScript 检查。以下为单项入口：

```sh
python skill/scripts/rebuild.py
python skill/scripts/validate.py
python skill/scripts/test_system.py
python skill/scripts/package_release.py
python skill/scripts/test_release.py
python skill/scripts/test_adaptive_layout.py
python skill/scripts/test_browser_scripts.py
python skill/scripts/test_picker_state.py
node --test native/test-tokens.cjs
```

```sh
python skill/scripts/create_theme.py --id mist-blue --name 雾蓝 --accent "#6C8FA8" --dry-run
python skill/scripts/create_theme.py --id mist-blue --name 雾蓝 --accent "#6C8FA8"
python skill/scripts/rebuild.py
python skill/scripts/validate.py
```

同一色系 ID 已存在时默认失败，确认是更新该主题才加 `--replace`。主色须为六位十六进制；文字描述或 HTML 不能作为颜色。可用 `--dark-accent` 固定深色品牌色；`--material paper|glass` 选择 HTML 材质示意，二者独立。自然语言色系由 skill 先转换为明确颜色并说明推断。

## 兼容与限制

2026-10-07 GitHub 整理：保持本项目目录作为仓库根目录，保留全部主题，README 和网页总览精选余白与晴日。式样内容见 `docs/style-guide.md`，实际截图与更新方法见 `docs/previews/`。`.gitignore` 排除本地归档、日志、缓存和临时发布工具；`dist/` 仅保留页面链接的离线 ZIP 及摘要。源码提交前先重建、验收、更新截图（涉及展示时），再打包和检查；提交全部相应产物，避免源码、截图和下载包漂移。Pages 使用 `main` 分支根目录及 `.nojekyll`，无需额外构建依赖。JavaScript 检查本次使用 Node.js 24.19.0，Python 版本来源保持 `.python-version`。

时间滚轮状态检查：`python skill/scripts/test_picker_state.py --node <Node可执行文件路径>`。这是额外的JS语法与纯状态测试，使用本机已有Node，不启动浏览器；标准构建仍只需要Python。结果记录于 `picker-state-results.log`，不代表触控或原生验收。

原有主题文件名保持不变。新增文件为 `theme-<id>.html` / `theme-<id>-ext.html`。当前图标 169 枚，设备尺寸场景每主题四组；数量变化由生成器和验收脚本共同维护。Duo 页的尺寸、折线、安全区和操作按钮对齐均为 HTML 可调示意，不宣称官方硬件尺寸或原生姿态能力。空间不足时示意切为单侧，极端参数无法容纳 44px 操作会明确提示。

HTML 的 px 是样张逻辑尺寸，不是原生字号承诺。`--dt-scale` 是比例压力演示；原生使用系统 Text Style。iOS 最低支持版本须由具体 App 确认，玻璃材质在支持版本使用原生组件，旧系统采用实色回退。当前没有 SwiftUI 工程，JSON 导出不等于 SwiftUI 组件交付。

2026-09-28 已在浏览器实际验证开关、表单错误与成功反馈、弹窗 Escape 后焦点恢复，以及自适应场景切换后草稿保留。折叠参数 280px 宽、左右安全区各 60px、折线 20px 时明确提示无法容纳；680px 宽、左安全区 120px、右安全区 0、折线 20px 时，按钮与文本框的实际矩形均未跨越中线。下载入口可取得 ZIP，摘要核对一致。上述是所列浏览器行为和布局场景的证据，不代表所有视口、四模式、大字号或触控均已验收。原生 iOS、真实 Duo 姿态、VoiceOver 与系统 Dynamic Type 尚未验证；历史截图位于 `skill/archive/`，不作本轮证据。

## 2026-10-08 交互规范补充

日期／时间独立弹层、手势隔离、停稳响应、单一表单键盘避让及单行数字居中纳入通用标准；入口为 `docs/interaction-standard.md`、`standards.html#picker-presentation`。导出新增 `components.picker_presentation` 和 `components.form_interaction`，分别由 `hour_picker.py`、`component_catalog.py` 维护，静态验收检查源与导出一致。现有分钟默认步进 1、主题和业务边界不变；展开内容演示不代表完整原生弹层。
