## 1. Phase 1: 基础主题模块

- [ ] 1.1 创建 `src/web/themes.py` 模块文件
- [ ] 1.2 实现 `get_theme()` 函数，返回基于 `gr.themes.Soft` 的自定义主题
- [ ] 1.3 配置主题颜色方案（primary、secondary、neutral 色系）
- [ ] 1.4 配置主题字体（font、font_mono）和基础字号
- [ ] 1.5 配置主题间距（spacing、radius、shadow）
- [ ] 1.6 实现 `get_custom_css()` 函数，返回自定义 CSS 字符串
- [ ] 1.7 在 `src/config.py` 中添加 UI 主题配置项（可选主题名称）

## 2. Phase 2: 应用主题到界面

- [ ] 2.1 在 `src/web/app.py` 中导入 `get_theme` 和 `get_custom_css` 函数
- [ ] 2.2 将主题应用到 `gr.Blocks()` 组件（`theme=get_theme()`）
- [ ] 2.3 将自定义 CSS 添加到 `gr.Blocks()` 组件（`css=get_custom_css()`）
- [ ] 2.4 测试应用启动，确认主题加载正常

## 3. Phase 3: 自定义 CSS 样式增强

- [ ] 3.1 添加聊天气泡自定义样式（用户消息 vs 助手消息）
- [ ] 3.2 添加消息气泡的 padding、border-radius、阴影效果
- [ ] 3.3 添加按钮的 hover 和 active 状态样式
- [ ] 3.4 添加输入框的 focus 状态样式
- [ ] 3.5 添加页面整体容器的间距调整
- [ ] 3.6 添加标题和分隔符的样式优化

## 4. Phase 4: 布局优化

- [ ] 4.1 调整配置区域（API Key、模型选择）的列布局和间距
- [ ] 4.2 调整文档上传区域的组件间距
- [ ] 4.3 调整文件列表区域的显示样式
- [ ] 4.4 优化聊天区域的布局（输入框、按钮位置）
- [ ] 4.5 添加示例问题的样式优化

## 5. Phase 5: 视觉反馈改进

- [ ] 5.1 优化上传状态的显示样式（进度、成功、错误）
- [ ] 5.2 优化 URL 抓取状态的显示样式
- [ ] 5.3 添加操作按钮的加载状态反馈
- [ ] 5.4 添加成功/错误提示的视觉样式（颜色、图标）

## 6. Phase 6: 响应式布局

- [ ] 6.1 添加桌面屏幕（>= 1024px）的媒体查询样式
- [ ] 6.2 添加平板屏幕（768px - 1023px）的媒体查询样式
- [ ] 6.3 添加移动屏幕（< 768px）的媒体查询样式
- [ ] 6.4 测试不同屏幕尺寸下的布局效果

## 7. Phase 7: 测试与验证

- [ ] 7.1 启动应用，进行全功能测试
- [ ] 7.2 测试所有按钮、输入框、下拉菜单的交互效果
- [ ] 7.3 测试文档上传、URL 抓取、问答功能的显示效果
- [ ] 7.4 使用浏览器开发者工具测试响应式布局
- [ ] 7.5 验证主题在不同浏览器中的兼容性

## 8. Phase 8: 代码审查与提交

- [ ] 8.1 运行 `uv run pytest` 确保现有测试通过
- [ ] 8.2 运行 `uv run python src/web/app.py` 进行最终验证
- [ ] 8.3 检查代码风格和类型注解
- [ ] 8.4 提交代码：`git add src/web/themes.py src/web/app.py src/config.py`
- [ ] 8.5 提交：`git commit -m "feat(web): Add modern UI theme with enhanced styling"`

## 9. Phase 9: 文档更新（可选）

- [ ] 9.1 更新 README.md 中的界面截图（如有）
- [ ] 9.2 更新 CLAUDE.md 中的 Web 接口描述（如需要）
