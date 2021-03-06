# -*- coding: utf-8 -*-

"""Output dialog for slvs format."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2016-2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from abc import abstractmethod
from typing import (
    Tuple,
    Callable,
    Sequence,
    Optional,
)
from os.path import isdir, isfile
import shutil
from subprocess import Popen, DEVNULL
from core.QtModules import (
    pyqtSlot,
    Qt,
    QDialog,
    QDir,
    QMessageBox,
    QFileDialog,
    QTextEdit,
    QWidget,
    QLabel,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QIcon,
    QPixmap,
    QAbcMeta,
)
from core.libs import VPoint
from .slvs import slvs_frame, slvs_part
from .dxf import (
    DXF_VERSIONS,
    DXF_VERSIONS_MAP,
    dxf_frame,
    dxf_boundary,
)
from .Ui_output_option import Ui_Dialog


def _get_name(widget: QTextEdit, *, ispath: bool = False) -> str:
    """Return the file name of widget."""
    text = widget.text()
    place_text = widget.placeholderText()
    if ispath:
        return text if isdir(text) else place_text
    return ''.join(x for x in text if x.isalnum() or x in "._- ") or place_text


class _OutputDialog(QDialog, Ui_Dialog, metaclass=QAbcMeta):

    """Output dialog template."""

    def __init__(
        self,
        format_name: str,
        format_icon: str,
        assembly_description: str,
        frame_description: str,
        env: str,
        file_name: str,
        vpoints: Tuple[VPoint],
        v_to_slvs: Callable[[], Sequence[Tuple[int, int]]],
        parent: QWidget
    ):
        """Comes in environment variable and workbook name."""
        super(_OutputDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(f"Export {format_name} module project")
        self.setWindowIcon(QIcon(QPixmap(f":/icons/{format_icon}")))
        self.assembly_label.setText(assembly_description)
        self.frame_label.setText(frame_description)
        self.path_edit.setPlaceholderText(env)
        self.filename_edit.setPlaceholderText(file_name)
        self.vpoints = vpoints
        self.v_to_slvs = v_to_slvs

    @pyqtSlot(name='on_choose_dir_button_clicked')
    def __set_dir(self):
        """Choose path and it will be set as environment variable if accepted."""
        path = self.path_edit.text()
        if not isdir(path):
            path = self.path_edit.placeholderText()
        path = QFileDialog.getExistingDirectory(self, "Choose a directory", path)
        if path:
            self.path_edit.setText(path)

    @pyqtSlot(name='on_buttonBox_accepted')
    def __accepted(self):
        """Use the file path to export the project."""
        qdir = QDir(_get_name(self.path_edit, ispath=True))
        if self.newfolder_option.isChecked():
            new_folder = self.filename_edit.placeholderText()
            if (not qdir.mkdir(new_folder)) and self.warn_radio.isChecked():
                self.exist_warning(new_folder, folder=True)
                return
            qdir.cd(new_folder)
            del new_folder
        try:
            ok = self.do(qdir)
        except PermissionError as e:
            QMessageBox.warning(self, "Permission error", str(e))
        else:
            if ok:
                self.accept()

    @abstractmethod
    def do(self, dir_str: QDir) -> Optional[bool]:
        """Do the saving work here, return True if done."""
        ...

    def exist_warning(self, name: str, *, folder: bool = False):
        """Show the "file is exist" message box."""
        QMessageBox.warning(
            self,
            f"{'Folder' if folder else 'File'} exist",
            f"The folder named {name} is exist."
            if folder else
            f"The file {name} is exist."
        )


class SlvsOutputDialog(_OutputDialog):

    """Dialog for Solvespace format."""

    def __init__(self, *args):
        """Type name: "Solvespace module"."""
        super(SlvsOutputDialog, self).__init__(
            "Solvespace",
            "solvespace.ico",
            "The part sketchs file will be generated automatically "
            "with target directory.",
            "There is only sketch file of main mechanism will be generated.",
            *args
        )

    def do(self, dir_str: QDir) -> Optional[bool]:
        """Output types:

        + Assembly
        + Only wire frame
        """
        file_name = dir_str.filePath(_get_name(self.filename_edit) + '.slvs')
        if isfile(file_name) and self.warn_radio.isChecked():
            self.exist_warning(file_name)
            return

        # Wire frame
        slvs_frame(self.vpoints, self.v_to_slvs, file_name)

        # Open Solvespace by commend line if available.
        cmd = shutil.which("solvespace")
        if cmd:
            Popen([cmd, file_name], stdout=DEVNULL, stderr=DEVNULL)

        if self.frame_radio.isChecked():
            self.accept()
            return

        # Assembly
        vlinks = {}
        for i, vpoint in enumerate(self.vpoints):
            for link in vpoint.links:
                if link in vlinks:
                    vlinks[link].add(i)
                else:
                    vlinks[link] = {i}
        for name, points in vlinks.items():
            if name == 'ground':
                continue
            file_name = dir_str.filePath(name + '.slvs')
            if isfile(file_name) and self.warn_radio.isChecked():
                self.exist_warning(file_name)
                return
            slvs_part([
                self.vpoints[i] for i in points
            ], self.link_radius.value(), file_name)

        return True


class DxfOutputDialog(_OutputDialog):

    """Dialog for DXF format."""

    def __init__(self, *args):
        """Type name: "DXF module"."""
        super(DxfOutputDialog, self).__init__(
            "DXF",
            "dxf.png",
            "The part sketchs will including in the file.",
            "There is only wire frame will be generated.",
            *args
        )
        # DXF version option.
        version_label = QLabel("DXF version:", self)
        self.version_option = QComboBox(self)
        self.version_option.addItems(sorted((
            f"{name} - {DXF_VERSIONS_MAP[name]}" for name in DXF_VERSIONS
        ), key=lambda v: v.split()[-1]))
        self.version_option.setCurrentIndex(self.version_option.count() - 1)
        self.version_option.setSizePolicy(QSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        ))
        dxf_version_layout = QHBoxLayout()
        dxf_version_layout.addWidget(version_label)
        dxf_version_layout.addWidget(self.version_option)
        self.main_layout.insertLayout(3, dxf_version_layout)
        # Parts interval.
        self.interval_enable = QCheckBox("Parts interval:", self)
        self.interval_enable.setCheckState(Qt.Checked)
        self.interval_option = QDoubleSpinBox(self)
        self.interval_option.setValue(10)
        self.interval_enable.stateChanged.connect(self.interval_option.setEnabled)
        dxf_interval_layout = QHBoxLayout()
        dxf_interval_layout.addWidget(self.interval_enable)
        dxf_interval_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        dxf_interval_layout.addWidget(self.interval_option)
        self.assembly_layout.insertLayout(2, dxf_interval_layout)

    def do(self, dir_str: QDir) -> Optional[bool]:
        """Output types:

        + Boundary
        + Frame
        """
        file_name = dir_str.filePath(_get_name(self.filename_edit) + '.dxf')
        if isfile(file_name) and self.warn_radio.isChecked():
            self.exist_warning(file_name)
            return

        version = self.version_option.currentText().split()[0]

        if self.frame_radio.isChecked():
            # Frame
            dxf_frame(
                self.vpoints,
                self.v_to_slvs,
                version,
                file_name
            )
        elif self.assembly_radio.isChecked():
            # Boundary
            dxf_boundary(
                self.vpoints,
                self.link_radius.value(),
                self.interval_option.value()
                if self.interval_enable.isChecked() else None,
                version,
                file_name
            )

        return True
