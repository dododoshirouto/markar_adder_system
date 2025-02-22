from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QSlider, QCheckBox, QRadioButton, QHBoxLayout, QSpinBox, QGroupBox, QComboBox, QListWidget
)
from PyQt6.QtCore import Qt

class AudioMarkerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None  # ファイルパスを保存する変数
        self.initUI()

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
        self.track_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.color_dropdown = QComboBox()
        self.color_dropdown.addItems(["Red", "Blue", "Green", "Yellow", "Magenta", "Cyan"])
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
        self.silence_slider.setMinimum(-80)
        self.silence_slider.setMaximum(0)
        self.silence_slider.setValue(-40)
        self.silence_spinbox = QSpinBox()
        self.silence_spinbox.setRange(-80, 0)
        self.silence_spinbox.setValue(-40)
        detect_layout.addWidget(self.silence_slider)
        detect_layout.addWidget(self.silence_spinbox)
        
        detect_layout.addWidget(QLabel("無音の最低時間 (ms)"))
        self.silence_duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.silence_duration_slider.setMinimum(100)
        self.silence_duration_slider.setMaximum(10000)
        self.silence_duration_slider.setValue(500)
        self.silence_duration_spinbox = QSpinBox()
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
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "動画ファイルを選択", "", "Video Files (*.mp4 *.mov *.avi)")
        if file_path:
            self.file_label.setText(file_path)
            self.file_path = file_path

if __name__ == "__main__":
    app = QApplication([])
    window = AudioMarkerApp()
    window.show()
    app.exec()
