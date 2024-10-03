# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QGridLayout,
    QHeaderView, QLabel, QMainWindow, QPushButton,
    QSizePolicy, QStatusBar, QTextBrowser, QTreeView,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(711, 577)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.PB_sc_delete = QPushButton(self.centralwidget)
        self.PB_sc_delete.setObjectName(u"PB_sc_delete")
        font = QFont()
        font.setPointSize(10)
        self.PB_sc_delete.setFont(font)

        self.gridLayout.addWidget(self.PB_sc_delete, 2, 5, 1, 1)

        self.PB_sc_create = QPushButton(self.centralwidget)
        self.PB_sc_create.setObjectName(u"PB_sc_create")
        self.PB_sc_create.setFont(font)

        self.gridLayout.addWidget(self.PB_sc_create, 2, 4, 1, 1)

        self.scality_fs_tree = QTreeView(self.centralwidget)
        self.scality_fs_tree.setObjectName(u"scality_fs_tree")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scality_fs_tree.sizePolicy().hasHeightForWidth())
        self.scality_fs_tree.setSizePolicy(sizePolicy)
        self.scality_fs_tree.setStyleSheet(u"")
        self.scality_fs_tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.scality_fs_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scality_fs_tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.scality_fs_tree.setHeaderHidden(True)

        self.gridLayout.addWidget(self.scality_fs_tree, 3, 4, 6, 2)

        self.local_fs_tree = QTreeView(self.centralwidget)
        self.local_fs_tree.setObjectName(u"local_fs_tree")
        sizePolicy.setHeightForWidth(self.local_fs_tree.sizePolicy().hasHeightForWidth())
        self.local_fs_tree.setSizePolicy(sizePolicy)
        self.local_fs_tree.setStyleSheet(u"")
        self.local_fs_tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.local_fs_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.local_fs_tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.local_fs_tree.setHeaderHidden(True)

        self.gridLayout.addWidget(self.local_fs_tree, 3, 0, 6, 2)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        font1 = QFont()
        font1.setPointSize(14)
        self.label_2.setFont(font1)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_2, 0, 4, 1, 2)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.PB_fs_create = QPushButton(self.centralwidget)
        self.PB_fs_create.setObjectName(u"PB_fs_create")
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(False)
        self.PB_fs_create.setFont(font2)

        self.gridLayout.addWidget(self.PB_fs_create, 2, 0, 1, 1)

        self.PB_fs_delete = QPushButton(self.centralwidget)
        self.PB_fs_delete.setObjectName(u"PB_fs_delete")
        self.PB_fs_delete.setFont(font)

        self.gridLayout.addWidget(self.PB_fs_delete, 2, 1, 1, 1)

        self.TB_status = QTextBrowser(self.centralwidget)
        self.TB_status.setObjectName(u"TB_status")
        palette = QPalette()
        brush = QBrush(QColor(187, 255, 183, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush1 = QBrush(QColor(240, 240, 240, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        self.TB_status.setPalette(palette)

        self.gridLayout.addWidget(self.TB_status, 10, 0, 1, 6)

        self.PB_download = QPushButton(self.centralwidget)
        self.PB_download.setObjectName(u"PB_download")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.PB_download.sizePolicy().hasHeightForWidth())
        self.PB_download.setSizePolicy(sizePolicy1)
        self.PB_download.setMinimumSize(QSize(0, 50))
        font3 = QFont()
        font3.setPointSize(15)
        self.PB_download.setFont(font3)

        self.gridLayout.addWidget(self.PB_download, 6, 2, 1, 2)

        self.PB_upload = QPushButton(self.centralwidget)
        self.PB_upload.setObjectName(u"PB_upload")
        sizePolicy1.setHeightForWidth(self.PB_upload.sizePolicy().hasHeightForWidth())
        self.PB_upload.setSizePolicy(sizePolicy1)
        self.PB_upload.setMinimumSize(QSize(0, 50))
        self.PB_upload.setFont(font3)

        self.gridLayout.addWidget(self.PB_upload, 5, 2, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.PB_sc_delete.setText(QCoreApplication.translate("MainWindow", u"Delete Folder", None))
        self.PB_sc_create.setText(QCoreApplication.translate("MainWindow", u"Create Folder", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Scality", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Local", None))
        self.PB_fs_create.setText(QCoreApplication.translate("MainWindow", u"Create Folder", None))
        self.PB_fs_delete.setText(QCoreApplication.translate("MainWindow", u"Delete Folder", None))
        self.PB_download.setText(QCoreApplication.translate("MainWindow", u"<", None))
        self.PB_upload.setText(QCoreApplication.translate("MainWindow", u">", None))
    # retranslateUi

