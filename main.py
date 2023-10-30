import json
from pathlib import Path

import pydicom
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QTableWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QRadioButton,
    QLabel,
    QButtonGroup,
    QMenuBar,
    QMenu,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout,
    QLineEdit,
    QProgressBar,
    QMessageBox,
    QInputDialog,
)

from utilities.config_manager import load_config, save_config, auto_select
from utilities.encryption_manager import encrypt, decrypt, detect_if_encrypted
from utilities.helper_function import load_dcm_files, get_tags


class DICOMAnonymizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("DICOM Anonymizer")
        self.setGeometry(100, 100, 1200, 600)
        self.setup_menu()
        self.setup_layout()

    def setup_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        file_menu = QMenu("File", self)
        menubar.addMenu(file_menu)

        save_action = QAction(QIcon(), "Save Config", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)

        load_action = QAction(QIcon(), "Load Config", self)
        load_action.triggered.connect(self.load_config)
        file_menu.addAction(load_action)

    def setup_layout(self):
        """Setup the main layout and add widgets."""
        main_layout = QVBoxLayout()

        # Folder Selector
        self.folderBtn = QPushButton("Select Folder", self)
        self.folderBtn.clicked.connect(self.select_folder)
        main_layout.addWidget(self.folderBtn)

        # Search Fields
        self.setup_search_fields(main_layout)

        # Tags Table
        self.setup_table(main_layout)

        # Radio buttons for Anonymize or Encrypt and Password input
        self.setup_radio_buttons(main_layout)

        # Auto Select and Process Button
        self.autoSelectBtn = QPushButton("Auto Select", self)
        self.autoSelectBtn.clicked.connect(self.auto_select)
        main_layout.addWidget(self.autoSelectBtn)

        self.processBtn = QPushButton("Process", self)
        self.processBtn.clicked.connect(self.process_files)
        main_layout.addWidget(self.processBtn)

        # Progress bar
        self.progressBar = QProgressBar(self)
        main_layout.addWidget(self.progressBar)
        self.progressBar.setValue(0)
        self.progressBar.hide()

        centralWidget = QWidget(self)
        centralWidget.setLayout(main_layout)
        self.setCentralWidget(centralWidget)

    def setup_table(self, main_layout):
        self.tagsTable = QTableWidget(0, 8)
        self.tagsTable.setHorizontalHeaderLabels(
            [
                "Tag (Flag)",
                "Tag Name",
                "value",
                "Unchanged",
                "Change",
                "Dummy value",
                "Delete",
                "Encrypt",
            ]
        )
        self.tagsTable.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        main_layout.addWidget(self.tagsTable)

    def setup_search_fields(self, main_layout):
        """Setup search fields for Tag (Flag), Tag Name, and Value."""
        search_layout = QHBoxLayout()

        # Search fields for Tag (Flag), Tag Name, and Value
        self.searchTag = QLineEdit(self)
        self.searchTag.setPlaceholderText("Search Tag (Flag)")
        self.searchTagName = QLineEdit(self)
        self.searchTagName.setPlaceholderText("Search Tag Name")
        self.searchValue = QLineEdit(self)
        self.searchValue.setPlaceholderText("Search Value")

        # Connect textChanged signal to filterTable method
        self.searchTag.textChanged.connect(self.filter_table)
        self.searchTagName.textChanged.connect(self.filter_table)
        self.searchValue.textChanged.connect(self.filter_table)

        search_layout.addWidget(self.searchTag)
        search_layout.addWidget(self.searchTagName)
        search_layout.addWidget(self.searchValue)

        main_layout.addLayout(search_layout)

    def filter_table(self):
        """Filter table rows based on search criteria."""
        # Get search criteria
        search_tag = self.searchTag.text().lower()
        search_tag_name = self.searchTagName.text().lower()
        search_value = self.searchValue.text().lower()

        for row in range(self.tagsTable.rowCount()):
            tag_flag = self.tagsTable.item(row, 0).text().lower()
            tag_name = self.tagsTable.item(row, 1).text().lower()
            value = self.tagsTable.cellWidget(row, 2).text().lower()

            # Show or hide the row based on search criteria
            match = True
            if search_tag and search_tag not in tag_flag:
                match = False
            if search_tag_name and search_tag_name not in tag_name:
                match = False
            if search_value and search_value not in value:
                match = False

            self.tagsTable.setRowHidden(row, not match)

    def setup_radio_buttons(self, main_layout):
        radio_layout = QHBoxLayout()

        self.passwordLabel = QLabel("Encryption Password:")
        self.passwordInput = QLineEdit(self)
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        radio_layout.addWidget(self.passwordLabel)
        radio_layout.addWidget(self.passwordInput)

        main_layout.addLayout(radio_layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder = folder
            self.get_dicom_tags()

    def get_dicom_tags(self):
        self.tagsTable.setRowCount(0)
        try:
            tags_set = get_tags(self.folder)
        except ValueError:
            # Show a dialog to input password for decryption
            password, ok = QInputDialog.getText(
                self, "Encrypted Data Detected", "Enter password for decryption:"
            )
            if ok:
                self.decrypt_files(password)
            return
        for tag_flag, tag_name, value in sorted(tags_set, key=lambda x: x[1]):
            row_position = self.tagsTable.rowCount()
            self.tagsTable.insertRow(row_position)
            self.tagsTable.setItem(row_position, 0, QTableWidgetItem(tag_flag))
            self.tagsTable.setItem(row_position, 1, QTableWidgetItem(tag_name))

            value_input = QLineEdit(value)
            self.tagsTable.setCellWidget(row_position, 2, value_input)

            self.add_actions_to_row(row_position)

    def add_actions_to_row(self, row):
        radio_group = QButtonGroup(self)
        unchanged_radio = QRadioButton("")
        change_dummy_radio = QRadioButton("")
        change_value_radio = QRadioButton("")
        delete_radio = QRadioButton("")
        encryptRadio = QRadioButton("")

        radio_group.addButton(unchanged_radio)
        radio_group.addButton(change_dummy_radio)
        radio_group.addButton(change_value_radio)
        radio_group.addButton(delete_radio)
        radio_group.addButton(encryptRadio)

        self.tagsTable.setCellWidget(row, 3, unchanged_radio)
        self.tagsTable.setCellWidget(row, 4, change_dummy_radio)
        self.tagsTable.setCellWidget(row, 5, change_value_radio)
        self.tagsTable.setCellWidget(row, 6, delete_radio)
        self.tagsTable.setCellWidget(row, 7, encryptRadio)
        unchanged_radio.setChecked(True)

    def save_config(self):
        save_config(self.tagsTable, "config.ini")

    def load_config(self):
        load_config(self.tagsTable, "config.ini")

    def auto_select(self):
        auto_select(self.tagsTable)

    def process_files(self):
        if self.is_encrypt_selected() and not self.passwordInput.text():
            QMessageBox.critical(
                self, "Error", "Please provide an encryption password!"
            )
            return

        dummy_ds = pydicom.dcmread(pydicom.data.get_testdata_file("CT_small.dcm"))
        total_files = len(list(load_dcm_files(self.folder)))
        self.progressBar.setMaximum(total_files)
        self.progressBar.show()

        for idx, dcm_file in enumerate(load_dcm_files(self.folder)):
            self.process_single_file(dcm_file, dummy_ds)
            self.progressBar.setValue(idx + 1)

    def process_single_file(self, dcm_file, dummy_ds):
        output_filepath = dcm_file.replace(self.folder, self.folder + "_new")
        ds = pydicom.dcmread(dcm_file)
        encryption_flags = {}
        for row in range(self.tagsTable.rowCount()):
            tag_name = self.tagsTable.item(row, 1).text()
            if tag_name in ds:
                flag = self.process_tag(ds, tag_name, row, dummy_ds)
                if flag:
                    encryption_flags[str(flag["tag"])] = flag
        if len(encryption_flags.keys()) > 0:
            encrypted_data = encrypt(
                json.dumps(encryption_flags), self.passwordInput.text()
            )
            ds.add_new((0x0019, 0x0101), "OB", encrypted_data.encode())
        Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
        ds.save_as(output_filepath)

    def process_tag(self, ds, tag_name, row, dummy_ds):
        action = self.get_action_for_row(row)
        tag = pydicom.datadict.tag_for_keyword(tag_name)
        if action == "Change with Dummy Value":
            ds[tag].value = dummy_ds.get(tag_name, "")
        elif action == "Change with Value":
            new_value = self.tagsTable.cellWidget(row, 2).text()
            ds[tag].value = new_value
        elif action == "Delete":
            del ds[tag]
        elif action == "Encrypt":
            data = {
                "tag": ds[tag].tag,
                "value": ds[tag].value,
                "name": ds[tag].name,
                "VR": ds[tag].VR,
            }
            del ds[tag]
            return data

    def get_action_for_row(self, row):
        if self.tagsTable.cellWidget(row, 3).isChecked():
            return "Unchanged"
        elif self.tagsTable.cellWidget(row, 5).isChecked():
            return "Change with Dummy Value"
        elif self.tagsTable.cellWidget(row, 4).isChecked():
            return "Change with Value"
        elif self.tagsTable.cellWidget(row, 6).isChecked():
            return "Delete"
        elif self.tagsTable.cellWidget(row, 7).isChecked():
            return "Encrypt"

    def is_encrypt_selected(self):
        for row in range(self.tagsTable.rowCount()):
            if self.tagsTable.cellWidget(row, 7).isChecked():
                return True
        return False

    def findRowForTag(self, tag_name):
        """Find the row in the table corresponding to a given DICOM tag."""
        for row in range(self.tagsTable.rowCount()):
            if self.tagsTable.item(row, 1).text() == tag_name:
                return row
        return None

    def decrypt_files(self, password):
        for dcm_file in load_dcm_files(self.folder):
            output_filepath = dcm_file.replace(self.folder, self.folder + "_new")
            ds = pydicom.dcmread(dcm_file)
            if detect_if_encrypted(ds):
                data = ds[(0x0019, 0x0101)].value.decode()
                data_decripted = json.loads(decrypt(data, password))
                for key in data_decripted.keys():
                    tag = data_decripted[key]
                    ds.add_new(tag["tag"], tag["VR"], tag["value"])
            Path(output_filepath).parent.mkdir(exist_ok=True, parents=True)
            ds.save_as(output_filepath)


if __name__ == "__main__":
    app = QApplication([])
    window = DICOMAnonymizer()
    window.show()
    app.exec()
