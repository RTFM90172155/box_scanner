# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import threading
import glob
import time
import csv
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_result_file(data):
    str_time = time.strftime('%y%m%d%H%M%S', time.localtime())
    result_file = f'result_{str_time}.csv'
    if not os.path.exists(result_file):
        with open(result_file, 'w', newline='') as f:
            csv.writer(f).writerow(data)
    return result_file

def append_result_data(result_file, data):
    with open(result_file, 'a', newline='') as f:
        csv.writer(f).writerow(data)


class BoxScanner(QThread):

    pBar_setRange = pyqtSignal(int, int)
    pBar_setValue = pyqtSignal(int)
    completed = pyqtSignal(int, int, int, str)

    def __init__(self, scan_dir, sub_dir, only_img, parent=None):
        super().__init__(parent)
        self.scan_dir = scan_dir
        self.sub_dir = sub_dir
        self.only_img = only_img
        self.flag = False

    def run(self):
        self.pBar_setRange.emit(0, 0)

        if self.sub_dir:
            scan_path = os.path.join(self.scan_dir, '**')
        else:
            scan_path = self.scan_dir

        img_ext_list = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        if self.only_img:
            ext_list = [f'*{ext}' for ext in img_ext_list]
        else:
            ext_list = ['*']

        file_list = [self.scan_dir]
        for ext in ext_list:
            search_iter = glob.iglob(os.path.join(scan_path, ext), recursive=True)
            for file in search_iter:
                if self.flag:
                    print(f'box(suspect)/total: 0(0)/0 Completed')
                    self.completed.emit(0, 0, 0, '')
                    return
                file_list.append(file)

        num_file = len(file_list)
        result_file = create_result_file(['file_name', 'is_box'])

        self.pBar_setRange.emit(0, num_file)
        self.pBar_setValue.emit(0)
        img_sig_list = [b'\x60\x82', b'\xFF\xD9', b'\x00\x3B']
        zip_sig = b'\x50\x4B\x05\x06'
        certain_count = 0
        suspect_count = 0
        for i, file in enumerate(file_list):
            if self.flag:
                print(f'box(suspect)/total: {certain_count}({suspect_count})/{num_file} Completed')
                self.completed.emit(certain_count, suspect_count, num_file, result_file)
                return

            if os.path.isdir(file):
                is_box = 'dir'
            else:
                file_size = os.path.getsize(file)
                if file_size < 100:
                    is_box = 'not'
                else:
                    with open(file, 'rb') as f:
                        f.seek(4, 0)
                        is_webp = int.from_bytes(f.read(4), byteorder='little') + 8
                        f.seek(-22, 2)
                        is_zip = f.read(4)
                        f.seek(-2, 2)
                        is_img = f.read()
                    
                    if is_zip == zip_sig:
                        is_box = 'certain'
                        certain_count += 1
                    elif is_webp == file_size or is_img in img_sig_list:
                        is_box = 'not'
                    else:
                        file_ext = os.path.splitext(file)[1]
                        if self.only_img or file_ext in img_ext_list:
                            is_box = 'suspect'
                            suspect_count += 1
                        else:
                            is_box = 'unknown'

            append_result_data(result_file, [file, is_box])
            print(f'({i+1}/{num_file}) Scan')
            self.pBar_setValue.emit(i+1)

        print(f'box(suspect)/total: {certain_count}({suspect_count})/{num_file} Completed')
        self.completed.emit(certain_count, suspect_count, num_file, result_file)

    def stop(self):
        self.flag = True


class MainWindow(QWidget):

    scan_stop = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()

        self.titleLb = QLabel('박스 스캐너', self)
        self.titleLb.setAlignment(Qt.AlignCenter)
        titleLbFont = self.titleLb.font()
        titleLbFont.setPointSize(16)
        self.titleLb.setFont(titleLbFont)

        self.settingLb = QLabel('옵션', self)
        self.subdirCB = QCheckBox('하위 폴더 포함', self)
        self.onlyimgCB = QCheckBox('이미지 확장자만 검사', self)
        self.scanBtn = QPushButton('시작', self)
        self.scanBtn.clicked.connect(self.scanBtnClicked)

        self.pBarLb = QLabel('진행률', self)
        self.pBar = QProgressBar(self)
        self.pBar.setFormat(r'%v/%m')

        scan_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.pathLb = QLabel('스캔 폴더', self)
        self.pathLE = QLineEdit(scan_dir, self)
        self.selectBtn = QPushButton('선택', self)
        self.selectBtn.clicked.connect(self.selectBtnClicked)

        self.copyrightLb = QLabel('developed by @RTFM', self)
        self.copyrightLb.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.versionLb = QLabel('v1.0.0', self)
        self.versionLb.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        self.grid.addWidget(self.titleLb, 0, 0, 1, 6)
        self.grid.addWidget(self.pathLb, 1, 0)
        self.grid.addWidget(self.pathLE, 1, 1, 1, 4)
        self.grid.addWidget(self.selectBtn, 1, 5)
        self.grid.addWidget(self.settingLb, 2, 0)
        self.grid.addWidget(self.subdirCB, 2, 1, 1, 2)
        self.grid.addWidget(self.onlyimgCB, 2, 3, 1, 2)
        self.grid.addWidget(self.scanBtn, 2, 5)
        self.grid.addWidget(self.pBarLb, 3, 0)
        self.grid.addWidget(self.pBar, 3, 1, 1, 5)
        self.grid.addWidget(self.copyrightLb, 4, 0, 1, 3)
        self.grid.addWidget(self.versionLb, 4, 3, 1, 3)

        for i in range(6):
            self.grid.setColumnMinimumWidth(i, 64)

        for i in range(5):
            self.grid.setRowMinimumHeight(i, 32)

        self.setLayout(self.grid)
        self.setWindowTitle('박스 스캐너')
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.setFixedSize(self.sizeHint())
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def pBar_setRange(self, minimum, maximum):
        self.pBar.setRange(minimum, maximum)

    def pBar_setValue(self, value):
        self.pBar.setValue(value)

    def scan_complete(self, certain, suspect, total, result_file):
        text = f'{total}개의 파일에서 {certain}({suspect})개의 박스(의심) 파일을 식별했습니다.'
        text += f'\n자세한 사항은 \'{result_file}\' 파일을 참조해주세요.' if result_file else ''
        QMessageBox.information(self, '스캔 완료', text)
        self.scanBtn.setText('시작')
        self.pBar.setRange(0, 100)
        self.pBar.reset()

    def scan_start(self, scan_dir, sub_dir, only_img):
        self.scanBtn.setText('중지')
        box_scanner = BoxScanner(scan_dir, sub_dir, only_img, self)
        box_scanner.pBar_setRange.connect(self.pBar_setRange)
        box_scanner.pBar_setValue.connect(self.pBar_setValue)
        box_scanner.completed.connect(self.scan_complete)
        self.scan_stop.connect(box_scanner.stop)
        box_scanner.start()

    def scanBtnClicked(self):
        if self.scanBtn.text() == '중지':
            self.scan_stop.emit()
            return

        scan_dir = self.pathLE.text()
        if not os.path.isdir(scan_dir):
            QMessageBox.warning(self, '오류', '잘못된 경로입니다.')
            return

        self.scan_start(os.path.abspath(scan_dir), self.subdirCB.isChecked(), self.onlyimgCB.isChecked())

    def selectBtnClicked(self):
        save_dir = str(QFileDialog.getExistingDirectory(self, '스캔 폴더 선택'))
        if save_dir:
            self.pathLE.setText(save_dir)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    exit_code = app.exec_()
    print(f'exit: {exit_code}')
    sys.exit(exit_code)
