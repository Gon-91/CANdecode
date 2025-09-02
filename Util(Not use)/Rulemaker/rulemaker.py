import sys
import json
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QLineEdit, QFileDialog, QMessageBox,
    QComboBox, QCheckBox
)


class RuleBuilder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN Log Rule Builder (PyQt5)")
        self.setGeometry(200, 200, 900, 700)

        self.sample_lines = []  # 파일 미리보기용 저장

        layout = QVBoxLayout()

        # 파일 미리보기
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(QLabel("File Preview"))
        layout.addWidget(self.preview)

        open_btn = QPushButton("Open Log File")
        open_btn.clicked.connect(self.open_file)
        layout.addWidget(open_btn)

        # 컬럼 매핑
        self.col_edits = {}
        for field in ["timestamp", "channel", "can_id", "dlc", "data", "type"]:
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(f"{field} 예시 값 →"))
            edit = QLineEdit()
            self.col_edits[field] = edit
            hbox.addWidget(edit)
            layout.addLayout(hbox)

        # 옵션
        self.timestamp_combo = QComboBox()
        self.timestamp_combo.addItems(["int", "float"])
        self.canid_combo = QComboBox()
        self.canid_combo.addItems(["hex", "dec"])
        self.data_combo = QComboBox()
        self.data_combo.addItems(["hex", "ascii"])
        self.fd_checkbox = QCheckBox("CAN FD")

        layout.addWidget(QLabel("Timestamp Format"))
        layout.addWidget(self.timestamp_combo)
        layout.addWidget(QLabel("CAN ID Base"))
        layout.addWidget(self.canid_combo)
        layout.addWidget(QLabel("Data Encoding"))
        layout.addWidget(self.data_combo)
        layout.addWidget(self.fd_checkbox)

        # 버튼
        gen_btn = QPushButton("Generate Rule & Preview")
        gen_btn.clicked.connect(self.generate_rule)
        layout.addWidget(gen_btn)

        self.result_preview = QTextEdit()
        self.result_preview.setReadOnly(True)
        layout.addWidget(QLabel("Parsed Preview"))
        layout.addWidget(self.result_preview)

        save_btn = QPushButton("Save Rule")
        save_btn.clicked.connect(self.save_rule)
        layout.addWidget(save_btn)

        self.setLayout(layout)

        self.generated_rule = {}

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Log File", "", "Text Files (*.txt *.log *.csv);;All Files (*)")
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                self.sample_lines = []
                for i, line in enumerate(f):
                    if i >= 10:
                        break
                    self.sample_lines.append(line.strip())
            self.preview.setText("\n".join(self.sample_lines))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def generate_rule(self):
        if not self.sample_lines:
            QMessageBox.warning(self, "Warning", "파일을 먼저 열어주세요.")
            return

        # 사용자가 입력한 값들
        mapping_values = {k: v.text().strip()
                          for k, v in self.col_edits.items() if v.text().strip()}

        # 간단한 regex 자동 생성 (예시 값 중심)
        sample_line = self.sample_lines[0]
        pattern = re.escape(sample_line)
        for field, value in mapping_values.items():
            if value in sample_line:
                pattern = pattern.replace(re.escape(value), f"(?P<{field}>.+?)")

        regex = re.compile(pattern)

        parsed_preview = []
        for line in self.sample_lines:
            match = regex.match(line)
            if match:
                parsed_preview.append(str(match.groupdict()))
            else:
                parsed_preview.append("Parse fail: " + line)

        self.result_preview.setText("\n".join(parsed_preview))

        # JSON 룰 저장용
        self.generated_rule = {
            "pattern": pattern,
            "columns": list(mapping_values.keys()),
            "timestamp_format": self.timestamp_combo.currentText(),
            "can_id_base": self.canid_combo.currentText(),
            "data_encoding": self.data_combo.currentText(),
            "is_fd": self.fd_checkbox.isChecked()
        }

    def save_rule(self):
        if not self.generated_rule:
            QMessageBox.warning(self, "Warning", "룰을 먼저 생성하세요.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Rule", "", "JSON Files (*.json)")
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(self.generated_rule, f, indent=2)
                QMessageBox.information(self, "Success",
                                        f"Rule saved to {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                     f"Failed to save rule:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RuleBuilder()
    win.show()
    sys.exit(app.exec_())
