# React Native 接入

`native/resolve-tokens.cjs` 用来把 `design-tokens.json` 中的颜色转换为 React Native 可用的字段。当前数据版本为 5.1，原生接口版本为 1（`native_contract_version`）。

把以下文件一起复制到自己的工程：

- `design-tokens.json`
- `native/resolve-tokens.cjs`
- `native/resolve-tokens.d.cts`

调用时指定主题和模式。主按钮用 `action` 填充、`onAction` 显示文字；普通背景上的文字操作用 `actionText`。适配器会检查版本、颜色和尺寸；主题或模式缺失时直接报错，避免错用另一套配色。

`native/ActionExample.tsx` 是一个保存按钮示例。传入实际保存函数后，它会处理提交中、失败重试和快速重复点击。示例保留字体缩放，不限制文字行数，只设置按钮的最小高度。

CSS 中的圆角会转换为逻辑尺寸。百分比圆角不能直接交给 React Native；示例胶囊使用 999，圆形图标按钮应按实际宽高设置。

在本仓库运行适配器测试：

```sh
node --test native/test-tokens.cjs
```

接入后还需要在自己的工程中检查类型、系统字号、安全区、键盘和读屏操作。本仓库没有完整的 React Native App 工程。

## 表单和日期／时间选择

接入时同时读取[交互标准](interaction-standard.md)及导出的 `components.picker_presentation`、`components.form_interaction`。这两项描述验收行为，不是现成的原生控件；颜色适配器不自动实现弹层、手势或键盘避让。
