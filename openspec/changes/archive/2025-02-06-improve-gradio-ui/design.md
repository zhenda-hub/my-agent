## Context

### Current State

当前 Gradio 应用 (`src/web/app.py`) 使用默认的 Gradio 主题，没有自定义样式。界面布局较为紧凑，缺乏现代化的视觉设计。主要问题包括：

- 使用 Gradio 默认样式，缺乏品牌识别度
- 组件间距较小，视觉层次不清晰
- 按钮和输入框样式较为朴素
- 聊天气泡样式简单，可读性一般
- 无暗色模式支持

### Constraints

- **不引入新的外部依赖**：使用 Gradio 内置功能（themes, CSS）
- **保持向后兼容**：不改变现有 API 和功能逻辑
- **代码组织**：遵循项目 SOLID 原则，单一职责
- **性能**：样式加载不应影响应用启动性能

### Stakeholders

- 最终用户：获得更好的使用体验
- 开发者：易于维护和扩展的主题系统

## Goals / Non-Goals

**Goals:**

1. 提供现代化的 UI 主题，改善整体视觉效果
2. 增强交互组件的样式（按钮、输入框、下拉菜单）
3. 优化布局和间距，提升可读性
4. 添加视觉反馈机制（加载、成功、错误状态）
5. 改进聊天界面的消息气泡样式
6. 支持响应式布局，适配不同屏幕尺寸
7. （可选）支持暗色模式切换

**Non-Goals:**

- 不重构现有业务逻辑和功能
- 不改变 API 接口
- 不引入新的前端框架（如 React、Vue）
- 不创建复杂的多主题系统（如主题商店）

## Decisions

### D1: 使用 Gradio 内置主题系统

**Decision**: 使用 Gradio 4.0+ 的内置主题系统（`gr.themes`）而不是纯自定义 CSS。

**Rationale**:

- Gradio 内置主题经过良好设计，提供现代化基础
- 支持主题继承和自定义，灵活性高
- 无需维护大量 CSS 代码
- 官方支持，版本升级兼容性好

**Alternatives Considered**:

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| 纯自定义 CSS | 完全控制 | 维护成本高，版本兼容性差 | ❌ |
| Gradio 内置主题 | 官方支持，易维护 | 定制性稍受限 | ✅ |
| 使用第三方 Gradio 主题包 | 即用型 | 引入额外依赖 | ❌ |

### D2: 主题配置模块化

**Decision**: 创建独立的 `src/web/themes.py` 模块管理主题配置。

**Rationale**:

- 遵循单一职责原则（SRP）
- 主题逻辑与界面构建逻辑分离
- 便于测试和复用
- 符合 OCP 原则（对扩展开放，对修改关闭）

**Implementation**:

```python
# src/web/themes.py
def get_theme(theme_name: str = "default") -> gr.Theme:
    """获取配置好的 Gradio 主题"""

def get_custom_css() -> str:
    """返回自定义 CSS 字符串"""
```

### D3: 渐进式样式增强

**Decision**: 先实现基础主题和核心组件样式，再逐步添加高级特性（如暗色模式）。

**Rationale**:

- 降低实现风险
- 可以逐步验证效果
- 便于分阶段测试

**Implementation Phases**:

1. **Phase 1**: 应用现代主题，优化基础组件样式
2. **Phase 2**: 改进聊天界面，添加视觉反馈
3. **Phase 3**: 响应式布局优化
4. **Phase 4 (可选)**: 暗色模式支持

### D4: 配置驱动主题选择

**Decision**: 通过环境变量或配置文件控制主题选择，不添加用户界面切换。

**Rationale**:

- 简化实现，降低复杂度
- 管理员可统一控制界面风格
- 避免增加用户认知负担

**Alternatives Considered**:

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| UI 切换按钮 | 用户自选 | 增加复杂度，需要持久化状态 | ❌ |
| 配置文件控制 | 简单，统一管理 | 用户无法自选 | ✅ |

### D5: CSS 选择范围

**Decision**: 仅使用自定义 CSS 处理 Gradio 主题无法覆盖的细节，主要样式通过主题 API 配置。

**Rationale**:

- 主题 API 更稳定，版本升级兼容
- CSS 容易在 Gradio 更新时失效
- 减少 CSS 维护成本

**CSS 使用场景**:

- 聊天气泡的特殊样式
- 自定义动画效果
- 细微的间距调整
- 特定组件的覆盖样式

## Risks / Trade-offs

### Risk 1: Gradio 版本升级导致主题失效

**Risk**: Gradio 主题 API 在未来版本可能发生变化。

**Mitigation**:

- 使用 Gradio 官方文档推荐的 API
- 避免使用未文档化的内部属性
- 在 `pyproject.toml` 中固定 Gradio 主版本号

### Risk 2: 自定义 CSS 兼容性问题

**Risk**: Gradio DOM 结构变化可能导致 CSS 选择器失效。

**Mitigation**:

- 最小化自定义 CSS 使用
- 优先使用 Gradio 组件 ID 和类名
- 在 Gradio 更新时进行回归测试

### Trade-off 1: 定制性 vs 维护成本

**Trade-off**: 使用内置主题降低了定制自由度，但减少了维护成本。

**Decision**: 选择可维护性，通过主题继承和色彩调整实现足够的定制化。

### Trade-off 2: 暗色模式复杂度

**Trade-off**: 暗色模式需要额外的状态管理和组件适配。

**Decision**: 将暗色模式作为可选特性，在后续迭代中实现。

## Migration Plan

### Deployment Steps

1. **创建主题模块**
   ```bash
   touch src/web/themes.py
   ```

2. **实现基础主题**
   - 继承 `gr.themes.Soft` 或 `gr.themes.Base`
   - 配置颜色方案
   - 设置字体和间距

3. **更新 `src/web/app.py`**
   - 导入主题模块
   - 应用主题到 `gr.Blocks()`
   - 添加自定义 CSS

4. **测试验证**
   - 启动应用，检查视觉效果
   - 测试所有交互组件
   - 验证响应式布局

5. **提交代码**
   ```bash
   git add src/web/themes.py src/web/app.py
   git commit -m "feat(web): Add modern UI theme"
   ```

### Rollback Strategy

如果主题出现问题，可以通过以下方式回滚：

1. 移除 `gr.Blocks(theme=...)` 参数，恢复默认主题
2. 或切换回简单的配置：
   ```python
   gr.Blocks(theme=gr.themes.Default())
   ```

## Open Questions

1. **Q**: 是否需要支持用户自定义主题颜色？
   - **A**: 当前阶段不支持，通过配置文件预设几个主题选项

2. **Q**: 暗色模式的实现优先级？
   - **A**: 作为可选特性，在基础主题稳定后考虑实现

3. **Q**: 是否需要主题预览功能？
   - **A**: 不需要，通过配置文件控制的模式不需要预览
