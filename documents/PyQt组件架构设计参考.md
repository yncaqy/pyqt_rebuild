我正在对一个 PyQt/PySide 项目中的 **基础组件** 进行重构，重点是 **样式、动画及自定义绘制** 的解耦与现代化。许多组件因视觉效果复杂（如渐变、阴影、异形、不规则状态指示器等）无法完全依赖 QSS，不得不编写大量 `paintEvent` 代码。你将以资深 Qt 界面开发专家的身份，提供具体的设计方案、代码示例及迁移策略，尤其要解决 **绘制逻辑与组件逻辑深度耦合** 的问题。

------

### 1. 重构背景

- **目标组件**：`[例如：CustomPushButton, ModernLineEdit, AnimatedSlider, ProgressRing]`（至少包含一个严重依赖 `paintEvent` 的组件）
- **当前技术栈**：Python [3.9+]，PyQt [6] 
- **组件职责**：作为项目中的通用基础 UI 元件，提供统一的视觉风格和交互动画，部分效果无法通过原生 QSS 实现，必须使用 `QPainter` 自定义绘制。
- **当前实现存在的问题**：
  - **样式与逻辑耦合**：组件内部通过 `setStyleSheet` 硬编码样式字符串，或直接在 `paintEvent` 中用 QPainter 绘制，绘制参数（颜色、圆角、渐变、阴影）与状态变量混在一起。
  - **动画代码分散**：动画相关的 `QPropertyAnimation`、`QParallelAnimationGroup` 等直接在组件类中创建和管理，动画过程中往往强制调用 `update()` 触发整个 `paintEvent` 重绘，无法局部更新。
  - **状态管理混乱**：使用多个布尔变量（`hover`、`pressed`、`checked`、`enabled` 等）并在 `enterEvent`、`leaveEvent`、`mousePressEvent` 等事件中手动更新状态，触发 `update()`，状态组合复杂时极易出错。
  - **自定义绘制臃肿**：`paintEvent` 代码动辄上百行，包含大量绘图指令、分支判断，难以阅读和维护，也无法针对不同主题更换绘制风格。
  - **性能问题**：动画每帧都调用 `update()` 导致整个控件重绘，未利用 `QPainter` 的局部更新特性；`QTimer` 模拟动画现象普遍。
  - **定制性差**：外部调用者无法在不修改组件源码的情况下调整绘制参数（如颜色、圆角半径、阴影模糊半径）或替换整套绘制策略。
- **预期重构范围**：为项目中所有自定义基础组件建立一套统一的 **样式、动画与绘制管理机制**，并选取 1~2 个典型组件（一个以 QSS 为主，一个以 `paintEvent` 为主）进行重构示范。

------

### 2. 重构目标

1. **样式与组件分离**
   - 将视觉样式参数（颜色、字体、边框、圆角、渐变、阴影等）完全剥离出组件类，支持 **外部主题/样式注册表** 或 **QSS 变量** 的动态切换。
   - 对于 QSS 无法实现的效果，通过 **可插拔的绘制策略（Painting Strategy）** 将 `paintEvent` 委托给独立绘制对象，组件本身只负责事件处理和状态管理。
2. **动画与组件分离**
   - 将动画定义（属性变化、时间线、缓动曲线）与组件逻辑解耦，设计可复用的 **动画控制器** 或 **状态动画绑定器**。
   - 使用 `QPropertyAnimation` + `QVariantAnimation` 等原生机制，避免手动定时器，并尽可能针对特定属性变化进行局部更新，而非全组件重绘。
3. **状态管理统一化**
   - 基于 `Q_PROPERTY` 定义关键状态（如 `hover`、`pressed`、`checked`），通过属性变化发射信号，驱动动画控制器和绘制对象。
   - 对于 QSS 方案，利用 Qt 样式表的 **伪状态**（`:hover`、`:pressed`）减少自定义事件处理代码；对于自定义绘制，状态作为绘制策略的输入参数。
4. **绘制逻辑独立化**
   - 将 `paintEvent` 中的绘图代码提取到独立的类（如 `XxxPainter`、`XxxStyle`）中，组件通过组合方式持有绘制对象。
   - 绘制对象可根据主题/配置动态替换，实现 **运行时换肤** 或 **风格切换**。
   - 绘制方法只接收绘制设备（`QWidget`/`QPaintDevice`）、状态快照（或组件引用）及样式参数，不依赖组件内部实现细节。
5. **对外接口保持兼容**
   - 原有使用者通过 `setXXX()` 方法设置的属性（如 `setChecked(True)`）仍然有效，不破坏现有代码。
   - 提供简洁的扩展方式（如 `button.setPainter(MyCustomPainter())`、`button.setTheme("dark")`）。
6. **性能优化**
   - 避免不必要的重绘：动画属性变化时，若仅影响部分区域，使用 `update(rect)` 或 `QWidget::repaint` 的重载版本。
   - 动画对象生命周期管理，防止内存泄漏；绘制对象可复用。

------

### 3. 期望的输出形式

请以**分步骤、可落地**的方式提供以下内容：

1. **整体架构设计**

   - 类图或文字描述新引入的模块/类，例如：
     - `ThemeManager`：全局样式注册中心，支持动态换肤。
     - `AnimationController`：独立动画控制类，接收状态变化并驱动属性动画。
     - `WidgetPainter` 抽象基类/接口，定义 `paint(widget, painter, option, state)` 方法。
     - 重构后的基础组件如何继承 `QWidget` 并组合上述模块。
   - 推荐的设计模式（策略模式、装饰器模式、状态模式、观察者模式等）及在绘制解耦中的具体应用。

2. **关键代码示例**（以两个典型组件为例）
   **组件A：以 QSS 为主的按钮**（如 `CustomPushButton`）

   - 样式管理：主题字典定义，通过 `setProperty` + `polish` 动态应用样式表。
   - 动画管理：独立的 `ButtonAnimator` 类，监听状态属性变化，驱动 `QPropertyAnimation`。
   - 重构后的按钮类：极简的事件处理，仅委托给动画控制器。

   **组件B：严重依赖 paintEvent 的组件**（如 `ProgressRing` 或 `AnimatedSlider`）

   - 绘制策略接口定义：`class ProgressRingPainter` 实现 `paint` 方法，内部使用 `QPainter` 绘制圆弧、文字、阴影等。
   - 组件类内部持有 `ProgressRingPainter` 实例，`paintEvent` 中调用 `painter.paint(self, painter, option, self.currentState())`。
   - 动画如何影响绘制：例如 `value` 属性动画，动画更新时仅发射 `valueChanged`，组件内部调用 `update()` 触发重绘，绘制策略根据当前 `value` 绘制对应进度的圆弧。

3. **迁移步骤**

   - 在不破坏现有功能的前提下，如何逐步替换旧组件（例如先增加新类，旧类委托给新类，最后删除冗余代码）。
   - 单元测试建议：如何测试绘制策略（可使用 `QPixmap` 抓取绘制结果对比）、动画行为、样式切换。

4. **PyQt 特有注意事项**

   - `QSS` 在子控件中的局限性及替代方案；何时必须使用 `paintEvent`。
   - `QPropertyAnimation` 与 `QWidget` 属性的配合（需用 `Q_PROPERTY` 声明）。
   - 动态添加/删除属性对样式表的影响（`widget->setProperty()` 后需 `unpolish`/`polish`）。
   - 内存管理：动画对象应设置父对象或使用弱引用防止残留；绘制策略对象可全局共享（无状态时）或每个组件独立。
   - 双缓冲与绘制效率：减少 `painter.begin()`/`end()` 开销，合理使用 `QStyleOption` 获取标准样式参数。

5. **方案对比**（可选但推荐）
   针对自定义绘制部分，对比以下几种设计并提供推荐：

   - 完全基于 `QStyle` 派生（复杂，但深度集成）
   - 基于策略模式的独立绘制类（灵活，学习成本低）
   - 基于装饰器模式动态添加绘制层（类似 `QGraphicsEffect`，但限制较多）

------

### 4. 现有代码片段（示例）

为便于你理解当前实现，提供两个典型组件的简化代码：

**组件A：CustomPushButton（仅 QSS，无 paintEvent）**

python

```
class CustomPushButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.hover = False
        self.pressed = False
        self.animation = QVariantAnimation()
        self.animation.valueChanged.connect(self.update)
        self.setStyleSheet(""" ... 硬编码样式 ... """)
    
    def enterEvent(self, e): ...
    def leaveEvent(self, e): ...
    # 动画直接写在按钮里，无法复用
```



**组件B：CircularProgress（重度依赖 paintEvent）**

python

```
class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.maximum = 100
        self.animation = QPropertyAnimation(self, b"value")
        # 颜色、宽度等硬编码
        self.bar_color = QColor(52, 152, 219)
        self.bg_color = QColor(230, 230, 230)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 绘制背景圆环
        pen = QPen(self.bg_color, 10, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect().adjusted(5,5,-5,-5), 0, 5760)
        # 绘制前景进度
        pen.setColor(self.bar_color)
        painter.setPen(pen)
        angle = int(self.value / self.maximum * 5760)
        painter.drawArc(rect().adjusted(5,5,-5,-5), 0, angle)
        # 绘制中心文字等...
```



痛点：

- `CircularProgress` 中绘制参数（颜色、宽度、圆角）与组件代码耦合，无法换肤。
- `paintEvent` 包含全部绘制逻辑，难以扩展为其他风格（如虚线、渐变）。
- 动画仅驱动 `value` 属性，但 `paintEvent` 每帧重绘全部，性能尚可接受但仍有优化空间（如仅更新变化区域）。
- 无法在外部调整绘制细节，只能继承重写 `paintEvent`。

------

### 5. 附加约束

- 仅使用 PyQt 自身模块，不引入第三方库。
- 保持 Python 3.8+ 兼容
- 代码遵循 PEP8，类型提示可选但鼓励。
- 若存在多种设计方案，请对比优缺点并推荐一种。

------

**请根据以上信息，给出详细、可直接指导编码的重构方案。谢谢！**