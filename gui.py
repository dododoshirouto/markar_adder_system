from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QSlider, QCheckBox, QRadioButton, QHBoxLayout, QSpinBox, QGroupBox, QComboBox, QListWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QColor
import ffmpeg

class AudioMarkerApp(QWidget):
  
    # color_options = ["not use", "Red", "Blue", "Green", "Yellow", "Magenta", "Cyan"]
    color_options = [
        {
            "name": "Red",
            "color": Qt.GlobalColor.red
        },
        {
            "name": "Blue",
            "color": Qt.GlobalColor.blue
        },
        {
            "name": "Green",
            "color": Qt.GlobalColor.green
        },
        {
            "name": "Yellow",
            "color": Qt.GlobalColor.yellow
        },
        {
            "name": "Magenta",
            "color": Qt.GlobalColor.magenta
        },
        {
            "name": "Cyan",
            "color": Qt.GlobalColor.cyan
        }
    ]
        
    silence_spinbox:QSpinBox = None
    silence_slider:QSlider = None
    silence_duration_spinbox:QSpinBox = None
    silence_duration_slider:QSlider = None

    def __init__(self):
        super().__init__()
        self.file_path = None  # ファイルパスを保存する変数
        self.initUI()
        self.setAcceptDrops(True)  # D&Dを有効化

    def initUI(self):
        layout = QVBoxLayout()
        
        # ファイル選択セクション（D&D対応予定）
        file_group = QGroupBox("ファイル選択")
        file_layout = QVBoxLayout()
        self.file_label_head = QLabel("選択されたファイル:")
        self.file_label = QLabel("なし")
        self.file_label.setMaximumHeight(20)
        self.file_label.setWordWrap(False)
        self.file_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.file_button = QPushButton("ファイルを選択")
        self.file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label_head)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_button)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # トラック選択と色設定
        track_group = QGroupBox("トラック選択 & マーカー色設定")
        track_layout = QVBoxLayout()
        self.track_list = QListWidget()
        self.track_list.itemSelectionChanged.connect(self.update_color_selection)
        self.track_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.color_dropdown = QComboBox()
        self.color_dropdown.currentIndexChanged.connect(self.apply_selected_color)
        self.color_dropdown.addItems(['- None -'] + [color['name'] for color in self.color_options])
        track_layout.addWidget(QLabel("使用するトラックを選択"))
        track_layout.addWidget(self.track_list)
        track_layout.addWidget(QLabel("マーカーの色を選択"))
        track_layout.addWidget(self.color_dropdown)
        track_group.setLayout(track_layout)
        layout.addWidget(track_group)
        
        # 無音検出設定セクション
        detect_group = QGroupBox("無音検出の設定")
        detect_layout = QVBoxLayout()
        detect_layout.addWidget(QLabel("無視する音量レベル (dB)"))
        self.silence_slider = QSlider(Qt.Orientation.Horizontal)
        self.silence_slider.valueChanged.connect(self.sync_silence_spinbox)
        self.silence_slider.setMinimum(-80)
        self.silence_slider.setMaximum(0)
        self.silence_slider.setValue(-40)
        self.silence_spinbox = QSpinBox()
        self.silence_spinbox.valueChanged.connect(self.sync_silence_slider)
        self.silence_spinbox.setRange(-80, 0)
        self.silence_spinbox.setValue(-40)
        detect_layout.addWidget(self.silence_slider)
        detect_layout.addWidget(self.silence_spinbox)
        
        detect_layout.addWidget(QLabel("無音の最低時間 (ms)"))
        self.silence_duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.silence_duration_slider.valueChanged.connect(self.sync_silence_duration_spinbox)
        self.silence_duration_slider.setMinimum(100)
        self.silence_duration_slider.setMaximum(10000)
        self.silence_duration_slider.setValue(500)
        self.silence_duration_spinbox = QSpinBox()
        self.silence_duration_spinbox.valueChanged.connect(self.sync_silence_duration_slider)
        self.silence_duration_spinbox.setRange(100, 10000)
        self.silence_duration_spinbox.setValue(500)
        detect_layout.addWidget(self.silence_duration_slider)
        detect_layout.addWidget(self.silence_duration_spinbox)
        detect_group.setLayout(detect_layout)
        layout.addWidget(detect_group)
        
        # マーカー設定セクション
        marker_group = QGroupBox("マーカー設定")
        marker_layout = QVBoxLayout()
        self.start_marker_checkbox = QCheckBox("音の出始めにマーカーを付ける")
        self.end_marker_checkbox = QCheckBox("音の終わりにマーカーを付ける")
        marker_layout.addWidget(self.start_marker_checkbox)
        marker_layout.addWidget(self.end_marker_checkbox)
        marker_group.setLayout(marker_layout)
        layout.addWidget(marker_group)
        
        # マーカー数表示（トラックごとの個数 & 合計）
        self.marker_count_label = QLabel("マーカー数: -")
        self.track_marker_count_label = QLabel("トラックごとのマーカー数: -")
        layout.addWidget(self.marker_count_label)
        layout.addWidget(self.track_marker_count_label)
        
        # 実行ボタン
        self.create_marker_button = QPushButton("マーカー作成")
        layout.addWidget(self.create_marker_button)
        
        self.setLayout(layout)
        self.setWindowTitle("Audio Marker Tool")
        self.resize(400, 400)

    def sync_silence_spinbox(self, value):
        if self.silence_spinbox is None: return
        self.silence_spinbox.setValue(value)

    def sync_silence_slider(self, value):
        if self.silence_slider is None: return
        self.silence_slider.setValue(value)

    def sync_silence_duration_spinbox(self, value):
        if self.silence_duration_spinbox is None: return
        self.silence_duration_spinbox.setValue(value)

    def sync_silence_duration_slider(self, value):
        if self.silence_duration_slider is None: return
        self.silence_duration_slider.setValue(value)
        self.setWindowTitle("Audio Marker Tool")
        self.resize(400, 400)
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "動画ファイルを選択", "", "Video Files (*.mp4 *.mov *.avi)")
        if file_path:
            self.file_label.setText(file_path)
            self.file_path = file_path
            self.update_track_list()
    
    def update_track_list(self):
        """ 選択した動画ファイルから音声トラック情報を取得し、リストを更新し、デフォルトの色を割り当て """
        self.track_list.clear()
        self.track_colors = {}
        
        if not self.file_path:
            return
        
        probe = ffmpeg.probe(self.file_path)
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
        
        for i, stream in enumerate(audio_streams):
            track_name = f"Track {i+1} ({stream['codec_name']})"
            self.track_list.addItem(track_name)
            self.track_colors[track_name] = self.color_options[i % len(self.color_options)]['name']  # 色を順番に割り当て
        
        self.update_color_selection()
        self.adjust_track_list_height()
        """ 選択した動画ファイルから音声トラック情報を取得し、リストを更新 """
        self.track_list.clear()
        if not self.file_path:
            return
        
        probe = ffmpeg.probe(self.file_path)
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
        
        for i, stream in enumerate(audio_streams):
            self.track_list.addItem(f"Track {i+1} ({stream['codec_name']})")
        self.track_list.addItem("")

        self.update_color_selection()
        
    def adjust_track_list_height(self):
        """ トラック数に応じてリストの高さを調整 """
        row_height = 26  # 各トラックの高さ（ピクセル）
        max_visible_tracks = 10  # 一度に表示する最大のトラック数
        track_count = self.track_list.count()
        new_height = min(track_count, max_visible_tracks) * row_height
        self.track_list.setFixedHeight(new_height)

    def update_color_selection(self):
        """ 選択されたトラックに対して、現在選択中の色を適用し、背景色を変更 """
        for index in range(self.track_list.count()):
            item = self.track_list.item(index)
            track_name = item.text()
            color_name = self.track_colors.get(track_name, "- None -")
            color = QColor(next((c['color'] for c in self.color_options if c['name'] == color_name), Qt.GlobalColor.black))
            item.setBackground(color)  # 背景色を設定
            alpha_color = color
            alpha_color.setAlphaF(0.5)
            item.setBackground(alpha_color)
            selected_color = color
            selected_color.setAlphaF(0.7)
            if item.isSelected():
                item.setBackground(selected_color)
        
        selected_items = self.track_list.selectedItems()
        if selected_items:
            track_name = selected_items[0].text()
            current_color = self.track_colors.get(track_name, "- None -")
            index = self.color_dropdown.findText(current_color)
            if index != -1:
                self.color_dropdown.setCurrentIndex(index)
        """ 選択されたトラックに対して、現在選択中の色を適用 """
        selected_items = self.track_list.selectedItems()
        if selected_items:
            track_name = selected_items[0].text()
            current_color = self.track_colors.get(track_name, "- None -")
            index = self.color_dropdown.findText(current_color)
            if index != -1:
                self.color_dropdown.setCurrentIndex(index)

    def apply_selected_color(self):
        """ 選択されたトラックに新しい色を適用 """
        selected_items = self.track_list.selectedItems()
        if selected_items:
            track_name = selected_items[0].text()
            selected_color_name = self.color_dropdown.currentText()
            self.track_colors[track_name] = selected_color_name

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_label.setText(file_path)
            self.file_path = file_path
            self.update_track_list()

if __name__ == "__main__":
    app = QApplication([])
    window = AudioMarkerApp()
    window.show()
    app.exec()
