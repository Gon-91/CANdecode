from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QFileDialog,QMessageBox,
    QListWidgetItem, QLabel, QLineEdit, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
import pandas as pd


class DBCManagerDialog(QDialog):
    def __init__(self, dbc_manager, df: pd.DataFrame, parent=None):
        """
        dbc_manager: DBCManager 인스턴스
        df: 현재 테이블/그래프와 연동된 DataFrame
        """
        super().__init__(parent)
        self.setWindowTitle("DBC Manager")
        self.resize(900, 600)

        self.dbc_manager = dbc_manager
        self.df = df.copy()
        self.selected_signal = None

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)

        # 버튼 영역
        self.btn_load = QPushButton("Load DBC")
        self.btn_load.clicked.connect(self.load_dbc)
        main_layout.addWidget(self.btn_load)

        # 중앙 영역 (좌: 신호 리스트 / 우: 에디터+테이블)
        center_layout = QHBoxLayout()
        main_layout.addLayout(center_layout)

        # 좌측: 신호 리스트
        self.signal_list = QListWidget()
        self.signal_list.itemClicked.connect(self.on_signal_selected)
        center_layout.addWidget(self.signal_list, 2)

        # 우측 레이아웃
        right_layout = QVBoxLayout()
        center_layout.addLayout(right_layout, 5)

        # 우측 상단: 신호 정보 및 factor/offset 입력
        self.lbl_info = QLabel("No signal selected")
        right_layout.addWidget(self.lbl_info)

        fo_layout = QHBoxLayout()
        self.factor_input = QLineEdit("1.0")
        self.offset_input = QLineEdit("0.0")
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self.apply_factor_offset)

        fo_layout.addWidget(QLabel("Factor"))
        fo_layout.addWidget(self.factor_input)
        fo_layout.addWidget(QLabel("Offset"))
        fo_layout.addWidget(self.offset_input)
        fo_layout.addWidget(self.btn_apply)
        right_layout.addLayout(fo_layout)

        # 우측 하단: 디코딩 값 테이블
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Decoded Value"])
        right_layout.addWidget(self.table, stretch=1)

    def load_dbc(self):
        """DBC 파일 불러오기"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox

        filepath, _ = QFileDialog.getOpenFileName(self, "DBC 파일 선택", "", "DBC Files (*.dbc)")
        if not filepath:
            return

        try:
            self.dbc_manager.load_dbc(filepath)
            self.signal_list.clear()

            # 메시지와 신호 목록 가져오기
            for msg in self.dbc_manager.db.messages:
                for sig in msg.signals:
                    sig_dict = {
                        "message_id": msg.frame_id,
                        "name": sig.name,
                        "factor": sig.scale,
                        "offset": sig.offset
                    }
                    item = QListWidgetItem(f"{msg.name} - {sig.name}")
                    item.setData(Qt.UserRole, sig_dict)
                    self.signal_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"DBC 불러오기 실패:\n{e}")


    def on_signal_selected(self, item: QListWidgetItem):
        """신호 선택 시 정보 표시"""
        sig = item.data(Qt.UserRole)
        self.selected_signal = sig
        self.lbl_info.setText(
            f"Message ID: {sig.get('message_id')} | Signal: {sig.get('name')}"
        )
        self.factor_input.setText(str(sig.get("factor", 1.0)))
        self.offset_input.setText(str(sig.get("offset", 0.0)))
        self.update_preview()

    def apply_factor_offset(self):
        """Factor/Offset 적용"""
        if not self.selected_signal:
            return
        try:
            factor = float(self.factor_input.text())
            offset = float(self.offset_input.text())
        except ValueError:
            return

        # 신호 dict 갱신
        self.selected_signal["factor"] = factor
        self.selected_signal["offset"] = offset

        self.update_preview()

    def update_preview(self):
        """선택된 신호 디코딩 값 미리보기"""
        if not self.selected_signal:
            return

        factor = self.selected_signal.get("factor", 1.0)
        offset = self.selected_signal.get("offset", 0.0)

        # DataFrame을 DBC 디코딩용으로 변환
        df_for_decoding = self.df.copy()

        # DBCManager decode_dataframe 호출 전 data 열 생성
        if "data" not in df_for_decoding.columns:
            def row_to_bytes(row):
                dlc = int(row.get("dlc", 8))
                return bytes([int(row.get(str(i), "0"), 16) for i in range(dlc)])  # HEX 문자열 → 정수
            df_for_decoding["data"] = df_for_decoding.apply(row_to_bytes, axis=1)

        try:
            decoded_df = self.dbc_manager.decode_dataframe(df_for_decoding)
        except Exception as e:
            QMessageBox.critical(self, "Decode Error", f"디코딩 실패:\n{e}")
            return

        # 선택된 신호에 대한 디코딩 값 추출
        sig_name = self.selected_signal.get("name")
        if sig_name not in decoded_df.columns:
            return

        decoded_series = decoded_df[sig_name] * factor + offset

        # 테이블 갱신
        self.table.setRowCount(len(decoded_series))
        for i, (ts, val) in enumerate(zip(df_for_decoding["timestamp"], decoded_series)):
            self.table.setItem(i, 0, QTableWidgetItem(str(ts)))
            self.table.setItem(i, 1, QTableWidgetItem(f"{val:.2f}"))