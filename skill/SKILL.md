---
name: jp-min-ui-build
description: 复用和维护本仓库的日式简约 iPhone UI 式样，选择现有主题或按指定色系生成四模式 HTML 样张、语义 Token 和配套说明。用于本项目的式样选择、主题生成与修改，不代替原生 App 实现或真机验收。
metadata:
  emoji: 🎨
---

# 日式简约 iPhone UI · v5

## 工作范围与入口

这是仓库内 skill，注册名为 `jp-min-ui-build`，入口文件为 `skill/SKILL.md`。项目根为本文件的父目录上一层，应包含 `build.py`、`design_tokens.py`、`theme_registry.py`。迁移时携带整个项目；`create_theme.py`、`rebuild.py`、`validate.py` 支持 `--project` 显式指定实际项目，其他入口随完整仓库运行。单独复制 skill 文件夹不包含完整模板，也不等于安装了可独立使用的全局 skill。

先读项目 `AGENTS.md`、`PROJECT.md` 与 `ACCEPTANCE.md`。只修改用户请求涉及的内容；保持现有主题和文件名。当前自然语言接口示例：

- “用这个 skill 做一套雾蓝色 UI，主色 #6C8FA8，用于阅读 App。”
- “生成奶油黄配色，浅色按钮保留柔和感，文字必须清楚。”
- “将现有桜色应用到新的 App，沿用组件规范。”

## 选择与复用已有式样

用户只要求选风格、整理展示或复用时，不必创建新主题。阅读 [式样内容说明](../docs/style-guide.md)，从 `index.html` 进入样张。当前对外精选「余白」（Token ID `A`，暖纸与焦茶）和「晴日」（Token ID `SUNNY-DAY`，配置 ID `sunny-day`，蓝、珊瑚与暖黄）；这只是展示选择，不限制其他主题。

交付应说明主题、适用场景、基础/扩展页面和可复用组件。颜色取自 `design-tokens.json` 的主题四模式；修改颜色仍从权威生成源进行。静态画板、可操作 HTML 区域、原生接入示例各自说明范围。展示截图应来自实际生成页；样张相关内容改变时更新截图，截图不能充当交互或真机验收。

## 核心设计规则

- 保留纸感底色、克制线条、清晰层级与适度留白。主题决定色彩性格；组件语义、文字用途和交互习惯保持一致。不同业务可以使用不同页面布局。
- 不要求新主题占用独一无二的色相，也不把某种颜色解释成“护眼”等医学效果。
- 配色与材质独立。`paper` 为默认；`glass` 仅为 HTML 导航材质示意，原生效果使用系统组件并另行验收。
- 品牌填充 `accent` 与可读的 `accent_text`、`accent_ui` 分离。浅品牌色不能直接作为浅底功能文字。
- 颜色全部经 `design_tokens.py` 求解，四模式分别验收。不能以缺失深色HC为由回退到浅色，不吞掉失败。
- 通用图标保持24网格与currentColor；原生Tab可使用系统填充变体。状态栏图形与图标库资源分别管理。
- HTML缩放比例仅作排版压力演示。iOS使用系统Text Style、实际安全区与可访问的交互控件。
- WidgetKit桌面/锁屏小组件按 [WidgetKit与按钮形状契约](references/widgetkit.md) 生成。外框由系统管理，内部容器圆角协调；App与Widget的独立文字按钮统一胶囊，图标按钮圆形。色系不改变按钮形状；时间滚轮属于App内组件。
- 时间滚动选择复用 `hour_picker.py`，并读取 [小时与分钟选择契约](references/hour-picker.md)。提供仅小时和小时＋分钟两种样张；小时0–23、分钟0–59，默认分钟步进1。双列共同确认/取消，首尾循环但不跨列进位，不静默取整。时长与12小时制另定语义。所有新色系自动继承两种组件的四模式样张。

## 按指定色系生成

1. 明确主色、主题名/ID、用途；若用户给出HEX则准确保留为常规模式品牌填充。只给颜色名称或氛围时，选出具体HEX并说明这是本次设计取值，不把推断写成用户既定选择。除非歧义影响品牌含义，否则继续生成，不反复确认。
2. 读取 [色系与组件契约](references/theme-contract.md)。新建使用独立ID，更新已有自定义主题才用`--replace`。不要覆盖A–F文件来实现新增。
3. 在项目根运行（调用当前环境的Python 3.12）：

```sh
python skill/scripts/create_theme.py --id mist-blue --name 雾蓝 --accent "#6C8FA8" --dry-run
python skill/scripts/create_theme.py --id mist-blue --name 雾蓝 --accent "#6C8FA8"
python skill/scripts/rebuild.py
python skill/scripts/validate.py
```

可选：`--dark-accent "#A0BDCF"`、`--auxiliary "#F26B5B"`、`--tertiary "#F4C84A"`、`--material glass`、`--description "低饱和雾蓝，适合安静阅读。"`。`--dry-run`不写入。生成脚本只登记配置；构建与验收是后续必要步骤，任一步失败不得报告完成。

4. 检查新增主题的基础/扩展页、主页入口、图标对照与4个设备尺寸样张，核对`design-tokens.json`。生成器按注册表自动接入，不手工维护主题数量。
5. 在获准的浏览器环境进行视觉检查：长文案、浅深HC、透明背景、放大字号、滚动到底的主要操作。受工具/安全策略限制时如实记录“未验证”，不可借助替代通道绕过限制。
6. 交付主色、生成页入口、自动验收结果和待验证事项。不要把HTML演示报告为原生App。

## 修改现有组件或生成逻辑

先读涉及的生成器，备份将改的源文件或使用版本控制；修改源而非产物。`build.py`处理共用基础组件，`build_ext.py`处理扩展与图标，`build_d*.py`保留D专属玻璃展示，`build_devices.py`处理尺寸样张，`site_support.py`处理共享规范与导航。

颜色算法、注册表或构建流程变更后：

```sh
python skill/scripts/rebuild.py
python skill/scripts/validate.py
python skill/scripts/test_system.py
```

测试会在临时副本生成新主题并检查重复构建，不改正式注册表。静态脚本不测浏览器计算样式；浏览器、原生验证结果各自记录，不能互相替代。`acceptance-results.json`由静态验收刷新；同步更新`ACCEPTANCE_REPORT.md`。

## 有效资源

- [色系与组件契约](references/theme-contract.md)：添加色系、修改语义颜色、材质或导出结构时读取。
- [WidgetKit与按钮形状契约](references/widgetkit.md)：桌面/锁屏小组件、圆角、按钮及跨App一致性。
- [小时选择契约](references/hour-picker.md)：生成提醒、预约或时长选择界面时读取；明确数据含义、交互和未实现的变体。
- [skill审核记录](references/skill-audit.md)：说明从旧版移除的过时规则与归档边界。
- `scripts/create_theme.py`：校验/登记新主题。
- `scripts/rebuild.py`：完整构建与Token导出。
- `scripts/package_release.py`：固定文件清单和元数据生成离线 ZIP。
- `scripts/test_release.py`：检查归档重现、链接与迁移重建。
- `scripts/validate.py`：当前产物与颜色静态验收。
- `scripts/test_system.py`：真实回归与新主题贯通测试。

原工作区的 `archive/v4/` 与 `scripts/old/` 仅为历史记录，不随 GitHub 仓库发布，也不是构建依赖。不要运行归档探针、把其截图当本轮证据，或重新引入其中已废弃的目录、数量、禁止规则。新增自动检查应验证可观察行为，不按CSS类数量制造“覆盖一致”的结论。
