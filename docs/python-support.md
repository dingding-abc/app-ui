# Python 文件与版本

构建使用 Python 标准库，不需要 `pip install`。支持范围为 Python 3.10–3.14；`.python-version` 的 3.12 是默认开发版本，不要求安装 3.12.14。仅浏览已有 HTML 时不需要 Python。

## 完整检查

在仓库根目录运行：

```sh
python skill/scripts/check_all.py
```

检查先复制项目到临时目录，再逐个编译、执行辅助模块和生成器，运行主题生成、静态检查、回归和离线包重建。检查结束后清理临时目录，不改变当前项目的主题配置和生成页。任一命令失败都会以非零状态退出并显示对应文件。

三个 JavaScript 检查脚本和原生 Token 测试需要 Node.js；可以用 `--node PATH` 指定。没有 Node.js 时可用 `--python-only`，结果会列出跳过的检查，不记为完整通过。本次 Node.js 版本为 24.19.0。

## 文件清单

当前维护 26 个 Python 文件。辅助模块不提供独立命令，直接执行时只加载定义；它们的实际功能由生成器和回归测试调用。

| 文件 | 用途 |
| --- | --- |
| `build.py` | 基础样张 |
| `build_d.py` | 紫硝子基础样张 |
| `build_d_ext.py` | 紫硝子扩展样张 |
| `build_devices.py` | 设备尺寸样张 |
| `build_ext.py` | 扩展样张与共享页面 |
| `adaptive_demo.py` | 自适应容器页面模块 |
| `catalog_pages.py` | 组件索引和下载页面模块 |
| `component_catalog.py` | HTML 交互演示模块 |
| `design_tokens.py` | 语义颜色和对比度计算模块 |
| `hour_picker.py` | 时间滚轮模块 |
| `shape_tokens.py` | 控件形状配置 |
| `ui_contract.py` | 主要组件排版、间距与顶部提示权威契约 |
| `site_support.py` | 导航、总览及规范页面模块 |
| `theme_registry.py` | 主题配置读取与校验模块 |
| `widget_spec.py` | Widget 外观与说明模块 |
| `skill/scripts/create_theme.py` | 登记新主题；`--dry-run` 只检查配置 |
| `skill/scripts/rebuild.py` | 按顺序运行生成器并导出 Token |
| `skill/scripts/validate.py` | 检查颜色、生成内容和本地链接 |
| `skill/scripts/package_release.py` | 生成离线 ZIP 和摘要 |
| `skill/scripts/test_system.py` | 新主题、输入边界和重复构建回归 |
| `skill/scripts/test_release.py` | 归档摘要、离线链接与换目录重建 |
| `skill/scripts/test_browser_scripts.py` | 页面内 JavaScript 语法检查，需要 Node.js |
| `skill/scripts/test_picker_state.py` | 时间滚轮状态检查，需要 Node.js |
| `skill/scripts/test_adaptive_layout.py` | 自适应布局状态检查，需要 Node.js |
| `skill/scripts/preview_stress.py` | 从真实组件源生成116个窄屏/四模式/大字压力场景 |
| `skill/scripts/check_all.py` | 上述文件的统一检查入口 |

`skill/archive/`、`skill/scripts/old/` 是原工作区中的历史备份，不属于当前源码，不上传、不打包，也不在此清单中。

## 实测记录

2026-10-07 在 Windows 上使用同一条 `check_all.py` 命令逐版本执行：

| Python | 24 个 Python 文件 | 构建、回归、打包和 JavaScript 检查 |
| --- | --- | --- |
| 3.10.21 | 通过 | 通过 |
| 3.11.16 | 通过 | 通过 |
| 3.12.14 | 通过 | 通过 |
| 3.13.15 | 通过 | 通过 |
| 3.14.7 | 通过 | 通过 |

表中的补丁号用于记录实测环境，不是安装要求。此前 `build_ext.py` 中两处字符串写法依赖 Python 3.12 语法，已改成较早版本也能执行的写法。

详细结果见 [验收记录](../ACCEPTANCE_REPORT.md)。本次没有测试 Linux/macOS；版本检查不代替浏览器或原生 iOS 验证。

2026-10-10 UI一致性修订增加两份Python源；本轮实测Python3.12.14，历史五版本24文件记录仅对应当时版本，不能作为新增文件已跨版本测试的证据。
