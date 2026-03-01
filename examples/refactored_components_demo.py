"""
重构组件验证Demo

只使用重构过的组件，不包含任何原生PyQt组件（除布局类和QApplication外）

重构组件列表:
- FramelessWindow (容器)
- CustomPushButton (按钮)
- ModernLineEdit (输入框)
- CustomCheckBox (复选框)
- CircularProgress (圆形进度条)
- AnimatedSlider (动画滑块)
- ThemedLabel (主题化标签)
- Toast + ToastManager (通知)
- ThemedGroupBox (分组框)
- ThemedScrollArea (滚动区域)
- ThemedWidget (主题化容器)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIntValidator, QStandardItemModel, QStandardItem, QColor
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QAbstractItemView, QStackedWidget

from containers.frameless_window import FramelessWindow
from components.buttons.custom_push_button import CustomPushButton
from components.buttons.tool_button import ToolButton
from components.inputs.modern_line_edit import ModernLineEdit
from components.buttons.primary_push_button import PrimaryPushButton
from components.buttons.hyperlink_button import HyperlinkButton
from components.buttons.toggle_push_button import TogglePushButton
from components.buttons.pill_push_button import PillPushButton
from components.buttons.dropdown_push_button import DropDownPushButton
from components.buttons.radio_button import RadioButton
from components.widgets.combo_box import ComboBox
from components.widgets.editable_combo_box import EditableComboBox
from components.menus.round_menu import RoundMenu
from components.checkboxes.custom_check_box import CustomCheckBox
from components.progress.circular_progress import CircularProgress
from components.sliders.animated_slider import AnimatedSlider
from components.labels.themed_label import ThemedLabel
from components.labels.image_label import ImageLabel
from components.layouts.flow_layout import FlowLayout
from components.toasts.toast import Toast, ToastType, ToastPosition
from components.toasts.toast_manager import ToastManager
from components.containers.themed_group_box import ThemedGroupBox
from components.containers.themed_scroll_area import ThemedScrollArea
from components.containers.themed_widget import ThemedWidget
from components.dialogs.message_box import MessageBox
from components.lists.custom_list_widget import CustomListWidget, CustomListWidgetItem
from components.lists.custom_list_view import CustomListView
from components.tables.custom_table_widget import CustomTableWidget, CustomTableWidgetItem
from components.trees.custom_tree_widget import CustomTreeWidget, CustomTreeWidgetItem
from components.splash.splash_screen import SplashScreen
from components.containers.elevated_card_widget import ElevatedCardWidget
from components.menus.round_menu import RoundMenu
from components.navigation.pivot import Pivot
from components.navigation.tab_bar import TabBar, TabWidget
from components.media.simple_media_playbar import SimpleMediaPlayBar
from components.widgets.icon_widget import IconWidget, IconSize
from core.theme_manager import ThemeManager
from themes import DARK_THEME, LIGHT_THEME, DEFAULT_THEME


class RefactoredComponentsDemo(FramelessWindow):
    """重构组件验证窗口"""
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_content()
        
    def _setup_window(self):
        """设置窗口属性"""
        self.setTitle("重构组件验证Demo")
        self.resize(900, 700)
        
    def _setup_content(self):
        """设置内容"""
        content = self._create_content_widget()
        self.setCentralWidget(content)
        
    def _create_content_widget(self):
        """创建内容区域"""
        content = ThemedWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题区域
        layout.addWidget(self._create_title_section())
        layout.addWidget(self._create_theme_section())
        
        # 创建 Pivot 标签导航
        pivot = Pivot()
        pivot.addItem("基础组件", "basic")
        pivot.addItem("高级组件", "advanced")
        pivot.addItem("图标库", "icons")
        pivot.addItem("Pivot演示", "pivot_demo")
        pivot.addItem("TabBar演示", "tabbar_demo")
        
        # 创建堆叠窗口
        stack = QStackedWidget()
        
        # 基础组件页面
        basic_page = self._create_basic_page()
        stack.addWidget(basic_page)
        
        # 高级组件页面
        advanced_page = self._create_advanced_page()
        stack.addWidget(advanced_page)
        
        # 图标库页面
        icons_page = self._create_icons_page()
        stack.addWidget(icons_page)
        
        # Pivot演示页面
        pivot_demo_page = self._create_pivot_demo_page()
        stack.addWidget(pivot_demo_page)
        
        # TabBar演示页面
        tabbar_demo_page = self._create_tabbar_demo_page()
        stack.addWidget(tabbar_demo_page)
        
        # 连接信号
        def on_pivot_changed(key: str):
            index_map = {"basic": 0, "advanced": 1, "icons": 2, "pivot_demo": 3, "tabbar_demo": 4}
            if key in index_map:
                stack.setCurrentIndex(index_map[key])
        
        pivot.currentChanged.connect(on_pivot_changed)
        
        layout.addWidget(pivot)
        layout.addWidget(stack, 1)
        
        return content
    
    def _create_basic_page(self):
        """创建基础组件页面"""
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        page = ThemedWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_buttons_section())
        layout.addWidget(self._create_toggle_button_section())
        layout.addWidget(self._create_pill_button_section())
        layout.addWidget(self._create_dropdown_button_section())
        layout.addWidget(self._create_combo_box_section())
        layout.addWidget(self._create_editable_combo_section())
        layout.addWidget(self._create_inputs_section())
        layout.addWidget(self._create_checkbox_section())
        layout.addWidget(self._create_radio_button_section())
        layout.addWidget(self._create_progress_section())
        layout.addWidget(self._create_slider_section())
        layout.addWidget(self._create_toast_section())
        layout.addWidget(self._create_messagebox_section())
        layout.addStretch()
        
        scroll.setWidget(page)
        return scroll
    
    def _create_advanced_page(self):
        """创建高级组件页面"""
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        page = ThemedWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_list_section())
        layout.addWidget(self._create_listview_section())
        layout.addWidget(self._create_table_section())
        layout.addWidget(self._create_tree_section())
        layout.addWidget(self._create_splash_section())
        layout.addWidget(self._create_card_section())
        layout.addWidget(self._create_image_section())
        layout.addWidget(self._create_flow_section())
        layout.addWidget(self._create_tool_button_section())
        layout.addWidget(self._create_primary_button_section())
        layout.addWidget(self._create_hyperlink_section())
        layout.addWidget(self._create_menu_section())
        layout.addWidget(self._create_icon_widget_section())
        layout.addWidget(self._create_mediabar_section())
        layout.addStretch()
        
        scroll.setWidget(page)
        return scroll
    
    def _create_icons_page(self):
        """创建图标库展示页面"""
        from core.icon_manager import IconManager
        
        page = ThemedWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        icon_mgr = IconManager.instance()
        all_icons = icon_mgr.list_icons()
        
        title = ThemedLabel(f"图标库 (共 {len(all_icons)} 个图标)", font_role='subtitle')
        main_layout.addWidget(title)
        
        search_layout = QHBoxLayout()
        search_label = ThemedLabel("搜索:")
        self._icon_search_edit = ModernLineEdit()
        self._icon_search_edit.setPlaceholderText("输入图标名称过滤...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self._icon_search_edit, 1)
        main_layout.addLayout(search_layout)
        
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        self._icons_container = ThemedWidget()
        self._icons_grid_layout = QGridLayout(self._icons_container)
        self._icons_grid_layout.setSpacing(10)
        
        self._icon_widgets = []
        
        cols = 10
        row, col = 0, 0
        
        for icon_name in all_icons:
            icon_widget = self._create_icon_display(icon_name)
            self._icon_widgets.append((icon_name, icon_widget))
            self._icons_grid_layout.addWidget(icon_widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1
        
        self._icon_search_edit.textChanged.connect(self._filter_icons)
        
        scroll.setWidget(self._icons_container)
        main_layout.addWidget(scroll, 1)
        
        return page
    
    def _filter_icons(self, text: str):
        """过滤图标"""
        text = text.lower()
        for icon_name, icon_widget in self._icon_widgets:
            icon_widget.setVisible(text in icon_name.lower())
    
    def _create_icon_display(self, icon_name: str):
        """创建单个图标展示组件"""
        from components.widgets.icon_card import IconCard
        
        card = IconCard(icon_name, size=IconSize.XLARGE)
        card.clicked.connect(lambda name: self._show_toast(f"已复制: {name}", ToastType.SUCCESS))
        
        return card
    
    def _create_pivot_demo_page(self):
        """创建Pivot演示页面"""
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        page = ThemedWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_pivot_section())
        layout.addStretch()
        
        scroll.setWidget(page)
        return scroll
        
    def _create_title_section(self):
        """创建标题区域"""
        widget = ThemedWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 10)
        
        title = ThemedLabel("PyQt 重构组件验证", font_role='title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = ThemedLabel("所有组件均为重构版本，无原生组件", font_role='body')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        return widget
        
    def _create_theme_section(self):
        """创建主题控制区域"""
        group = ThemedGroupBox("主题切换")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        dark_btn = CustomPushButton("暗色主题")
        dark_btn.clicked.connect(lambda: self._switch_theme('dark'))
        
        light_btn = CustomPushButton("亮色主题")
        light_btn.clicked.connect(lambda: self._switch_theme('light'))
        
        default_btn = CustomPushButton("默认主题")
        default_btn.clicked.connect(lambda: self._switch_theme('default'))
        
        layout.addWidget(dark_btn)
        layout.addWidget(light_btn)
        layout.addWidget(default_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def _create_buttons_section(self):
        """创建按钮区域"""
        group = ThemedGroupBox("CustomPushButton 按钮")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 普通按钮
        normal_layout = QHBoxLayout()
        btn1 = CustomPushButton("普通按钮")
        btn1.set_tooltip("这是一个普通按钮")
        btn1.clicked.connect(lambda: self._show_toast("普通按钮被点击", ToastType.INFO))
        
        btn2 = CustomPushButton("成功操作")
        btn2.set_tooltip("执行成功操作")
        btn2.clicked.connect(lambda: self._show_toast("操作成功!", ToastType.SUCCESS))
        
        btn3 = CustomPushButton("警告")
        btn3.set_tooltip("显示警告信息")
        btn3.clicked.connect(lambda: self._show_toast("这是警告信息", ToastType.WARNING))
        
        btn4 = CustomPushButton("错误")
        btn4.set_tooltip("显示错误信息")
        btn4.clicked.connect(lambda: self._show_toast("发生错误!", ToastType.ERROR))
        
        btn5 = CustomPushButton("禁用状态")
        btn5.set_tooltip("此按钮已禁用")
        btn5.setEnabled(False)
        
        normal_layout.addWidget(btn1)
        normal_layout.addWidget(btn2)
        normal_layout.addWidget(btn3)
        normal_layout.addWidget(btn4)
        normal_layout.addWidget(btn5)
        normal_layout.addStretch()
        
        # 带图标按钮
        icon_layout = QHBoxLayout()
        btn6 = CustomPushButton("关闭", icon_name="window_close")
        btn6.set_tooltip("关闭窗口")
        btn6.clicked.connect(lambda: self._show_toast("关闭按钮被点击", ToastType.INFO))
        
        btn7 = CustomPushButton("最小化", icon_name="window_minimize")
        btn7.set_tooltip("最小化窗口")
        btn7.clicked.connect(lambda: self._show_toast("最小化按钮被点击", ToastType.INFO))
        
        btn8 = CustomPushButton("最大化", icon_name="window_maximize")
        btn8.set_tooltip("最大化窗口")
        btn8.clicked.connect(lambda: self._show_toast("最大化按钮被点击", ToastType.INFO))
        
        btn9 = CustomPushButton("恢复", icon_name="window_restore")
        btn9.set_tooltip("恢复窗口大小")
        btn9.clicked.connect(lambda: self._show_toast("恢复按钮被点击", ToastType.INFO))
        
        icon_layout.addWidget(btn6)
        icon_layout.addWidget(btn7)
        icon_layout.addWidget(btn8)
        icon_layout.addWidget(btn9)
        icon_layout.addStretch()
        
        layout.addLayout(normal_layout)
        layout.addLayout(icon_layout)
        
        group.setLayout(layout)
        return group

    def _create_toggle_button_section(self):
        """创建切换按钮区域"""
        group = ThemedGroupBox("TogglePushButton 切换按钮")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 基本切换按钮
        row1 = QHBoxLayout()
        
        self.toggle_btn1 = TogglePushButton("未选中")
        self.toggle_btn1.toggled.connect(lambda checked: self._on_toggle_changed(1, checked))
        
        self.toggle_btn2 = TogglePushButton("已选中")
        self.toggle_btn2.setChecked(True)
        self.toggle_btn2.toggled.connect(lambda checked: self._on_toggle_changed(2, checked))
        
        self.toggle_btn3 = TogglePushButton("禁用状态")
        self.toggle_btn3.setEnabled(False)
        
        row1.addWidget(self.toggle_btn1)
        row1.addWidget(self.toggle_btn2)
        row1.addWidget(self.toggle_btn3)
        row1.addStretch()
        
        # 带图标的切换按钮
        row2 = QHBoxLayout()
        
        self.toggle_btn4 = TogglePushButton("设置", icon_name="Setting")
        self.toggle_btn4.toggled.connect(lambda checked: self._on_toggle_changed(4, checked))
        
        self.toggle_btn5 = TogglePushButton("搜索", icon_name="Search")
        self.toggle_btn5.setChecked(True)
        self.toggle_btn5.toggled.connect(lambda checked: self._on_toggle_changed(5, checked))
        
        self.toggle_btn6 = TogglePushButton("下载", icon_name="Download")
        self.toggle_btn6.toggled.connect(lambda checked: self._on_toggle_changed(6, checked))
        
        row2.addWidget(self.toggle_btn4)
        row2.addWidget(self.toggle_btn5)
        row2.addWidget(self.toggle_btn6)
        row2.addStretch()
        
        # 状态显示
        self.toggle_status = ThemedLabel("点击按钮切换状态")
        
        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(self.toggle_status)
        
        group.setLayout(layout)
        return group
    
    def _on_toggle_changed(self, btn_id: int, checked: bool):
        """处理切换按钮状态变化"""
        status = "选中" if checked else "未选中"
        self._show_toast(f"按钮 {btn_id}: {status}", ToastType.INFO)
        self.toggle_status.setText(f"按钮 {btn_id} 状态: {status}")

    def _create_pill_button_section(self):
        """创建胶囊按钮区域"""
        group = ThemedGroupBox("PillPushButton 胶囊按钮")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 基本胶囊按钮
        row1 = QHBoxLayout()
        
        self.pill_btn1 = PillPushButton("标签1")
        self.pill_btn1.toggled.connect(lambda c: self._on_pill_changed(1, c))
        
        self.pill_btn2 = PillPushButton("标签2")
        self.pill_btn2.setChecked(True)
        self.pill_btn2.toggled.connect(lambda c: self._on_pill_changed(2, c))
        
        self.pill_btn3 = PillPushButton("禁用")
        self.pill_btn3.setEnabled(False)
        
        row1.addWidget(self.pill_btn1)
        row1.addWidget(self.pill_btn2)
        row1.addWidget(self.pill_btn3)
        row1.addStretch()
        
        # 带图标的胶囊按钮
        row2 = QHBoxLayout()
        
        self.pill_btn4 = PillPushButton("Python", icon_name="Setting")
        self.pill_btn4.toggled.connect(lambda c: self._on_pill_changed(4, c))
        
        self.pill_btn5 = PillPushButton("PyQt", icon_name="Search")
        self.pill_btn5.setChecked(True)
        self.pill_btn5.toggled.connect(lambda c: self._on_pill_changed(5, c))
        
        self.pill_btn6 = PillPushButton("Fluent", icon_name="Download")
        self.pill_btn6.toggled.connect(lambda c: self._on_pill_changed(6, c))
        
        row2.addWidget(self.pill_btn4)
        row2.addWidget(self.pill_btn5)
        row2.addWidget(self.pill_btn6)
        row2.addStretch()
        
        # 状态显示
        self.pill_status = ThemedLabel("点击标签切换选中状态")
        
        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(self.pill_status)
        
        group.setLayout(layout)
        return group
    
    def _on_pill_changed(self, btn_id: int, checked: bool):
        """处理胶囊按钮状态变化"""
        status = "选中" if checked else "未选中"
        self._show_toast(f"标签 {btn_id}: {status}", ToastType.INFO)
        self.pill_status.setText(f"标签 {btn_id} 状态: {status}")

    def _create_dropdown_button_section(self):
        """创建下拉按钮区域"""
        group = ThemedGroupBox("DropDownPushButton 下拉按钮")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 文件菜单
        self.dropdown_btn1 = DropDownPushButton("文件")
        file_menu = RoundMenu()
        file_menu.addAction("新建", lambda: self._on_menu_action("新建文件"), icon="Add")
        file_menu.addAction("打开", lambda: self._on_menu_action("打开文件"), icon="Folder")
        file_menu.addSeparator()
        file_menu.addAction("退出", lambda: self._on_menu_action("退出"), icon="Close")
        self.dropdown_btn1.setMenu(file_menu)
        
        # 编辑菜单
        self.dropdown_btn2 = DropDownPushButton("编辑", icon_name="Edit")
        edit_menu = RoundMenu()
        edit_menu.addAction("撤销", lambda: self._on_menu_action("撤销"))
        edit_menu.addAction("重做", lambda: self._on_menu_action("重做"))
        edit_menu.addSeparator()
        edit_menu.addAction("复制", lambda: self._on_menu_action("复制"))
        edit_menu.addAction("粘贴", lambda: self._on_menu_action("粘贴"))
        self.dropdown_btn2.setMenu(edit_menu)
        
        # 禁用状态
        self.dropdown_btn3 = DropDownPushButton("禁用")
        self.dropdown_btn3.setEnabled(False)
        
        layout.addWidget(self.dropdown_btn1)
        layout.addWidget(self.dropdown_btn2)
        layout.addWidget(self.dropdown_btn3)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _on_menu_action(self, action: str):
        """处理菜单项点击"""
        self._show_toast(f"点击了: {action}", ToastType.INFO)

    def _create_combo_box_section(self):
        """创建组合框区域"""
        group = ThemedGroupBox("ComboBox 组合框")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 基本组合框
        self.combo1 = ComboBox()
        self.combo1.addItem("选项1")
        self.combo1.addItem("选项2")
        self.combo1.addItem("选项3")
        self.combo1.setCurrentIndex(0)
        self.combo1.currentIndexChanged.connect(lambda i: self._on_combo_changed("组合框1", i))
        
        # 编程语言选择
        self.combo2 = ComboBox()
        self.combo2.addItems(["Python", "JavaScript", "Java", "C++", "Go"])
        self.combo2.setCurrentIndex(0)
        self.combo2.currentIndexChanged.connect(lambda i: self._on_combo_changed("组合框2", i))
        
        # 带占位文本
        self.combo3 = ComboBox()
        self.combo3.setPlaceholderText("请选择...")
        self.combo3.addItems(["北京", "上海", "广州", "深圳"])
        self.combo3.currentIndexChanged.connect(lambda i: self._on_combo_changed("组合框3", i))
        
        # 禁用状态
        self.combo4 = ComboBox()
        self.combo4.addItem("禁用状态")
        self.combo4.setCurrentIndex(0)
        self.combo4.setEnabled(False)
        
        layout.addWidget(self.combo1)
        layout.addWidget(self.combo2)
        layout.addWidget(self.combo3)
        layout.addWidget(self.combo4)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _on_combo_changed(self, name: str, index: int):
        """处理组合框选择变化"""
        combo = self.sender()
        text = combo.currentText() if combo else ""
        self._show_toast(f"{name} 选中: {index} - {text}", ToastType.INFO)

    def _create_editable_combo_section(self):
        """创建可编辑组合框区域"""
        group = ThemedGroupBox("EditableComboBox 可编辑组合框")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 基本可编辑组合框
        self.edit_combo1 = EditableComboBox()
        self.edit_combo1.addItems(["Python", "JavaScript", "Java", "C++", "Go"])
        self.edit_combo1.setCurrentIndex(0)
        self.edit_combo1.currentIndexChanged.connect(lambda i: self._on_edit_combo_changed("可编辑组合框1", i))
        self.edit_combo1.itemAdded.connect(lambda text: self._show_toast(f"添加新项目: {text}", ToastType.SUCCESS))
        
        # 带占位文本
        self.edit_combo2 = EditableComboBox()
        self.edit_combo2.setPlaceholderText("输入并按回车添加...")
        self.edit_combo2.addItems(["北京", "上海", "广州", "深圳"])
        self.edit_combo2.currentIndexChanged.connect(lambda i: self._on_edit_combo_changed("可编辑组合框2", i))
        
        # 禁用状态
        self.edit_combo3 = EditableComboBox()
        self.edit_combo3.addItem("禁用状态")
        self.edit_combo3.setCurrentIndex(0)
        self.edit_combo3.setEnabled(False)
        
        layout.addWidget(self.edit_combo1)
        layout.addWidget(self.edit_combo2)
        layout.addWidget(self.edit_combo3)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _on_edit_combo_changed(self, name: str, index: int):
        """处理可编辑组合框选择变化"""
        combo = self.sender()
        text = combo.currentText() if combo else ""
        self._show_toast(f"{name} 选中: {index} - {text}", ToastType.INFO)
        
    def _create_inputs_section(self):
        """创建输入框区域"""
        group = ThemedGroupBox("ModernLineEdit 输入框")
        container = ThemedWidget()
        layout = QGridLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label1 = ThemedLabel("用户名:")
        self.username_input = ModernLineEdit()
        self.username_input.set_placeholder_text("请输入用户名...")
        
        label2 = ThemedLabel("密码:")
        self.password_input = ModernLineEdit()
        self.password_input.set_placeholder_text("请输入密码...")
        self.password_input.set_echo_mode(ModernLineEdit.EchoMode.Password)
        
        label3 = ThemedLabel("年龄:")
        self.age_input = ModernLineEdit()
        self.age_input.set_placeholder_text("18-99")
        self.age_input.setValidator(QIntValidator(18, 99, self.age_input))
        
        label4 = ThemedLabel("邮箱:")
        self.email_input = ModernLineEdit()
        self.email_input.set_placeholder_text("example@email.com")
        self.email_input.textChanged.connect(self._validate_email)
        
        self.email_status = ThemedLabel("")
        
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(label2, 1, 0)
        layout.addWidget(self.password_input, 1, 1)
        layout.addWidget(label3, 2, 0)
        layout.addWidget(self.age_input, 2, 1)
        layout.addWidget(label4, 3, 0)
        layout.addWidget(self.email_input, 3, 1)
        layout.addWidget(self.email_status, 4, 1)
        
        group.setLayout(layout)
        return group
        
    def _create_checkbox_section(self):
        """创建复选框区域"""
        group = ThemedGroupBox("CustomCheckBox 复选框")
        container = ThemedWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        row1 = ThemedWidget()
        layout1 = QHBoxLayout(row1)
        layout1.setContentsMargins(0, 0, 0, 0)
        
        self.cb1 = CustomCheckBox("功能A")
        self.cb2 = CustomCheckBox("功能B")
        self.cb3 = CustomCheckBox("功能C")
        self.cb1.stateChanged.connect(self._update_checkbox_status)
        self.cb2.stateChanged.connect(self._update_checkbox_status)
        self.cb3.stateChanged.connect(self._update_checkbox_status)
        
        layout1.addWidget(self.cb1)
        layout1.addWidget(self.cb2)
        layout1.addWidget(self.cb3)
        layout1.addStretch()
        
        row2 = ThemedWidget()
        layout2 = QHBoxLayout(row2)
        layout2.setContentsMargins(0, 0, 0, 0)
        
        self.cb4 = CustomCheckBox("接收通知")
        self.cb5 = CustomCheckBox("同意条款")
        self.cb5.setChecked(True)
        
        layout2.addWidget(self.cb4)
        layout2.addWidget(self.cb5)
        layout2.addStretch()
        
        self.checkbox_status = ThemedLabel("已启用: 0/3 个功能")
        
        main_layout.addWidget(row1)
        main_layout.addWidget(row2)
        main_layout.addWidget(self.checkbox_status)
        
        group.setLayout(main_layout)
        return group
        
    def _create_radio_button_section(self):
        """创建单选按钮区域"""
        group = ThemedGroupBox("RadioButton 单选按钮")
        container = ThemedWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        row1 = ThemedWidget()
        layout1 = QHBoxLayout(row1)
        layout1.setContentsMargins(0, 0, 0, 0)
        
        self.radio1 = RadioButton("选项A")
        self.radio2 = RadioButton("选项B")
        self.radio3 = RadioButton("选项C")
        self.radio1.setChecked(True)
        self.radio1.toggled.connect(self._on_radio_toggled)
        self.radio2.toggled.connect(self._on_radio_toggled)
        self.radio3.toggled.connect(self._on_radio_toggled)
        
        layout1.addWidget(self.radio1)
        layout1.addWidget(self.radio2)
        layout1.addWidget(self.radio3)
        layout1.addStretch()
        
        row2 = ThemedWidget()
        layout2 = QHBoxLayout(row2)
        layout2.setContentsMargins(0, 0, 0, 0)
        
        self.radio4 = RadioButton("启用")
        self.radio5 = RadioButton("禁用")
        self.radio5.setEnabled(False)
        
        layout2.addWidget(self.radio4)
        layout2.addWidget(self.radio5)
        layout2.addStretch()
        
        self.radio_status = ThemedLabel("当前选中: 选项A")
        
        main_layout.addWidget(row1)
        main_layout.addWidget(row2)
        main_layout.addWidget(self.radio_status)
        
        group.setLayout(main_layout)
        return group
    
    def _on_radio_toggled(self, checked: bool):
        """处理单选按钮状态变化"""
        if checked:
            radio = self.sender()
            if radio:
                self.radio_status.setText(f"当前选中: {radio.text()}")
        
    def _create_progress_section(self):
        """创建进度条区域"""
        group = ThemedGroupBox("CircularProgress 圆形进度条")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        for value, label_text in [(25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]:
            col = ThemedWidget()
            col_layout = QVBoxLayout(col)
            col_layout.setContentsMargins(0, 0, 0, 0)
            
            progress = CircularProgress()
            progress.setValue(value)
            progress.setFixedSize(80, 80)
            
            center = ThemedWidget()
            center_layout = QHBoxLayout(center)
            center_layout.setContentsMargins(0, 0, 0, 0)
            center_layout.addStretch()
            center_layout.addWidget(progress)
            center_layout.addStretch()
            
            label = ThemedLabel(label_text, font_role='small')
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            col_layout.addWidget(center)
            col_layout.addWidget(label)
            
            layout.addWidget(col)
            
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def _create_slider_section(self):
        """创建滑块区域"""
        group = ThemedGroupBox("AnimatedSlider 动画滑块")
        container = ThemedWidget()
        layout = QGridLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label1 = ThemedLabel("音量:")
        self.volume_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_label = ThemedLabel("70%", font_role='small')
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"{v}%")
        )
        
        label2 = ThemedLabel("亮度:")
        self.brightness_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_label = ThemedLabel("50%", font_role='small')
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_label.setText(f"{v}%")
        )
        
        label3 = ThemedLabel("进度:")
        self.progress_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(50)
        self.progress_value_label = ThemedLabel("50%", font_role='small')
        self.progress_slider.valueChanged.connect(
            lambda v: self.progress_value_label.setText(f"{v}%")
        )
        
        animate_btn = CustomPushButton("动画到100%")
        animate_btn.clicked.connect(self._animate_slider)
        
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.volume_slider, 0, 1)
        layout.addWidget(self.volume_label, 0, 2)
        
        layout.addWidget(label2, 1, 0)
        layout.addWidget(self.brightness_slider, 1, 1)
        layout.addWidget(self.brightness_label, 1, 2)
        
        layout.addWidget(label3, 2, 0)
        layout.addWidget(self.progress_slider, 2, 1)
        layout.addWidget(self.progress_value_label, 2, 2)
        layout.addWidget(animate_btn, 2, 3)
        
        group.setLayout(layout)
        return group
        
    def _create_toast_section(self):
        """创建Toast区域"""
        group = ThemedGroupBox("Toast 通知组件")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        info_btn = CustomPushButton("Info通知")
        info_btn.clicked.connect(
            lambda: self._show_toast("这是一条信息通知", ToastType.INFO)
        )
        
        success_btn = CustomPushButton("Success通知")
        success_btn.clicked.connect(
            lambda: self._show_toast("操作成功完成!", ToastType.SUCCESS)
        )
        
        warning_btn = CustomPushButton("Warning通知")
        warning_btn.clicked.connect(
            lambda: self._show_toast("请注意检查输入", ToastType.WARNING)
        )
        
        error_btn = CustomPushButton("Error通知")
        error_btn.clicked.connect(
            lambda: self._show_toast("发生了一个错误!", ToastType.ERROR)
        )
        
        layout.addWidget(info_btn)
        layout.addWidget(success_btn)
        layout.addWidget(warning_btn)
        layout.addWidget(error_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def _create_messagebox_section(self):
        """创建MessageBox区域"""
        group = ThemedGroupBox("MessageBox 消息对话框")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        info_btn = CustomPushButton("信息对话框")
        info_btn.clicked.connect(self._show_info_dialog)
        
        warning_btn = CustomPushButton("警告对话框")
        warning_btn.clicked.connect(self._show_warning_dialog)
        
        error_btn = CustomPushButton("错误对话框")
        error_btn.clicked.connect(self._show_error_dialog)
        
        question_btn = CustomPushButton("询问对话框")
        question_btn.clicked.connect(self._show_question_dialog)
        
        layout.addWidget(info_btn)
        layout.addWidget(warning_btn)
        layout.addWidget(error_btn)
        layout.addWidget(question_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def _show_info_dialog(self):
        MessageBox.information(self, "信息", "这是一条信息提示对话框。")
        
    def _show_warning_dialog(self):
        MessageBox.warning(self, "警告", "这是一条警告提示对话框。")
        
    def _show_error_dialog(self):
        MessageBox.critical(self, "错误", "这是一条错误提示对话框。")
        
    def _show_question_dialog(self):
        result = MessageBox.question(self, "确认", "确定要执行此操作吗？")
        if result == MessageBox.OK:
            self._show_toast("用户点击了确定", ToastType.SUCCESS)
        else:
            self._show_toast("用户点击了取消", ToastType.INFO)
    
    def _create_list_section(self):
        """创建ListWidget区域"""
        group = ThemedGroupBox("CustomListWidget 列表组件")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        single_list = CustomListWidget()
        single_list.setFixedHeight(150)
        single_list.addItems(["项目 1", "项目 2", "项目 3", "项目 4", "项目 5"])
        single_list.itemClicked.connect(self._on_list_item_clicked)
        
        multi_list = CustomListWidget()
        multi_list.setFixedHeight(150)
        multi_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        for i in range(1, 6):
            item = CustomListWidgetItem(f"可多选项目 {i}")
            multi_list.addItem(item)
        multi_list.itemSelectionChanged.connect(self._on_multi_selection_changed)
        
        layout.addWidget(single_list)
        layout.addWidget(multi_list)
        
        group.setLayout(layout)
        return group
    
    def _create_listview_section(self):
        """创建ListView区域"""
        group = ThemedGroupBox("CustomListView 视图组件 (Model-View)")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        list_view = CustomListView()
        list_view.setFixedHeight(150)
        
        model = QStandardItemModel()
        for i in range(1, 6):
            item = QStandardItem(f"模型数据 {i}")
            item.setEditable(False)
            model.appendRow(item)
        list_view.setModel(model)
        list_view.clicked.connect(self._on_listview_clicked)
        
        layout.addWidget(list_view)
        
        group.setLayout(layout)
        return group
    
    def _on_list_item_clicked(self, item: CustomListWidgetItem):
        self._show_toast(f"点击了: {item.text()}", ToastType.INFO)
    
    def _on_multi_selection_changed(self):
        pass
    
    def _on_listview_clicked(self, index):
        self._show_toast(f"选中了: {index.data()}", ToastType.INFO)
    
    def _create_table_section(self):
        """创建TableWidget区域"""
        group = ThemedGroupBox("CustomTableWidget 表格组件")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        table = CustomTableWidget()
        table.setFixedHeight(200)
        table.setColumnCount(4)
        table.setRowCount(5)
        table.setHorizontalHeaderLabels(["姓名", "年龄", "城市", "职业"])
        
        data = [
            ("张三", "25", "北京", "工程师"),
            ("李四", "30", "上海", "设计师"),
            ("王五", "28", "广州", "产品经理"),
            ("赵六", "35", "深圳", "架构师"),
            ("钱七", "22", "杭州", "实习生"),
        ]
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = CustomTableWidgetItem(value)
                table.setItem(row, col, item)
        
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        
        table.itemClicked.connect(self._on_table_item_clicked)
        
        layout.addWidget(table)
        
        group.setLayout(layout)
        return group
    
    def _on_table_item_clicked(self, item):
        self._show_toast(f"点击了: {item.text()}", ToastType.INFO)
    
    def _create_tree_section(self):
        """创建TreeWidget区域"""
        group = ThemedGroupBox("CustomTreeWidget 树形组件")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        tree = CustomTreeWidget()
        tree.setFixedHeight(200)
        
        root1 = CustomTreeWidgetItem(text="项目 1")
        tree.addTopLevelItem(root1)
        
        child1_1 = CustomTreeWidgetItem(root1, text="子项目 1-1")
        child1_2 = CustomTreeWidgetItem(root1, text="子项目 1-2")
        child1_3 = CustomTreeWidgetItem(root1, text="子项目 1-3")
        
        child1_1_1 = CustomTreeWidgetItem(child1_1, text="子项目 1-1-1")
        child1_1_2 = CustomTreeWidgetItem(child1_1, text="子项目 1-1-2")
        
        root2 = CustomTreeWidgetItem(text="项目 2")
        tree.addTopLevelItem(root2)
        
        child2_1 = CustomTreeWidgetItem(root2, text="子项目 2-1")
        child2_2 = CustomTreeWidgetItem(root2, text="子项目 2-2")
        
        root3 = CustomTreeWidgetItem(text="项目 3")
        tree.addTopLevelItem(root3)
        
        tree.expandItem(root1)
        tree.expandItem(child1_1)
        
        tree.itemClicked.connect(self._on_tree_item_clicked)
        
        layout.addWidget(tree)
        
        group.setLayout(layout)
        return group
    
    def _on_tree_item_clicked(self, item, column):
        self._show_toast(f"点击了: {item.text(0)}", ToastType.INFO)
    
    def _create_splash_section(self):
        """创建SplashScreen区域"""
        group = ThemedGroupBox("SplashScreen 启动画面")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        btn_with_progress = CustomPushButton("带进度条")
        btn_with_progress.clicked.connect(self._show_splash_with_progress)
        layout.addWidget(btn_with_progress)
        
        btn_simple = CustomPushButton("简单显示")
        btn_simple.clicked.connect(self._show_splash_simple)
        layout.addWidget(btn_simple)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _show_splash_with_progress(self):
        self._splash = SplashScreen()
        self._splash.setTitle("My Application")
        self._splash.setSubtitle("正在加载资源...")
        
        self._progress = 0
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_splash_progress)
        self._progress_timer.start(50)
        
        self._splash.show_and_fade_in()
    
    def _update_splash_progress(self):
        if not hasattr(self, '_splash'):
            self._progress_timer.stop()
            return
        
        self._progress += 2
        self._splash.setProgress(self._progress)
        
        if self._progress < 30:
            self._splash.setSubtitle("正在初始化...")
        elif self._progress < 60:
            self._splash.setSubtitle("正在加载资源...")
        elif self._progress < 90:
            self._splash.setSubtitle("正在准备界面...")
        else:
            self._splash.setSubtitle("即将完成...")
        
        if self._progress >= 100:
            self._progress_timer.stop()
            QTimer.singleShot(500, self._close_splash)
    
    def _close_splash(self):
        if hasattr(self, '_splash'):
            self._splash.fade_out()
    
    def _show_splash_simple(self):
        self._splash2 = SplashScreen()
        self._splash2.setTitle("My Application")
        self._splash2.setSubtitle("正在启动...")
        self._splash2.show_and_fade_in()
        
        QTimer.singleShot(2000, self._close_splash2)
    
    def _close_splash2(self):
        if hasattr(self, '_splash2'):
            self._splash2.fade_out()
    
    def _create_card_section(self):
        """创建Card区域"""
        group = ThemedGroupBox("ElevatedCardWidget 卡片组件")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        
        card1 = ElevatedCardWidget()
        card1.setFixedSize(180, 120)
        card1_content = ThemedWidget()
        card1_layout = QVBoxLayout(card1_content)
        card1_layout.setContentsMargins(0, 0, 0, 0)
        card1_title = ThemedLabel("卡片 1", font_role='subtitle')
        card1_desc = ThemedLabel("鼠标移入查看效果", font_role='body')
        card1_layout.addWidget(card1_title)
        card1_layout.addWidget(card1_desc)
        card1_layout.addStretch()
        card1.setContentWidget(card1_content)
        layout.addWidget(card1)
        
        card2 = ElevatedCardWidget()
        card2.setFixedSize(180, 120)
        card2_content = ThemedWidget()
        card2_layout = QVBoxLayout(card2_content)
        card2_layout.setContentsMargins(0, 0, 0, 0)
        card2_title = ThemedLabel("卡片 2", font_role='subtitle')
        card2_desc = ThemedLabel("带阴影和上移动画", font_role='body')
        card2_layout.addWidget(card2_title)
        card2_layout.addWidget(card2_desc)
        card2_layout.addStretch()
        card2.setContentWidget(card2_content)
        layout.addWidget(card2)
        
        card3 = ElevatedCardWidget()
        card3.setFixedSize(180, 120)
        card3_content = ThemedWidget()
        card3_layout = QVBoxLayout(card3_content)
        card3_layout.setContentsMargins(0, 0, 0, 0)
        card3_title = ThemedLabel("卡片 3", font_role='subtitle')
        card3_desc = ThemedLabel("主题适配", font_role='body')
        card3_layout.addWidget(card3_title)
        card3_layout.addWidget(card3_desc)
        card3_layout.addStretch()
        card3.setContentWidget(card3_content)
        layout.addWidget(card3)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _create_image_section(self):
        """创建ImageLabel区域"""
        group = ThemedGroupBox("ImageLabel 图片组件")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        
        # 获取图片目录的绝对路径（基于项目根目录）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_dir = os.path.join(project_root, 'src', 'resources', 'images')
        
        image_label1 = ImageLabel()
        image_label1.setFixedSize(150, 150)
        image_label1.setBorderRadius(8)
        image_label1.setImage(os.path.join(images_dir, "拾光_壁纸汇_6538fb82e8b39b98.jpg"))
        layout.addWidget(image_label1)
        
        image_label2 = ImageLabel()
        image_label2.setFixedSize(150, 150)
        image_label2.setBorderRadius(8)
        image_label2.setImage(os.path.join(images_dir, "拾光_故宫博物院_25609b39e7117207.jpg"))
        layout.addWidget(image_label2)
        
        image_label3 = ImageLabel()
        image_label3.setFixedSize(150, 150)
        image_label3.setBorderRadius(8)
        image_label3.setImage(os.path.join(images_dir, "拾光_故宫博物院_908379888903489d.jpg"))
        layout.addWidget(image_label3)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _create_flow_section(self):
        """创建FlowLayout区域"""
        group = ThemedGroupBox("FlowLayout 流式布局")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        flow_container = ThemedWidget()
        flow_layout = FlowLayout(flow_container)
        flow_layout.setSpacing(10)
        flow_layout.setContentsMargins(0, 0, 0, 0)
        
        tags = [
            "Python", "PyQt6", "Qt", "GUI", "Desktop",
            "Cross-platform", "Widgets", "Layout", "Flow",
            "自适应", "换行", "流式布局", "响应式"
        ]
        
        for tag in tags:
            btn = CustomPushButton(tag)
            btn.setFixedHeight(32)
            flow_layout.addWidget(btn)
        
        flow_container.setLayout(flow_layout)
        layout.addWidget(flow_container)
        
        group.setLayout(layout)
        return group
    
    def _create_tool_button_section(self):
        """创建ToolButton区域"""
        group = ThemedGroupBox("ToolButton 工具按钮")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        close_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>"""
        
        min_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg>"""
        
        max_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect></svg>"""
        
        setting_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>"""
        
        btn1 = ToolButton()
        btn1.setIcon(close_icon)
        btn1.setToolTip("关闭")
        layout.addWidget(btn1)
        
        btn2 = ToolButton()
        btn2.setIcon(min_icon)
        btn2.setToolTip("最小化")
        layout.addWidget(btn2)
        
        btn3 = ToolButton()
        btn3.setIcon(max_icon)
        btn3.setToolTip("最大化")
        layout.addWidget(btn3)
        
        btn4 = ToolButton()
        btn4.setIcon(setting_icon)
        btn4.setToolTip("设置")
        layout.addWidget(btn4)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _create_primary_button_section(self):
        """创建PrimaryPushButton区域"""
        group = ThemedGroupBox("PrimaryPushButton 主要按钮")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        btn1 = PrimaryPushButton("确定")
        layout.addWidget(btn1)
        
        btn2 = PrimaryPushButton("保存")
        layout.addWidget(btn2)
        
        submit_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>"""
        btn3 = PrimaryPushButton("提交")
        btn3.setIcon(submit_icon)
        layout.addWidget(btn3)
        
        btn4 = PrimaryPushButton("禁用状态")
        btn4.setEnabled(False)
        layout.addWidget(btn4)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _create_hyperlink_section(self):
        """创建HyperlinkButton区域"""
        group = ThemedGroupBox("HyperlinkButton 超链接按钮")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        
        btn1 = HyperlinkButton("访问 GitHub", "https://github.com")
        layout.addWidget(btn1)
        
        btn2 = HyperlinkButton("查看文档", "https://python.org")
        layout.addWidget(btn2)
        
        link_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>"""
        btn3 = HyperlinkButton("带图标链接", "https://example.com")
        btn3.setIcon(link_icon)
        layout.addWidget(btn3)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def _create_menu_section(self):
        """创建菜单演示区域"""
        from PyQt6.QtCore import QPoint
        
        group = ThemedGroupBox("RoundMenu 右键菜单")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 说明标签
        desc = ThemedLabel("在列表项上右键可显示上下文菜单", font_role='small')
        layout.addWidget(desc)
        
        # 创建带右键菜单的列表
        list_widget = CustomListWidget()
        list_widget.setFixedHeight(120)
        list_widget.addItems([
            "文档 1.txt - 右键显示菜单",
            "文档 2.py - 右键显示菜单",
            "文档 3.json - 右键显示菜单",
            "文档 4.md - 右键显示菜单",
        ])
        
        # 设置右键菜单
        list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        def show_list_menu(pos):
            from PyQt6.QtGui import QCursor
            item = list_widget.itemAt(pos)
            if item:
                menu = RoundMenu("操作")
                menu.addAction(
                    "打开",
                    lambda: self._show_toast(f"打开: {item.text()}", ToastType.INFO),
                    shortcut="Enter"
                )
                menu.addAction(
                    "编辑",
                    lambda: self._show_toast(f"编辑: {item.text()}", ToastType.INFO),
                    shortcut="F2"
                )
                menu.addSeparator()
                menu.addAction(
                    "复制",
                    lambda: self._show_toast(f"复制: {item.text()}", ToastType.SUCCESS),
                    shortcut="Ctrl+C"
                )
                menu.addAction(
                    "剪切",
                    lambda: self._show_toast(f"剪切: {item.text()}", ToastType.INFO),
                    shortcut="Ctrl+X"
                )
                menu.addSeparator()
                menu.addAction(
                    "删除",
                    lambda: self._show_toast(f"删除: {item.text()}", ToastType.WARNING),
                    shortcut="Delete"
                )
                menu.exec(QCursor.pos())
        
        list_widget.customContextMenuRequested.connect(show_list_menu)
        layout.addWidget(list_widget)
        
        # 按钮触发菜单演示
        btn_layout = QHBoxLayout()
        
        def show_button_menu(checked):
            menu = RoundMenu("文件")
            menu.addAction("新建文件", lambda: self._show_toast("新建文件", ToastType.INFO), shortcut="Ctrl+N")
            menu.addAction("打开文件", lambda: self._show_toast("打开文件", ToastType.INFO), shortcut="Ctrl+O")
            menu.addAction("保存", lambda: self._show_toast("保存文件", ToastType.SUCCESS), shortcut="Ctrl+S")
            menu.addSeparator()
            
            # 子菜单
            recent_menu = menu.addMenu("最近文件")
            recent_menu.addAction("document1.txt", lambda: self._show_toast("打开 document1.txt", ToastType.INFO))
            recent_menu.addAction("project.py", lambda: self._show_toast("打开 project.py", ToastType.INFO))
            
            menu.addSeparator()
            menu.addAction("退出", lambda: self.close(), shortcut="Alt+F4")
            
            btn = self.sender()
            if btn:
                menu.exec(btn.mapToGlobal(QPoint(0, btn.height())))
        
        menu_btn = PrimaryPushButton("点击显示菜单")
        menu_btn.clicked.connect(show_button_menu)
        btn_layout.addWidget(menu_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_icon_widget_section(self):
        """创建 IconWidget 演示区域"""
        group = ThemedGroupBox("IconWidget 图标组件")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        size_row = ThemedWidget()
        size_layout = QHBoxLayout(size_row)
        size_layout.setContentsMargins(0, 0, 0, 0)
        
        sizes = [
            (IconSize.TINY, "TINY(12)"),
            (IconSize.SMALL, "SMALL(16)"),
            (IconSize.MEDIUM, "MEDIUM(20)"),
            (IconSize.LARGE, "LARGE(24)"),
            (IconSize.XLARGE, "XLARGE(32)"),
        ]
        
        for icon_size, label_text in sizes:
            col = ThemedWidget()
            col_layout = QVBoxLayout(col)
            col_layout.setContentsMargins(5, 0, 5, 0)
            col_layout.setSpacing(5)
            
            icon = IconWidget("Play_white", size=icon_size)
            
            label = ThemedLabel(label_text, font_role='small')
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            col_layout.addWidget(icon)
            col_layout.addWidget(label)
            size_layout.addWidget(col)
        
        size_layout.addStretch()
        layout.addWidget(size_row)
        
        color_row = ThemedWidget()
        color_layout = QHBoxLayout(color_row)
        color_layout.setContentsMargins(0, 0, 0, 0)
        
        colors = [
            (QColor(255, 255, 255), "白色"),
            (QColor(52, 152, 219), "蓝色"),
            (QColor(46, 204, 113), "绿色"),
            (QColor(231, 76, 60), "红色"),
            (QColor(241, 196, 15), "黄色"),
        ]
        
        for color, label_text in colors:
            col = ThemedWidget()
            col_layout = QVBoxLayout(col)
            col_layout.setContentsMargins(5, 0, 5, 0)
            col_layout.setSpacing(5)
            
            icon = IconWidget("Play_white", size=IconSize.LARGE, color=color)
            
            label = ThemedLabel(label_text, font_role='small')
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            col_layout.addWidget(icon)
            col_layout.addWidget(label)
            color_layout.addWidget(col)
        
        color_layout.addStretch()
        layout.addWidget(color_row)
        
        interactive_row = ThemedWidget()
        interactive_layout = QHBoxLayout(interactive_row)
        interactive_layout.setContentsMargins(0, 0, 0, 0)
        
        clickable_icon = IconWidget(
            "Play_white", 
            size=IconSize.XLARGE, 
            clickable=True, 
            hover_effect=True
        )
        clickable_icon.clicked.connect(
            lambda: self._show_toast("图标被点击!", ToastType.INFO)
        )
        
        self._click_count = 0
        self._click_label = ThemedLabel("点击次数: 0")
        
        def on_click():
            self._click_count += 1
            self._click_label.setText(f"点击次数: {self._click_count}")
        
        clickable_icon.clicked.connect(on_click)
        
        interactive_layout.addWidget(clickable_icon)
        interactive_layout.addWidget(self._click_label)
        interactive_layout.addStretch()
        
        layout.addWidget(interactive_row)
        
        icons_row = ThemedWidget()
        icons_layout = QHBoxLayout(icons_row)
        icons_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_names = [
            "Play_white", "Pause_white", "Close_white",
            "Volume_white", "Mute_white", "Setting_white"
        ]
        
        for icon_name in icon_names:
            icon = IconWidget(icon_name, size=IconSize.LARGE)
            icons_layout.addWidget(icon)
        
        icons_layout.addStretch()
        layout.addWidget(icons_row)
        
        group.setLayout(layout)
        return group
    
    def _create_mediabar_section(self):
        """创建媒体播放栏演示区域"""
        group = ThemedGroupBox("SimpleMediaPlayBar 媒体播放栏")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        media_bar = SimpleMediaPlayBar()
        media_bar.setDuration(210)
        media_bar.setPosition(0)
        
        self._media_bar = media_bar
        self._play_timer = QTimer(self)
        self._play_timer.timeout.connect(self._update_media_position)
        
        media_bar.playToggled.connect(self._on_media_play_toggled)
        media_bar.positionChanged.connect(self._on_media_position_changed)
        media_bar.volumeChanged.connect(
            lambda v: self._show_toast(f"音量: {v}%", ToastType.INFO)
        )
        media_bar.muteToggled.connect(
            lambda m: self._show_toast("静音" if m else "取消静音", ToastType.INFO)
        )
        
        info_layout = QHBoxLayout()
        self._media_status = ThemedLabel("状态: 已暂停 | 位置: 00:00 / 03:30")
        info_layout.addWidget(self._media_status)
        info_layout.addStretch()
        
        layout.addWidget(media_bar)
        layout.addLayout(info_layout)
        
        group.setLayout(layout)
        return group
    
    def _on_media_play_toggled(self, playing: bool):
        """媒体播放状态改变"""
        if playing:
            self._play_timer.start(1000)
            self._show_toast("开始播放", ToastType.SUCCESS)
        else:
            self._play_timer.stop()
            self._show_toast("暂停播放", ToastType.INFO)
        self._update_media_status()
    
    def _on_media_position_changed(self, position: int):
        """媒体位置改变"""
        self._update_media_status()
    
    def _update_media_position(self):
        """更新媒体位置（模拟播放）"""
        if self._media_bar.isPlaying():
            current = self._media_bar.position()
            duration = self._media_bar.duration()
            if current < duration:
                self._media_bar.setPosition(current + 1)
            else:
                self._media_bar.pause()
                self._media_bar.setPosition(0)
                self._show_toast("播放完成", ToastType.SUCCESS)
    
    def _update_media_status(self):
        """更新媒体状态显示"""
        status = "播放中" if self._media_bar.isPlaying() else "已暂停"
        pos = self._media_bar.position()
        dur = self._media_bar.duration()
        pos_str = f"{pos // 60:02d}:{pos % 60:02d}"
        dur_str = f"{dur // 60:02d}:{dur % 60:02d}"
        self._media_status.setText(f"状态: {status} | 位置: {pos_str} / {dur_str}")
        
    def _switch_theme(self, theme_name: str):
        """切换主题"""
        ThemeManager.instance().set_theme(theme_name)
        
    def _show_toast(self, message: str, toast_type: ToastType):
        """显示Toast通知"""
        ToastManager.get_instance().show(
            message,
            toast_type,
            duration=3000,
            position=ToastPosition.TOP_CENTER,
            parent=self
        )
        
    def _validate_email(self, text: str):
        """验证邮箱"""
        if text and '@' not in text:
            self.email_input.set_error(True)
            self.email_status.setText("请输入有效的邮箱地址")
        else:
            self.email_input.set_error(False)
            self.email_status.setText("")
            
    def _update_checkbox_status(self):
        """更新复选框状态"""
        count = sum([
            self.cb1.isChecked(),
            self.cb2.isChecked(),
            self.cb3.isChecked()
        ])
        self.checkbox_status.setText(f"已启用: {count}/3 个功能")
        
    def _animate_slider(self):
        """动画滑块到100%"""
        self.progress_slider.set_value_animated(100, 1000)
    
    def _create_pivot_section(self):
        """创建Pivot演示区域"""
        from PyQt6.QtWidgets import QStackedWidget
        
        group = ThemedGroupBox("Pivot 标签导航")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建 Pivot
        pivot = Pivot()
        pivot.addItem("首页", "home")
        pivot.addItem("设置", "settings")
        pivot.addItem("关于", "about")
        pivot.addItem("示例", "demo")
        pivot.addItem("菜单", "menu")
        
        # 创建堆叠窗口
        stack = QStackedWidget()
        stack.setFixedHeight(160)
        
        # 首页页面 - 包含按钮
        home_page = ThemedWidget()
        home_layout = QVBoxLayout(home_page)
        home_layout.setContentsMargins(10, 10, 10, 10)
        home_layout.setSpacing(8)
        
        home_label = ThemedLabel("欢迎使用 Pivot 组件！")
        home_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        home_btn_layout = QHBoxLayout()
        home_btn1 = CustomPushButton("新建文件")
        home_btn2 = CustomPushButton("打开文件")
        home_btn3 = PrimaryPushButton("保存")
        home_btn_layout.addStretch()
        home_btn_layout.addWidget(home_btn1)
        home_btn_layout.addWidget(home_btn2)
        home_btn_layout.addWidget(home_btn3)
        home_btn_layout.addStretch()
        home_layout.addWidget(home_label)
        home_layout.addLayout(home_btn_layout)
        
        # 设置页面 - 包含按钮
        settings_page = ThemedWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(10, 10, 10, 10)
        settings_layout.setSpacing(8)
        
        settings_label = ThemedLabel("设置选项")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_btn_layout = QHBoxLayout()
        settings_btn1 = CustomPushButton("通用设置")
        settings_btn2 = CustomPushButton("高级设置")
        settings_btn3 = CustomPushButton("恢复默认")
        settings_btn_layout.addStretch()
        settings_btn_layout.addWidget(settings_btn1)
        settings_btn_layout.addWidget(settings_btn2)
        settings_btn_layout.addWidget(settings_btn3)
        settings_btn_layout.addStretch()
        settings_layout.addWidget(settings_label)
        settings_layout.addLayout(settings_btn_layout)
        
        # 关于页面 - 包含按钮
        about_page = ThemedWidget()
        about_layout = QVBoxLayout(about_page)
        about_layout.setContentsMargins(10, 10, 10, 10)
        about_layout.setSpacing(8)
        
        about_label = ThemedLabel("Pivot 组件 v1.0")
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_btn_layout = QHBoxLayout()
        about_btn1 = CustomPushButton("查看文档")
        about_btn2 = PrimaryPushButton("检查更新")
        about_btn_layout.addStretch()
        about_btn_layout.addWidget(about_btn1)
        about_btn_layout.addWidget(about_btn2)
        about_btn_layout.addStretch()
        about_layout.addWidget(about_label)
        about_layout.addLayout(about_btn_layout)
        
        # 示例页面 - 完整表单示例
        demo_page = ThemedWidget()
        demo_layout = QVBoxLayout(demo_page)
        demo_layout.setContentsMargins(10, 5, 10, 5)
        demo_layout.setSpacing(6)
        
        # 表单行
        form_layout = QHBoxLayout()
        
        # 左侧：输入框
        input_widget = ThemedWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(4)
        
        name_input = ModernLineEdit()
        name_input.set_placeholder_text("用户名")
        email_input = ModernLineEdit()
        email_input.set_placeholder_text("邮箱地址")
        
        input_layout.addWidget(name_input)
        input_layout.addWidget(email_input)
        
        # 右侧：复选框和按钮
        right_widget = ThemedWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        
        cb_row = QHBoxLayout()
        cb1 = CustomCheckBox("记住我")
        cb1.setChecked(True)
        cb2 = CustomCheckBox("订阅")
        cb_row.addWidget(cb1)
        cb_row.addWidget(cb2)
        cb_row.addStretch()
        
        btn_row = QHBoxLayout()
        submit_btn = PrimaryPushButton("提交")
        reset_btn = CustomPushButton("重置")
        btn_row.addWidget(submit_btn)
        btn_row.addWidget(reset_btn)
        btn_row.addStretch()
        
        right_layout.addLayout(cb_row)
        right_layout.addLayout(btn_row)
        
        form_layout.addWidget(input_widget, 1)
        form_layout.addWidget(right_widget, 1)
        
        demo_layout.addLayout(form_layout)
        
        # 菜单页面 - 右键菜单示例
        menu_page = ThemedWidget()
        menu_layout = QVBoxLayout(menu_page)
        menu_layout.setContentsMargins(10, 5, 10, 5)
        menu_layout.setSpacing(6)
        
        menu_label = ThemedLabel("右键点击下方区域显示菜单")
        menu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建一个可右键的区域
        menu_area = ThemedWidget()
        menu_area.setFixedHeight(60)
        menu_area.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        area_layout = QVBoxLayout(menu_area)
        area_layout.setContentsMargins(10, 10, 10, 10)
        area_hint = ThemedLabel("右键此处...", font_role='small')
        area_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        area_layout.addWidget(area_hint)
        
        # 右键菜单处理
        def show_demo_menu(pos):
            from PyQt6.QtGui import QCursor
            menu = RoundMenu("操作")
            menu.addAction("复制", lambda: self._show_toast("复制", ToastType.INFO), shortcut="Ctrl+C")
            menu.addAction("剪切", lambda: self._show_toast("剪切", ToastType.INFO), shortcut="Ctrl+X")
            menu.addAction("粘贴", lambda: self._show_toast("粘贴", ToastType.INFO), shortcut="Ctrl+V")
            menu.addSeparator()
            menu.addAction("全选", lambda: self._show_toast("全选", ToastType.INFO), shortcut="Ctrl+A")
            menu.exec(QCursor.pos())
        
        menu_area.customContextMenuRequested.connect(show_demo_menu)
        
        menu_layout.addWidget(menu_label)
        menu_layout.addWidget(menu_area)
        
        stack.addWidget(home_page)
        stack.addWidget(settings_page)
        stack.addWidget(about_page)
        stack.addWidget(demo_page)
        stack.addWidget(menu_page)
        
        # 连接信号
        def on_pivot_changed(key: str):
            index_map = {"home": 0, "settings": 1, "about": 2, "demo": 3, "menu": 4}
            if key in index_map:
                stack.setCurrentIndex(index_map[key])
        
        pivot.currentChanged.connect(on_pivot_changed)
        
        # 提示信息
        hint = ThemedLabel("提示: 使用左右方向键可切换标签", font_role='small')
        
        layout.addWidget(pivot)
        layout.addWidget(stack)
        layout.addWidget(hint)
        
        group.setLayout(layout)
        return group
    
    def _create_tabbar_demo_page(self):
        """创建TabBar演示页面"""
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        page = ThemedWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_tabbar_section())
        layout.addWidget(self._create_tabwidget_section())
        layout.addStretch()
        
        scroll.setWidget(page)
        return scroll
    
    def _create_tabbar_section(self):
        """创建TabBar演示区域"""
        group = ThemedGroupBox("TabBar 标签栏")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        tab_bar = TabBar()
        tab_bar.addTab("首页", "home", closable=False)
        tab_bar.addTab("文档", "docs")
        tab_bar.addTab("设置", "settings")
        tab_bar.addTab("关于", "about")
        
        self._tabbar_status = ThemedLabel("当前选中: 首页")
        tab_bar.currentChanged.connect(
            lambda key: self._tabbar_status.setText(f"当前选中: {tab_bar.tab(key).text() if tab_bar.tab(key) else 'None'}")
        )
        
        tab_bar.tabCloseRequested.connect(tab_bar.removeTab)
        
        btn_layout = QHBoxLayout()
        add_btn = CustomPushButton("添加标签")
        add_btn.clicked.connect(lambda: tab_bar.addTab(f"新标签 {tab_bar.count() + 1}", f"new_{tab_bar.count() + 1}"))
        
        remove_btn = CustomPushButton("删除当前")
        remove_btn.clicked.connect(lambda: tab_bar.removeTab(tab_bar.currentKey()) if tab_bar.currentKey() else None)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        
        layout.addWidget(tab_bar)
        layout.addWidget(self._tabbar_status)
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_tabwidget_section(self):
        """创建TabWidget演示区域"""
        group = ThemedGroupBox("TabWidget 标签页组件")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        tab_widget = TabWidget()
        tab_widget.setFixedHeight(200)
        
        page1 = ThemedWidget()
        page1_layout = QVBoxLayout(page1)
        page1_layout.setContentsMargins(10, 10, 10, 10)
        page1_label = ThemedLabel("这是首页内容区域")
        page1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page1_btn = PrimaryPushButton("首页操作")
        page1_layout.addWidget(page1_label)
        page1_layout.addWidget(page1_btn)
        page1_layout.addStretch()
        
        page2 = ThemedWidget()
        page2_layout = QVBoxLayout(page2)
        page2_layout.setContentsMargins(10, 10, 10, 10)
        page2_label = ThemedLabel("这是文档页面")
        page2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page2_input = ModernLineEdit()
        page2_input.set_placeholder_text("输入文档名称...")
        page2_layout.addWidget(page2_label)
        page2_layout.addWidget(page2_input)
        page2_layout.addStretch()
        
        page3 = ThemedWidget()
        page3_layout = QVBoxLayout(page3)
        page3_layout.setContentsMargins(10, 10, 10, 10)
        page3_label = ThemedLabel("设置选项")
        page3_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page3_cb1 = CustomCheckBox("启用功能A")
        page3_cb2 = CustomCheckBox("启用功能B")
        page3_cb1.setChecked(True)
        page3_layout.addWidget(page3_label)
        page3_layout.addWidget(page3_cb1)
        page3_layout.addWidget(page3_cb2)
        page3_layout.addStretch()
        
        tab_widget.addTab(page1, "首页", "home", closable=False)
        tab_widget.addTab(page2, "文档", "docs")
        tab_widget.addTab(page3, "设置", "settings")
        
        hint = ThemedLabel("提示: 点击标签上的 × 可关闭标签，使用左右方向键切换", font_role='small')
        
        layout.addWidget(tab_widget)
        layout.addWidget(hint)
        
        group.setLayout(layout)
        return group


def main():
    """运行验证Demo"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    ToastManager.prewarm()
    
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict('dark', DARK_THEME)
    theme_mgr.register_theme_dict('light', LIGHT_THEME)
    theme_mgr.register_theme_dict('default', DEFAULT_THEME)
    theme_mgr.set_theme('dark')
    
    splash = SplashScreen()
    splash.setTitle("PyQt 重构组件验证")
    splash.setSubtitle("正在初始化...")
    splash.show_and_fade_in()
    
    progress = [0]
    progress_timer = QTimer()
    
    def update_progress():
        progress[0] += 5
        splash.setProgress(progress[0])
        
        if progress[0] < 30:
            splash.setSubtitle("正在加载主题...")
        elif progress[0] < 60:
            splash.setSubtitle("正在初始化组件...")
        elif progress[0] < 90:
            splash.setSubtitle("正在准备界面...")
        else:
            splash.setSubtitle("即将完成...")
        
        if progress[0] >= 100:
            progress_timer.stop()
            splash.finish(window)
    
    window = RefactoredComponentsDemo()
    
    screen = app.primaryScreen()
    screen_geometry = screen.availableGeometry()
    window_geometry = window.frameGeometry()
    center_point = screen_geometry.center()
    window_geometry.moveCenter(center_point)
    window.move(window_geometry.topLeft())
    
    progress_timer.timeout.connect(update_progress)
    progress_timer.start(50)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
