# React Native 消费契约 1

`design-tokens.json` 仍为生成产物，版本 5.1；新增 `native_contract_version=1`。
`native/resolve-tokens.cjs` 校验版本、主题、模式和颜色后映射成 RN 语义角色。
主色用于按钮填充，`onAction` 用于配对文字；文字操作使用 `actionText`。
模式必须由宿主明确传入，缺少深色或增强对比度模式时报错，不作隐式回退。

复制 JSON、适配器及类型声明到消费工程，保留这三个文件的版本关系。
CSS px 圆角转换为逻辑尺寸；百分比圆角不能直接传给 RN。示例胶囊使用 999，图标按钮由宿主按实际宽高构成圆形。
不从 HTML 的缩放比例推断系统字号。示例保留 `allowFontScaling`，不限制文字行数，按钮仅设最小高度。

`native/ActionExample.tsx` 展示最小保存行为，传入真正的持久化函数；失败可重试，快速重复按压不会重复提交。
宿主负责安全区、键盘、VoiceOver 焦点与系统高对比度设置。示例没有整套原生工程，不能直接称为 iOS 验收通过。

在根目录执行 `node --test native/test-tokens.cjs` 验证所有主题四模式与失败路径。
复制到已有 RN 工程后另做其类型检查、最小屏幕、最大系统文字、深色/高对比度和读屏验收。
