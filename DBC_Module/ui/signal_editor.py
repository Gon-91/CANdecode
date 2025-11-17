from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox

class SignalEditor(QWidget):
    def __init__(self, layout_view=None, autosave_callback=None):
        super().__init__()
        self.layout_view = layout_view
        self.autosave_callback = autosave_callback
        self.current_signal = None

        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.start_edit = QSpinBox(); self.start_edit.setRange(0, 511)
        self.length_edit = QSpinBox(); self.length_edit.setRange(1, 64)
        self.type_edit = QComboBox()
        self.type_edit.addItems(["Unsigned", "Signed", "Float"])
        self.byteorder_edit = QComboBox()
        self.byteorder_edit.addItems(["Motorola", "Intel"])
        self.value_edit = QComboBox()
        self.value_edit.addItems(["+", "-"])
        self.factor_edit = QDoubleSpinBox(); self.factor_edit.setDecimals(6); self.factor_edit.setRange(-1e6, 1e6)
        self.offset_edit = QDoubleSpinBox(); self.offset_edit.setDecimals(6); self.offset_edit.setRange(-1e6, 1e6)
        self.min_edit = QDoubleSpinBox(); self.min_edit.setDecimals(6); self.min_edit.setRange(-1e6, 1e6)
        self.max_edit = QDoubleSpinBox(); self.max_edit.setDecimals(6); self.max_edit.setRange(-1e6, 1e6)
        self.unit_edit = QLineEdit()

        form.addRow("Name", self.name_edit)
        form.addRow("StartBit", self.start_edit)
        form.addRow("Length", self.length_edit)
        form.addRow("Type", self.type_edit)
        form.addRow("ByteOrder", self.byteorder_edit)
        form.addRow("Signed/Unsigned", self.value_edit)
        form.addRow("Factor", self.factor_edit)
        form.addRow("Offset", self.offset_edit)
        form.addRow("Min", self.min_edit)
        form.addRow("Max", self.max_edit)
        form.addRow("Unit", self.unit_edit)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addStretch()
        self.setLayout(layout)

        self.name_edit.textChanged.connect(self.apply)
        self.start_edit.valueChanged.connect(self.apply)
        self.length_edit.valueChanged.connect(self.apply)
        self.type_edit.currentTextChanged.connect(self.apply)
        self.byteorder_edit.currentTextChanged.connect(self.apply)
        self.value_edit.currentTextChanged.connect(self.apply)
        self.factor_edit.valueChanged.connect(self.apply)
        self.offset_edit.valueChanged.connect(self.apply)
        self.min_edit.valueChanged.connect(self.apply)
        self.max_edit.valueChanged.connect(self.apply)
        self.unit_edit.textChanged.connect(self.apply)

    def load_signal(self, sig):
        self.current_signal = sig
        if not sig:
            return
        self.name_edit.setText(sig.name)
        self.start_edit.setValue(sig.start_bit)
        self.length_edit.setValue(sig.length)
        self.type_edit.setCurrentText(sig.sig_type)
        self.byteorder_edit.setCurrentIndex(1 if sig.byte_order==1 else 0)
        self.value_edit.setCurrentText(sig.value_type)
        self.factor_edit.setValue(sig.factor)
        self.offset_edit.setValue(sig.offset)
        self.min_edit.setValue(sig.minimum)
        self.max_edit.setValue(sig.maximum)
        self.unit_edit.setText(sig.unit)

    def apply(self):
        if not self.current_signal:
            return
        sig = self.current_signal
        sig.name = self.name_edit.text()
        sig.start_bit = self.start_edit.value()
        sig.length = self.length_edit.value()
        sig.sig_type = self.type_edit.currentText()
        sig.byte_order = 1 if self.byteorder_edit.currentText()=="Intel" else 0
        sig.value_type = self.value_edit.currentText()
        sig.factor = self.factor_edit.value()
        sig.offset = self.offset_edit.value()
        sig.minimum = self.min_edit.value()
        sig.maximum = self.max_edit.value()
        sig.unit = self.unit_edit.text()
        if self.layout_view:
            self.layout_view.update()
        if self.autosave_callback:
            self.autosave_callback()
