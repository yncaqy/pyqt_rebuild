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

from PyQt6.QtCore import Qt, QTimer, QDate, QTime
from PyQt6.QtGui import QIntValidator, QStandardItemModel, QStandardItem, QColor
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QAbstractItemView, QStackedWidget, QWidget

from containers.frameless_window import FramelessWindow
from components.buttons.custom_push_button import CustomPushButton
from components.buttons.tool_button import ToolButton
from components.inputs.modern_line_edit import ModernLineEdit
from components.inputs.plain_text_edit import PlainTextEdit
from components.inputs.text_edit import TextEdit
from components.inputs.spin_box import SpinBox, DoubleSpinBox
from components.buttons.primary_push_button import PrimaryPushButton
from components.buttons.hyperlink_button import HyperlinkButton
from components.buttons.toggle_push_button import TogglePushButton
from components.buttons.pill_push_button import PillPushButton
from components.buttons.dropdown_push_button import DropDownPushButton
from components.buttons.radio_button import RadioButton
from components.buttons.switch_button import SwitchButton
from components.widgets.combo_box import ComboBox
from components.widgets.editable_combo_box import EditableComboBox
from components.widgets.date_picker import DatePicker
from components.widgets.time_picker import TimePicker
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
from components.containers.splitter import Splitter, AnimatedSplitter
from components.dialogs.message_box import MessageBox
from components.dialogs.color_dialog import ColorDialog
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
from components.widgets.drop_down_color_palette import DropDownColorPalette
from components.widgets.drop_down_color_picker import DropDownColorPicker
from components.widgets.screen_color_picker import ScreenColorPicker
from components.widgets.drop_single_file_widget import DropSingleFileWidget
from components.statusbar.status_bar import StatusBar
from components.navigation.breadcrumb_bar import BreadcrumbBar, BreadcrumbSeparator
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
        pivot.addItem("文件选择", "file_picker")
        pivot.addItem("状态栏", "statusbar")
        pivot.addItem("面包屑", "breadcrumb")
        
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
        
        # 文件选择页面
        file_picker_page = self._create_file_picker_page()
        stack.addWidget(file_picker_page)
        
        # 状态栏页面
        statusbar_page = self._create_statusbar_page()
        stack.addWidget(statusbar_page)
        
        # 面包屑页面
        breadcrumb_page = self._create_breadcrumb_page()
        stack.addWidget(breadcrumb_page)
        
        # 连接信号
        def on_pivot_changed(key: str):
            index_map = {"basic": 0, "advanced": 1, "icons": 2, "pivot_demo": 3, "tabbar_demo": 4, "file_picker": 5, "statusbar": 6, "breadcrumb": 7}
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
        layout.addWidget(self._create_spinbox_section())
        layout.addWidget(self._create_plain_text_edit_section())
        layout.addWidget(self._create_rich_text_edit_section())
        layout.addWidget(self._create_checkbox_section())
        layout.addWidget(self._create_radio_button_section())
        layout.addWidget(self._create_switch_section())
        layout.addWidget(self._create_date_picker_section())
        layout.addWidget(self._create_time_picker_section())
        layout.addWidget(self._create_progress_section())
        layout.addWidget(self._create_slider_section())
        layout.addWidget(self._create_toast_section())
        layout.addWidget(self._create_messagebox_section())
        layout.addWidget(self._create_colordialog_section())
        layout.addWidget(self._create_color_palette_section())
        layout.addWidget(self._create_color_picker_section())
        layout.addWidget(self._create_screen_color_picker_section())
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
        layout.addWidget(self._create_splitter_section())
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
    
    def _create_plain_text_edit_section(self):
        """创建纯文本编辑器区域"""
        group = ThemedGroupBox("PlainTextEdit 纯文本编辑器")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        self.plain_text_edit = PlainTextEdit()
        self.plain_text_edit.set_placeholder_text("在此输入纯文本内容...\n支持行号显示、语法高亮等功能")
        self.plain_text_edit.setMinimumHeight(150)
        
        btn_layout = QHBoxLayout()
        
        line_num_btn = CustomPushButton("显示行号")
        line_num_btn.clicked.connect(self._toggle_line_numbers)
        
        highlight_btn = CustomPushButton("高亮当前行")
        highlight_btn.clicked.connect(self._toggle_highlight_line)
        
        clear_btn = CustomPushButton("清空")
        clear_btn.clicked.connect(self.plain_text_edit.clear_text)
        
        word_count_btn = CustomPushButton("字数统计")
        word_count_btn.clicked.connect(self._show_word_count)
        
        btn_layout.addWidget(line_num_btn)
        btn_layout.addWidget(highlight_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(word_count_btn)
        btn_layout.addStretch()
        
        self.plain_text_status = ThemedLabel("行: 1, 列: 1 | 字符: 0 | 单词: 0")
        self.plain_text_edit.cursor_position_changed.connect(self._update_plain_text_status)
        self.plain_text_edit.text_changed.connect(self._update_plain_text_status)
        
        layout.addWidget(self.plain_text_edit)
        layout.addLayout(btn_layout)
        layout.addWidget(self.plain_text_status)
        
        group.setLayout(layout)
        return group
    
    def _create_spinbox_section(self):
        """创建数值输入区域"""
        group = ThemedGroupBox("SpinBox 数值输入组件")
        container = ThemedWidget()
        layout = QGridLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        label1 = ThemedLabel("整数输入:")
        self.int_spin = SpinBox()
        self.int_spin.setRange(0, 100)
        self.int_spin.setValue(50)
        self.int_spin.setSingleStep(1)
        self.int_spin.valueChanged.connect(lambda v: self._on_spinbox_changed("int", v))
        
        label2 = ThemedLabel("带单位:")
        self.unit_spin = SpinBox()
        self.unit_spin.setRange(0, 1000)
        self.unit_spin.setValue(100)
        self.unit_spin.setSuffix(" px")
        self.unit_spin.valueChanged.connect(lambda v: self._on_spinbox_changed("unit", v))
        
        label3 = ThemedLabel("浮点数:")
        self.double_spin = DoubleSpinBox()
        self.double_spin.setRange(0.0, 100.0)
        self.double_spin.setValue(50.5)
        self.double_spin.setDecimals(2)
        self.double_spin.setSingleStep(0.1)
        self.double_spin.valueChanged.connect(lambda v: self._on_spinbox_changed("double", v))
        
        label4 = ThemedLabel("百分比:")
        self.percent_spin = DoubleSpinBox()
        self.percent_spin.setRange(0.0, 100.0)
        self.percent_spin.setValue(75.0)
        self.percent_spin.setDecimals(1)
        self.percent_spin.setSuffix(" %")
        self.percent_spin.valueChanged.connect(lambda v: self._on_spinbox_changed("percent", v))
        
        label5 = ThemedLabel("货币:")
        self.currency_spin = DoubleSpinBox()
        self.currency_spin.setRange(0.0, 99999.99)
        self.currency_spin.setValue(1234.56)
        self.currency_spin.setDecimals(2)
        self.currency_spin.setPrefix("¥ ")
        self.currency_spin.setSingleStep(10)
        self.currency_spin.valueChanged.connect(lambda v: self._on_spinbox_changed("currency", v))
        
        self.spinbox_status = ThemedLabel("当前值: 整数=50, 浮点=50.5")
        
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.int_spin, 0, 1)
        layout.addWidget(label2, 0, 2)
        layout.addWidget(self.unit_spin, 0, 3)
        layout.addWidget(label3, 1, 0)
        layout.addWidget(self.double_spin, 1, 1)
        layout.addWidget(label4, 1, 2)
        layout.addWidget(self.percent_spin, 1, 3)
        layout.addWidget(label5, 2, 0)
        layout.addWidget(self.currency_spin, 2, 1, 1, 3)
        layout.addWidget(self.spinbox_status, 3, 0, 1, 4)
        
        group.setLayout(layout)
        return group
    
    def _on_spinbox_changed(self, name, value):
        status_text = f"当前值: 整数={self.int_spin.value()}, 浮点={self.double_spin.value():.2f}, 百分比={self.percent_spin.value():.1f}%"
        self.spinbox_status.setText(status_text)
    
    def _create_rich_text_edit_section(self):
        """创建富文本编辑器区域"""
        group = ThemedGroupBox("TextEditWithToolbar 带工具栏富文本编辑器")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        from components.inputs.text_edit_with_toolbar import TextEditWithToolbar
        self.rich_text_edit = TextEditWithToolbar()
        self.rich_text_edit.set_placeholder_text("在此输入富文本内容...\n工具栏已集成在顶部，支持格式化、颜色、列表等功能")
        self.rich_text_edit.setMinimumHeight(200)
        
        self.rich_text_status = ThemedLabel("格式: 普通 | 字体: 12pt")
        self.rich_text_edit.format_changed.connect(self._update_rich_text_status)
        
        layout.addWidget(self.rich_text_edit)
        layout.addWidget(self.rich_text_status)
        
        group.setLayout(layout)
        return group
    
    def _toggle_line_numbers(self):
        """切换行号显示"""
        current = self.plain_text_edit.is_line_numbers_visible()
        self.plain_text_edit.set_line_numbers_visible(not current)
        status = "开启" if not current else "关闭"
        self._show_toast(f"行号显示已{status}", ToastType.INFO)
    
    def _toggle_highlight_line(self):
        """切换当前行高亮"""
        current = self.plain_text_edit.is_highlight_current_line()
        self.plain_text_edit.set_highlight_current_line(not current)
        status = "开启" if not current else "关闭"
        self._show_toast(f"当前行高亮已{status}", ToastType.INFO)
    
    def _show_word_count(self):
        """显示字数统计"""
        char_count = self.plain_text_edit.get_char_count()
        word_count = self.plain_text_edit.get_word_count()
        line_count = self.plain_text_edit.get_line_count()
        self._show_toast(f"字符: {char_count} | 单词: {word_count} | 行数: {line_count}", ToastType.INFO)
    
    def _update_plain_text_status(self, *args):
        """更新纯文本编辑器状态"""
        line = self.plain_text_edit.get_current_line()
        col = self.plain_text_edit.get_current_column()
        chars = self.plain_text_edit.get_char_count()
        words = self.plain_text_edit.get_word_count()
        self.plain_text_status.setText(f"行: {line}, 列: {col} | 字符: {chars} | 单词: {words}")
    
    def _choose_text_color(self):
        """选择文字颜色"""
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self.rich_text_edit.set_text_color(color)
    
    def _choose_bg_color(self):
        """选择背景颜色"""
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self.rich_text_edit.set_background_color(color)
    
    def _insert_link(self):
        """插入链接"""
        from PyQt6.QtWidgets import QInputDialog
        url, ok = QInputDialog.getText(self, "插入链接", "请输入URL:", text="https://")
        if ok and url:
            selected = self.rich_text_edit.get_selected_text()
            self.rich_text_edit.insert_hyperlink(url, selected if selected else url)
    
    def _update_rich_text_status(self, state):
        """更新富文本编辑器状态"""
        formats = []
        if state.bold:
            formats.append("粗体")
        if state.italic:
            formats.append("斜体")
        if state.underline:
            formats.append("下划线")
        
        format_str = ", ".join(formats) if formats else "普通"
        self.rich_text_status.setText(f"格式: {format_str} | 字体: {int(state.font_size)}pt")
    
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
        
    def _create_switch_section(self):
        """创建开关按钮区域"""
        group = ThemedGroupBox("SwitchButton 开关按钮")
        container = ThemedWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        row1 = ThemedWidget()
        layout1 = QHBoxLayout(row1)
        layout1.setContentsMargins(0, 0, 0, 0)
        
        self.switch1 = SwitchButton()
        self.switch1.setChecked(True)
        self.switch1.checkedChanged.connect(lambda checked: self._on_switch_changed("开关1", checked))
        
        self.switch2 = SwitchButton()
        self.switch2.checkedChanged.connect(lambda checked: self._on_switch_changed("开关2", checked))
        
        self.switch3 = SwitchButton()
        self.switch3.setEnabled(False)
        
        layout1.addWidget(ThemedLabel("开启:"))
        layout1.addWidget(self.switch1)
        layout1.addSpacing(20)
        layout1.addWidget(ThemedLabel("关闭:"))
        layout1.addWidget(self.switch2)
        layout1.addSpacing(20)
        layout1.addWidget(ThemedLabel("禁用:"))
        layout1.addWidget(self.switch3)
        layout1.addStretch()
        
        self.switch_status = ThemedLabel("开关1: 开启")
        
        main_layout.addWidget(row1)
        main_layout.addWidget(self.switch_status)
        
        group.setLayout(main_layout)
        return group
    
    def _on_switch_changed(self, name: str, checked: bool):
        """处理开关状态变化"""
        status = "开启" if checked else "关闭"
        self.switch_status.setText(f"{name}: {status}")
        
    def _create_date_picker_section(self):
        """创建日期选择器区域"""
        group = ThemedGroupBox("DatePicker 日期选择器")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.date_picker1 = DatePicker()
        self.date_picker1.setDate(QDate.currentDate())
        self.date_picker1.dateChanged.connect(lambda date: self._on_date_changed("日期选择器1", date))
        
        self.date_picker2 = DatePicker()
        self.date_picker2.setDate(QDate.currentDate().addDays(7))
        self.date_picker2.dateChanged.connect(lambda date: self._on_date_changed("日期选择器2", date))
        
        self.date_picker3 = DatePicker()
        self.date_picker3.setDate(QDate.currentDate())
        self.date_picker3.setEnabled(False)
        
        layout.addWidget(ThemedLabel("今天:"))
        layout.addWidget(self.date_picker1)
        layout.addSpacing(20)
        layout.addWidget(ThemedLabel("一周后:"))
        layout.addWidget(self.date_picker2)
        layout.addSpacing(20)
        layout.addWidget(ThemedLabel("禁用:"))
        layout.addWidget(self.date_picker3)
        layout.addStretch()
        
        self.date_status = ThemedLabel(f"选择日期: {self.date_picker1.date().toString('yyyy-MM-dd')}")
        
        main_layout = QVBoxLayout(group)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        main_layout.addWidget(self.date_status)
        
        return group
    
    def _on_date_changed(self, name: str, date: QDate):
        """处理日期变化"""
        self.date_status.setText(f"{name} 选择日期: {date.toString('yyyy-MM-dd')}")
    
    def _create_time_picker_section(self):
        """创建时间选择器区域"""
        group = ThemedGroupBox("TimePicker 时间选择器")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.time_picker1 = TimePicker()
        self.time_picker1.setTime(QTime.currentTime())
        self.time_picker1.timeChanged.connect(lambda t: self._on_time_changed("时间选择器1", t))
        
        self.time_picker2 = TimePicker()
        self.time_picker2.setTime(QTime(18, 30))
        self.time_picker2.timeChanged.connect(lambda t: self._on_time_changed("时间选择器2", t))
        
        self.time_picker3 = TimePicker()
        self.time_picker3.setTime(QTime.currentTime())
        self.time_picker3.setEnabled(False)
        
        layout.addWidget(ThemedLabel("当前时间:"))
        layout.addWidget(self.time_picker1)
        layout.addSpacing(20)
        layout.addWidget(ThemedLabel("18:30:"))
        layout.addWidget(self.time_picker2)
        layout.addSpacing(20)
        layout.addWidget(ThemedLabel("禁用:"))
        layout.addWidget(self.time_picker3)
        layout.addStretch()
        
        self.time_status = ThemedLabel(f"选择时间: {self.time_picker1.time().toString('HH:mm')}")
        
        main_layout = QVBoxLayout(group)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        main_layout.addWidget(self.time_status)
        
        return group
    
    def _on_time_changed(self, name: str, time: QTime):
        """处理时间变化"""
        self.time_status.setText(f"{name} 选择时间: {time.toString('HH:mm')}")
        
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
    
    def _create_colordialog_section(self):
        """创建ColorDialog区域"""
        group = ThemedGroupBox("ColorDialog 颜色选择对话框")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        btn_layout = QHBoxLayout()
        
        self._color_preview = QWidget()
        self._color_preview.setFixedSize(40, 40)
        self._color_preview.setStyleSheet("background-color: #FF0000; border-radius: 4px;")
        
        self._color_label = ThemedLabel("当前颜色: #FF0000")
        
        color_btn = CustomPushButton("选择颜色")
        color_btn.clicked.connect(self._show_color_dialog)
        
        btn_layout.addWidget(self._color_preview)
        btn_layout.addWidget(self._color_label)
        btn_layout.addWidget(color_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
    
    def _show_color_dialog(self):
        dialog = ColorDialog(self, "选择颜色", QColor(self._color_preview.styleSheet().split(':')[1].split(';')[0].strip()))
        dialog.colorChanged.connect(self._on_color_changed)
        result = dialog.exec()
        if result == ColorDialog.Accepted:
            color = dialog.get_color()
            self._show_toast(f"最终选择: {color.name()}", ToastType.SUCCESS)
        dialog.cleanup()
    
    def _on_color_changed(self, color: QColor):
        self._color_preview.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")
        self._color_label.setText(f"当前颜色: {color.name()}")
    
    def _create_color_palette_section(self):
        """创建DropDownColorPalette区域"""
        group = ThemedGroupBox("DropDownColorPalette 下拉颜色面板")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self._palette_preview = QWidget()
        self._palette_preview.setFixedSize(32, 32)
        self._palette_preview.setStyleSheet("background-color: #0078D4; border-radius: 4px;")
        
        self._palette_label = ThemedLabel("当前颜色: #0078D4")
        
        self._color_palette = DropDownColorPalette()
        self._color_palette.setCurrentColor(QColor("#0078D4"))
        self._color_palette.colorChanged.connect(self._on_palette_color_changed)
        
        layout.addWidget(self._color_palette)
        layout.addWidget(self._palette_preview)
        layout.addWidget(self._palette_label)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _on_palette_color_changed(self, color: QColor):
        self._palette_preview.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")
        self._palette_label.setText(f"当前颜色: {color.name()}")
        self._show_toast(f"选择颜色: {color.name()}", ToastType.INFO)
    
    def _create_color_picker_section(self):
        """创建DropDownColorPicker区域"""
        group = ThemedGroupBox("DropDownColorPicker 下拉颜色选择器")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self._picker_preview = QWidget()
        self._picker_preview.setFixedSize(32, 32)
        self._picker_preview.setStyleSheet("background-color: #FF5722; border-radius: 4px;")
        
        self._picker_label = ThemedLabel("当前颜色: #FF5722")
        
        self._color_picker = DropDownColorPicker()
        self._color_picker.setCurrentColor(QColor("#FF5722"))
        self._color_picker.colorChanged.connect(self._on_picker_color_changed)
        
        layout.addWidget(self._color_picker)
        layout.addWidget(self._picker_preview)
        layout.addWidget(self._picker_label)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _on_picker_color_changed(self, color: QColor):
        self._picker_preview.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")
        self._picker_label.setText(f"当前颜色: {color.name()}")
        self._show_toast(f"选择颜色: {color.name()}", ToastType.INFO)
    
    def _create_screen_color_picker_section(self):
        """创建ScreenColorPicker区域"""
        group = ThemedGroupBox("ScreenColorPicker 屏幕颜色拾取器")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        picker_row = QHBoxLayout()
        picker_row.setSpacing(12)
        
        self._screen_picker = ScreenColorPicker()
        self._screen_picker.colorPicked.connect(self._on_screen_color_picked)
        
        self._screen_picker_preview = QWidget()
        self._screen_picker_preview.setFixedSize(32, 32)
        self._screen_picker_preview.setStyleSheet("background-color: #FFFFFF; border-radius: 4px;")
        
        self._screen_picker_label = ThemedLabel("点击按钮开始拾取屏幕颜色")
        
        picker_row.addWidget(self._screen_picker)
        picker_row.addWidget(self._screen_picker_preview)
        picker_row.addWidget(self._screen_picker_label)
        picker_row.addStretch()
        
        layout.addLayout(picker_row)
        
        help_label = ThemedLabel("提示: 点击按钮后移动鼠标到屏幕任意位置，点击左键拾取颜色，按 ESC 取消")
        help_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(help_label)
        
        group.setLayout(layout)
        return group
    
    def _on_screen_color_picked(self, color: QColor):
        self._screen_picker_preview.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")
        self._screen_picker_label.setText(f"拾取颜色: {color.name().upper()}")
        self._show_toast(f"拾取颜色: {color.name().upper()}", ToastType.INFO)
    
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
    
    def _create_splitter_section(self):
        """创建Splitter分割面板区域"""
        group = ThemedGroupBox("Splitter 分割面板组件")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        h_label = ThemedLabel("水平分割:")
        h_splitter = Splitter(Qt.Orientation.Horizontal)
        
        left_panel = ThemedWidget()
        left_panel.setStyleSheet("background-color: rgba(52, 152, 219, 0.2); border-radius: 4px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.addWidget(ThemedLabel("左侧面板"))
        left_info = ThemedLabel("可拖动分隔条调整大小")
        left_info.setStyleSheet("color: gray;")
        left_layout.addWidget(left_info)
        left_layout.addStretch()
        
        right_panel = ThemedWidget()
        right_panel.setStyleSheet("background-color: rgba(46, 204, 113, 0.2); border-radius: 4px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.addWidget(ThemedLabel("右侧面板"))
        right_info = ThemedLabel("最小尺寸: 100px")
        right_info.setStyleSheet("color: gray;")
        right_layout.addWidget(right_info)
        right_layout.addStretch()
        
        h_splitter.addWidget(left_panel, 100)
        h_splitter.addWidget(right_panel, 100)
        h_splitter.setSizes([300, 300])
        h_splitter.setMinimumHeight(120)
        
        v_label = ThemedLabel("垂直分割:")
        v_splitter = Splitter(Qt.Orientation.Vertical)
        
        top_panel = ThemedWidget()
        top_panel.setStyleSheet("background-color: rgba(155, 89, 182, 0.2); border-radius: 4px;")
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.addWidget(ThemedLabel("顶部面板"))
        top_layout.addStretch()
        
        bottom_panel = ThemedWidget()
        bottom_panel.setStyleSheet("background-color: rgba(241, 196, 15, 0.2); border-radius: 4px;")
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        bottom_layout.addWidget(ThemedLabel("底部面板"))
        bottom_layout.addStretch()
        
        v_splitter.addWidget(top_panel, 80)
        v_splitter.addWidget(bottom_panel, 80)
        v_splitter.setMinimumHeight(150)
        
        self._splitter_status = ThemedLabel("拖动分隔条查看效果")
        h_splitter.splitterMoved.connect(lambda idx, pos: self._on_splitter_moved("水平", idx, pos))
        v_splitter.splitterMoved.connect(lambda idx, pos: self._on_splitter_moved("垂直", idx, pos))
        
        layout.addWidget(h_label)
        layout.addWidget(h_splitter)
        layout.addWidget(v_label)
        layout.addWidget(v_splitter)
        layout.addWidget(self._splitter_status)
        
        group.setLayout(layout)
        return group
    
    def _on_splitter_moved(self, splitter_type, index, pos):
        self._splitter_status.setText(f"{splitter_type}分割: 分隔条 {index} 移动了 {pos} 像素")
    
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

    def _create_file_picker_page(self):
        """创建文件选择演示页面"""
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        page = ThemedWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_file_picker_section())
        layout.addStretch()
        
        scroll.setWidget(page)
        return scroll
    
    def _create_statusbar_page(self):
        """创建状态栏演示页面"""
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        page = ThemedWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_statusbar_section())
        layout.addStretch()
        
        scroll.setWidget(page)
        return scroll
    
    def _create_statusbar_section(self):
        """创建状态栏演示区域"""
        group = ThemedGroupBox("StatusBar 状态栏组件")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        demo_group = ThemedGroupBox("状态栏演示")
        demo_layout = QVBoxLayout(demo_group)
        demo_layout.setContentsMargins(5, 5, 5, 5)
        
        self._status_bar = StatusBar()
        self._status_bar.show_time(True)
        self._status_bar.show_battery(True)
        self._status_bar.show_network(True)
        self._status_bar.show_notification(True)
        self._status_bar.set_notification_count(3)
        demo_layout.addWidget(self._status_bar)
        
        control_layout = QHBoxLayout()
        
        time_cb = CustomCheckBox("显示时间")
        time_cb.setChecked(True)
        time_cb.stateChanged.connect(lambda s: self._status_bar.show_time(s == Qt.CheckState.Checked.value))
        control_layout.addWidget(time_cb)
        
        battery_cb = CustomCheckBox("显示电池")
        battery_cb.setChecked(True)
        battery_cb.stateChanged.connect(lambda s: self._status_bar.show_battery(s == Qt.CheckState.Checked.value))
        control_layout.addWidget(battery_cb)
        
        network_cb = CustomCheckBox("显示网络")
        network_cb.setChecked(True)
        network_cb.stateChanged.connect(lambda s: self._status_bar.show_network(s == Qt.CheckState.Checked.value))
        control_layout.addWidget(network_cb)
        
        notification_cb = CustomCheckBox("显示通知")
        notification_cb.setChecked(True)
        notification_cb.stateChanged.connect(lambda s: self._status_bar.show_notification(s == Qt.CheckState.Checked.value))
        control_layout.addWidget(notification_cb)
        
        demo_layout.addLayout(control_layout)
        
        battery_layout = QHBoxLayout()
        
        ThemedLabel("电池电量:").setFixedWidth(70)
        battery_layout.addWidget(ThemedLabel("电池电量:"))
        
        self._battery_slider = AnimatedSlider()
        self._battery_slider.setOrientation(Qt.Orientation.Horizontal)
        self._battery_slider.setRange(0, 100)
        self._battery_slider.setValue(100)
        self._battery_slider.valueChanged.connect(self._status_bar.set_battery_level)
        battery_layout.addWidget(self._battery_slider)
        
        charging_cb = CustomCheckBox("充电中")
        charging_cb.stateChanged.connect(lambda s: self._status_bar.set_charging(s == Qt.CheckState.Checked.value))
        battery_layout.addWidget(charging_cb)
        
        demo_layout.addLayout(battery_layout)
        
        notification_layout = QHBoxLayout()
        
        ThemedLabel("通知数量:").setFixedWidth(70)
        notification_layout.addWidget(ThemedLabel("通知数量:"))
        
        self._notification_spin = SpinBox()
        self._notification_spin.setRange(0, 99)
        self._notification_spin.setValue(3)
        self._notification_spin.valueChanged.connect(self._status_bar.set_notification_count)
        notification_layout.addWidget(self._notification_spin)
        
        clear_btn = CustomPushButton("清除通知")
        clear_btn.clicked.connect(self._status_bar.clear_notifications)
        clear_btn.clicked.connect(lambda: self._notification_spin.setValue(0))
        notification_layout.addWidget(clear_btn)
        
        demo_layout.addLayout(notification_layout)
        
        layout.addWidget(demo_group)
        
        group.setLayout(layout)
        return group
    
    def _create_file_picker_section(self):
        """创建文件选择演示区域"""
        group = ThemedGroupBox("DropSingleFileWidget 文件选择组件")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        default_group = ThemedGroupBox("默认文件选择器（支持多选）")
        default_layout = QVBoxLayout(default_group)
        default_layout.setContentsMargins(5, 5, 5, 5)
        
        self._default_file_widget = DropSingleFileWidget()
        self._default_file_widget.setMinimumHeight(150)
        self._default_file_widget.setMultiSelect(True)
        self._default_file_widget.fileSelected.connect(self._on_file_selected)
        self._default_file_widget.filesSelected.connect(self._on_files_selected)
        self._default_file_widget.fileCleared.connect(self._on_file_cleared)
        self._default_file_widget.errorOccurred.connect(self._on_file_error)
        
        default_layout.addWidget(self._default_file_widget)
        
        image_group = ThemedGroupBox("图片文件选择器（支持多选，PNG, JPG, JPEG）")
        image_layout = QVBoxLayout(image_group)
        image_layout.setContentsMargins(5, 5, 5, 5)
        
        self._image_file_widget = DropSingleFileWidget(
            title="拖拽图片到此处",
            subtitle="支持 PNG, JPG, JPEG 格式"
        )
        self._image_file_widget.setMinimumHeight(150)
        self._image_file_widget.setFilter(["*.png", "*.jpg", "*.jpeg"])
        self._image_file_widget.setMultiSelect(True)
        self._image_file_widget.fileSelected.connect(self._on_file_selected)
        self._image_file_widget.filesSelected.connect(self._on_files_selected)
        self._image_file_widget.errorOccurred.connect(self._on_file_error)
        
        image_layout.addWidget(self._image_file_widget)
        
        info_layout = QHBoxLayout()
        self._file_path_label = ThemedLabel("文件路径: 未选择")
        self._file_path_label.setWordWrap(True)
        
        clear_btn = CustomPushButton("清除文件")
        clear_btn.clicked.connect(self._clear_files)
        
        info_layout.addWidget(self._file_path_label, 1)
        info_layout.addWidget(clear_btn)
        
        layout.addWidget(default_group)
        layout.addWidget(image_group)
        layout.addLayout(info_layout)
        
        group.setLayout(layout)
        return group
    
    def _on_file_selected(self, file_path: str):
        """单文件选择回调"""
        import os
        self._file_path_label.setText(f"文件路径: {file_path}")
        toast = Toast(
            f"已选择文件: {os.path.basename(file_path)}",
            ToastType.SUCCESS,
            duration=2000
        )
        toast.show(ToastPosition.TOP_CENTER, self)
    
    def _on_files_selected(self, file_paths: list):
        """多文件选择回调"""
        import os
        count = len(file_paths)
        if count == 1:
            self._file_path_label.setText(f"文件路径: {file_paths[0]}")
        else:
            names = [os.path.basename(p) for p in file_paths[:3]]
            display = ", ".join(names)
            if count > 3:
                display += f" 等{count}个文件"
            self._file_path_label.setText(f"已选择 {count} 个文件: {display}")
        
        toast = Toast(
            f"已选择 {count} 个文件",
            ToastType.SUCCESS,
            duration=2000
        )
        toast.show(ToastPosition.TOP_CENTER, self)
    
    def _on_file_cleared(self):
        """文件清除回调"""
        self._file_path_label.setText("文件路径: 未选择")
    
    def _on_file_error(self, error_msg: str):
        """文件错误回调"""
        toast = Toast(error_msg, ToastType.ERROR, duration=3000)
        toast.show(ToastPosition.TOP_CENTER, self)
    
    def _clear_files(self):
        """清除所有文件"""
        self._default_file_widget.clearFile()
        self._image_file_widget.clearFile()
        toast = Toast("文件已清除", ToastType.INFO, duration=1500)
        toast.show(ToastPosition.TOP_CENTER, self)
    
    def _create_breadcrumb_page(self):
        """创建面包屑演示页面"""
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        page = ThemedWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_breadcrumb_section())
        layout.addStretch()
        
        scroll.setWidget(page)
        return scroll
    
    def _create_breadcrumb_section(self):
        """创建面包屑演示区域"""
        group = ThemedGroupBox("BreadcrumbBar 面包屑导航组件")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        demo_group = ThemedGroupBox("基础演示")
        demo_layout = QVBoxLayout(demo_group)
        demo_layout.setContentsMargins(5, 5, 5, 5)
        
        self._breadcrumb = BreadcrumbBar()
        self._breadcrumb.set_path(["首页", "产品中心", "电子产品", "智能手机", "iPhone 15"])
        self._breadcrumb.current_changed.connect(self._on_breadcrumb_changed)
        demo_layout.addWidget(self._breadcrumb)
        
        self._breadcrumb_result = ThemedLabel("点击面包屑项进行导航")
        demo_layout.addWidget(self._breadcrumb_result)
        
        layout.addWidget(demo_group)
        
        style_group = ThemedGroupBox("分隔符样式")
        style_layout = QVBoxLayout(style_group)
        style_layout.setContentsMargins(5, 5, 5, 5)
        
        self._breadcrumb_chevron = BreadcrumbBar()
        self._breadcrumb_chevron.set_path(["文档", "开发指南", "API参考"])
        style_layout.addWidget(self._breadcrumb_chevron)
        
        self._breadcrumb_arrow = BreadcrumbBar()
        self._breadcrumb_arrow.set_path(["文档", "开发指南", "API参考"])
        self._breadcrumb_arrow.set_separator_style(BreadcrumbSeparator.STYLE_ARROW)
        style_layout.addWidget(self._breadcrumb_arrow)
        
        self._breadcrumb_slash = BreadcrumbBar()
        self._breadcrumb_slash.set_path(["文档", "开发指南", "API参考"])
        self._breadcrumb_slash.set_separator_style(BreadcrumbSeparator.STYLE_SLASH)
        style_layout.addWidget(self._breadcrumb_slash)
        
        layout.addWidget(style_group)
        
        control_group = ThemedGroupBox("控制选项")
        control_layout = QVBoxLayout(control_group)
        control_layout.setContentsMargins(5, 5, 5, 5)
        
        path_layout = QHBoxLayout()
        ThemedLabel("设置路径:").setFixedWidth(70)
        path_layout.addWidget(ThemedLabel("设置路径:"))
        
        self._path_edit = ModernLineEdit()
        self._path_edit.setPlaceholderText("输入路径，用逗号分隔，如：首页,产品,详情")
        self._path_edit.setText("首页,产品中心,电子产品,智能手机,iPhone 15")
        path_layout.addWidget(self._path_edit)
        
        set_path_btn = CustomPushButton("设置")
        set_path_btn.clicked.connect(self._set_breadcrumb_path)
        path_layout.addWidget(set_path_btn)
        
        control_layout.addLayout(path_layout)
        
        options_layout = QHBoxLayout()
        
        show_current_cb = CustomCheckBox("显示当前项")
        show_current_cb.setChecked(True)
        show_current_cb.stateChanged.connect(lambda s: self._breadcrumb.set_show_current(s == Qt.CheckState.Checked.value))
        options_layout.addWidget(show_current_cb)
        
        ThemedLabel("最大可见项:").setFixedWidth(80)
        options_layout.addWidget(ThemedLabel("最大可见项:"))
        
        max_items_spin = SpinBox()
        max_items_spin.setRange(0, 20)
        max_items_spin.setValue(0)
        max_items_spin.valueChanged.connect(self._breadcrumb.set_max_visible_items)
        options_layout.addWidget(max_items_spin)
        
        options_layout.addStretch()
        
        control_layout.addLayout(options_layout)
        
        layout.addWidget(control_group)
        
        group.setLayout(layout)
        return group
    
    def _on_breadcrumb_changed(self, index: int, text: str):
        """面包屑导航改变回调"""
        current_path = self._breadcrumb.get_path()
        self._breadcrumb_result.setText(f"当前路径: {' > '.join(current_path)}")
        toast = Toast(f"导航到: {text}", ToastType.INFO, duration=1500)
        toast.show(ToastPosition.TOP_CENTER, self)
    
    def _set_breadcrumb_path(self):
        """设置面包屑路径"""
        path_text = self._path_edit.text().strip()
        if path_text:
            path = [p.strip() for p in path_text.split(",") if p.strip()]
            self._breadcrumb.set_path(path)
            toast = Toast(f"路径已更新: {' > '.join(path)}", ToastType.SUCCESS, duration=1500)
            toast.show(ToastPosition.TOP_CENTER, self)


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
