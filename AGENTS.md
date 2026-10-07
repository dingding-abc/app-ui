# 项目约定

- 项目事实与执行入口见 `PROJECT.md`，验收标准见 `ACCEPTANCE.md`。
- 本项目是 iPhone UI 规范与 HTML 样张生成器，不是可运行的 iOS App。不要将静态检查、浏览器渲染或历史截图报告为真机通过。
- 从生成器修改并重建；不要手改产出的 HTML 或 `design-tokens.json`。
- `design_tokens.py` 是语义颜色计算来源；`themes.json` 是新增色系入口。已有 A–F 主题保留各自种子色。
- 使用 `skill/SKILL.md` 的当前流程。`skill/archive/` 与 `skill/scripts/old/` 仅作历史留存，不作为有效规则或测试入口。
- 用 Python 标准库构建；保持当前 Python 3.12 系列。项目现位于 Windows 路径，当前环境无 WSL。迁移到 WSL 后使用该环境的独立 Python，不共享缓存。
- 颜色或生成逻辑变更运行 `rebuild.py`、`validate.py`、`test_system.py`；纯文案修改运行构建及静态验收即可。浏览器与原生验收单独记录。
- 不用“CSS 类计数一致”替代组件行为检查，不把新增主题绑定到一个未占用的色相，不依赖归档脚本的硬编码旧路径。
