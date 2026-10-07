# 色系与组件契约

## 输入与产物

`themes.json`为自定义主题数组，A–F内置主题继续在既有生成器保留。每项：

```json
{
  "id": "mist-blue",
  "name": "雾蓝",
  "accent": "#6C8FA8",
  "auxiliary": "#F26B5B",
  "tertiary": "#F4C84A",
  "dark_accent": "#A0BDCF",
  "description": "低饱和雾蓝，适合安静阅读。",
  "material": "paper"
}
```

`auxiliary` 与 `tertiary` 可选，分别成为分类/图表的第二、第三装饰色种子，经 `design_tokens.py` 求解可读文字和图表色。危险、成功、警告等状态始终使用独立语义，不根据品牌色相猜用途。

必填id/name/accent。ID为2–32位小写英文、数字、连字符，首字符英文；颜色为#RRGGBB；材质paper/glass。名称/描述拒绝HTML标记及换行。未知字段失败，避免拼错参数静默无效。dark_accent省略时由主色推导；description省略时使用普通说明。

输出`theme-<id>.html`、`theme-<id>-ext.html`，并自动同步总览、导航、图标主题对照、设备尺寸页和JSON颜色导出。`material=glass`为导航层CSS示意，不是原生Liquid Glass光学实现。

## 语义层

| 角色 | 使用 | 不应使用 |
| --- | --- | --- |
| accent / on_accent | 主按钮与品牌色块及配对文字 | 直接将accent用于浅底小字 |
| accent_text / danger_text | 可读的文字操作、危险提示 | 替代所有品牌填充 |
| accent_ui / control_border | 必要功能图标、选中标记、输入边界 | 要求所有装饰分隔线同样加深 |
| ink / sub / faint | 正文、说明、辅助信息 | 通过opacity把可用文字压低到不合格 |
| tone2 / tone3 | 分类装饰色 | 直接当小标签文字 |
| tone2_text / tone3_text | 对soft2/soft3背景的标签文字 | 假定对所有背景都达标 |
| data2 / data3 / chart_muted | 图表序列和可见的中性数据 | 用极浅装饰线表示必要数据 |
| success_text/soft 等 | 成功、警告、信息状态 | 单凭颜色表达状态 |

普通模式文字内部求解门槛4.6:1，为4.5留少量余量；功能图形3.1，为3留余量。sub与ink目标7。HC文字目标7，控件边界目标4.5。普通品牌填充保持用户HEX，HC允许为提高配对字色可读性微调明度。算法锁定色相和饱和度调明度；不可解须抛错。

透明材质下，静态纯色对比度不代表最终合成背景合格。需在最亮/最暗/复杂背板以及系统降低透明度下复查。JSON四模式为light/dark/light_hc/dark_hc，不提供跨模式回退。

## 生成、字体与图标

`design_tokens.py`为语义计算源；`theme_registry.py`为自定义色板推导。不要复制算法到新主题脚本。已有A–F种子保留，颜色最终都进入同一个语义求解器。

字体使用用途层级与系统文字样式。各主题组件示例保持结构一致；不同业务页面可以调整布局。不要强迫所有文字使用0.5px步进，或把1.75倍命名为某个原生辅助字号档。

通用图标优先复用当前库或SF Symbols；选中用可读前景和非颜色提示。Tab使用系统组件时允许填充图标，不为“统一线性”改坏原生导航惯例。SVG库与状态栏Wi-Fi是不同资产，不能互相替换。

## 验收范围

`validate.py`检查颜色配对、实际输出的根/深色HC变量、主题入口、图标合同、设备数量、页面链接与模板占位。它不执行浏览器布局，不能证明焦点、裁切、点击区域、透明度合成或无障碍树正确。

变更逻辑后运行`test_system.py`：E/F深色HC回归、浅粉色品牌保留/文字可读、极端主色、非法输入、临时主题全链路、重复构建。原生SwiftUI工程、动态字体、VoiceOver及数据操作不在本仓库自动测试范围内。

## WidgetKit与统一按钮形状

桌面/锁屏小组件遵从[WidgetKit契约](widgetkit.md)。`shape_tokens.py`负责按钮与分段控件的形状；颜色求解产出附加同一份形状Token。新色系不得覆盖r_btn来生成8–14pt按钮；独立文字动作在App/Widget均为胶囊，图标按钮为圆形。Widget外框与内部容器曲率由系统/ContainerRelativeShape处理，不沿用主题App卡片半径。
