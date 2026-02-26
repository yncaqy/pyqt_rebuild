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
from PyQt6.QtGui import QIntValidator, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QAbstractItemView

from containers.frameless_window import FramelessWindow
from components.buttons.custom_push_button import CustomPushButton
from components.buttons.tool_button import ToolButton
from components.inputs.modern_line_edit import ModernLineEdit
from components.buttons.primary_push_button import PrimaryPushButton
from components.buttons.hyperlink_button import HyperlinkButton
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
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        content = self._create_content_widget()
        scroll.setWidget(content)
        
        self.setCentralWidget(scroll)
        
    def _create_content_widget(self):
        """创建内容区域"""
        content = ThemedWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_title_section())
        layout.addWidget(self._create_theme_section())
        layout.addWidget(self._create_buttons_section())
        layout.addWidget(self._create_inputs_section())
        layout.addWidget(self._create_checkbox_section())
        layout.addWidget(self._create_progress_section())
        layout.addWidget(self._create_slider_section())
        layout.addWidget(self._create_toast_section())
        layout.addWidget(self._create_messagebox_section())
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
        layout.addStretch()
        
        return content
        
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
        
        image_label1 = ImageLabel()
        image_label1.setFixedSize(150, 150)
        image_label1.setBorderRadius(8)
        image_label1.setImage("src/resources/images/拾光_壁纸汇_6538fb82e8b39b98.jpg")
        layout.addWidget(image_label1)
        
        image_label2 = ImageLabel()
        image_label2.setFixedSize(150, 150)
        image_label2.setBorderRadius(8)
        image_label2.setImage("src/resources/images/拾光_故宫博物院_25609b39e7117207.jpg")
        layout.addWidget(image_label2)
        
        image_label3 = ImageLabel()
        image_label3.setFixedSize(150, 150)
        image_label3.setBorderRadius(8)
        image_label3.setImage("src/resources/images/拾光_故宫博物院_908379888903489d.jpg")
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
