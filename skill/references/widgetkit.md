# WidgetKit 小组件与共用按钮形状

这里的Widget指iPhone桌面/锁屏小组件，不是App内普通控件。权威来源为项目根 `widget_spec.py`、`shape_tokens.py`；人读规范 `standards.html#widgetkit`。JSON导出为 `components.widgetkit`、`components.button_shape`。四模式新色系自动继承。

## 圆角与系列一致性

- Widget外轮廓由系统管理，不套用主题的App卡片半径。背景使用 `containerBackground(for: .widget)`，内容遵从系统边距；不要用固定28pt描述所有设备的真实Widget圆角。
- 靠外框的内部卡片优先 `ContainerRelativeShape`，使圆角与容器协调。需要自绘时考虑连续圆角及同心关系。HTML演示外角28、内距16、内角12只是近似样张，不是Apple规定或原生连续曲率。
- 本项目明确选择独立文字按钮为Capsule、独立图标按钮为Circle，并同步App与Widget，避免App按钮8–14pt、Widget胶囊和时间选择器10pt混用。SwiftUI优先系统Button样式加 `buttonBorderShape(.capsule)`；不是宣称Apple要求所有按钮都是胶囊。
- `--r-btn:999px`是CSS胶囊手段，不是原生999pt半径；不随主题变化。分段控件有独立 `r_segment / r_segment_item`，不能用胶囊Token减常量。纯文字操作、Alert行按钮保持原生结构。

## 内容与交互

按widgetFamily分开设计小/中/大及锁屏圆形、矩形、行内布局；不要把App屏幕缩成Widget。样张当前覆盖小/中和三类锁屏布局，大尺寸须按具体内容补齐。小组件只显示关键摘要、快捷动作；时间选择滚轮/Sheet在App内，通过Link/widgetURL进入，不能声称HTML循环滚轮是WidgetKit可直接嵌入的控件。

真实动作使用Button/Toggle + App Intent，打开App使用Link/widgetURL。状态型操作用Toggle。支持版本、family、设备解锁状态分别核对；更新真实存储后提供时间线及错误恢复。HTML标签仅展示外观，不执行业务动作。

按widgetRenderingMode处理fullColor/accented/vibrant、背景移除以及用户主屏幕着色。锁屏示意只用单色，不能假定品牌底色一定保留。优先系统字体、SF Symbols和可访问名称，验证主要操作触达和大字裁切。

## 验收与改动

修改生成器和共享Token，重建全部页面；不得手改产物。运行rebuild、validate、test_system。静态检查确认四模式、注册主题覆盖、圆角Token和导出一致；真实WidgetKit扩展未提供时，必须将系统圆角、真实尺寸、锁屏着色、Intent与时间线验收标为待验证。

本轮按用户意图采用App/Widget统一胶囊按钮；不能继续从色系脚本生成各自8–14pt按钮半径。保留主题颜色和App内容卡片的差异。

参考：[Apple Widgets](https://developer.apple.com/design/human-interface-guidelines/widgets)、[ContainerRelativeShape](https://developer.apple.com/documentation/swiftui/containerrelativeshape)、[交互式Widget](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)。
