# -*- coding: utf-8 -*-

"""SQL database output function."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2016-2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from os import remove as os_remove
from os.path import isfile
from typing import (
    Tuple,
    List,
    Sequence,
    Dict,
    Union,
    Optional,
    Any,
)
import datetime
from zlib import compress, decompress
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    BlobField,
    ForeignKeyField,
    DateTimeField,
)
from core.QtModules import (
    QPushButton,
    pyqtSignal,
    QIcon,
    QPixmap,
    QFileInfo,
    QWidget,
    pyqtSlot,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QTableWidgetItem,
)
from core import main_window as mw
from core.libs import example_list
from .overview import OverviewDialog
from .Ui_database import Ui_Form
nan = float('nan')


def _compress(obj: Any) -> bytes:
    """Use to encode the Python script as bytes code."""
    return compress(bytes(repr(obj), encoding="utf8"), 5)


def _decompress(obj: Union[bytes, BlobField]) -> Any:
    """Use to decode the Python script."""
    return eval(decompress(obj).decode())


"""Create a empty Sqlite database object."""
_db = SqliteDatabase(None)


class UserModel(Model):

    """Show who committed the workbook."""

    name = CharField(unique=True)

    class Meta:
        database = _db


class BranchModel(Model):

    """The branch in this workbook."""

    name = CharField(unique=True)

    class Meta:
        database = _db


class CommitModel(Model):

    """Commit data: Mechanism and Workbook information.

    + Previous and branch commit.
    + Commit time.
    + Workbook information.
    + Expression using Lark parser.
    + Storage data.
    + Path data.
    + Collection data.
    + Triangle collection data.
    + Input variables data.
    + Algorithm data.
    """

    previous = ForeignKeyField('self', related_name='next', null=True)
    branch = ForeignKeyField(BranchModel, null=True)

    date = DateTimeField(default=datetime.datetime.now)

    author = ForeignKeyField(UserModel, null=True)
    description = CharField()

    mechanism = BlobField()
    linkcolor = BlobField()

    storage = BlobField()

    pathdata = BlobField()

    collectiondata = BlobField()

    triangledata = BlobField()

    inputsdata = BlobField()

    algorithmdata = BlobField()

    class Meta:
        database = _db


class LoadCommitButton(QPushButton):

    """The button of load commit."""

    loaded = pyqtSignal(int)

    def __init__(self, id_int: int, parent: QWidget):
        super(LoadCommitButton, self).__init__(
            QIcon(QPixmap(":icons/data_update.png")),
            f" # {id_int}",
            parent
        )
        self.setToolTip(f"Reset to commit # {id_int}.")
        self.id = id_int

    def mouseReleaseEvent(self, event):
        """Load the commit when release button."""
        super(LoadCommitButton, self).mouseReleaseEvent(event)
        self.loaded.emit(self.id)

    def set_loaded(self, id_int: int):
        """Set enable if this commit is been loaded."""
        self.setEnabled(id_int != self.id)


class DatabaseWidget(QWidget, Ui_Form):

    """The table that stored workbook data and changes."""

    load_id = pyqtSignal(int)

    def __init__(self, parent: 'mw.MainWindow'):
        super(DatabaseWidget, self).__init__(parent)
        self.setupUi(self)

        # ID
        self.CommitTable.setColumnWidth(0, 70)
        # Date
        self.CommitTable.setColumnWidth(1, 70)
        # Description
        self.CommitTable.setColumnWidth(2, 130)
        # Author
        self.CommitTable.setColumnWidth(3, 70)
        # Previous
        self.CommitTable.setColumnWidth(4, 70)
        # Branch
        self.CommitTable.setColumnWidth(5, 70)

        # Check file changed function.
        self.__check_file_changed = parent.checkFileChanged
        # Check workbook saved function.
        self.__workbook_saved = parent.workbookSaved

        # Call to get point expressions.
        self.__point_expr_func = parent.EntitiesPoint.expression
        # Call to get link data.
        self.__link_expr_func = parent.EntitiesLink.colors
        # Call to get storage data.
        self.__storage_data_func = parent.getStorage
        # Call to get collections data.
        self.__collect_data_func = parent.CollectionTabPage.collect_data
        # Call to get triangle data.
        self.__triangle_data_func = parent.CollectionTabPage.triangle_data
        # Call to get inputs variables data.
        self.__inputs_data_func = parent.InputsWidget.inputPairs
        # Call to get algorithm data.
        self.__algorithm_data_func = parent.DimensionalSynthesis.mechanism_data
        # Call to get path data.
        self.__path_data_func = parent.InputsWidget.pathData

        # Add empty links function.
        self.__add_links_func = parent.addEmptyLinks
        # Parse function.
        self.__parse_func = parent.parseExpression

        # Call to load inputs variables data.
        self.__load_inputs_func = parent.InputsWidget.addInputsVariables
        # Add storage function.
        self.__add_storage_func = parent.addMultipleStorage
        # Call to load paths.
        self.__load_path_func = parent.InputsWidget.loadPaths
        # Call to load collections data.
        self.__load_collect_func = parent.CollectionTabPage.StructureWidget.addCollections
        # Call to load triangle data.
        self.__load_triangle_func = parent.CollectionTabPage.TriangularIterationWidget.addCollections
        # Call to load algorithm results.
        self.__load_algorithm_func = parent.DimensionalSynthesis.loadResults

        # Clear function for main window.
        self.__clear_func = parent.clear


        # Close database when destroyed.
        self.destroyed.connect(self.__close_database)
        # Undo Stack
        self.__command_clear = parent.CommandStack.clear

        # Reset
        self.history_commit = None
        self.file_name = QFileInfo("Untitled")
        self.last_time = datetime.datetime.now()
        self.changed = False
        self.Stack = 0
        self.reset()

    def reset(self):
        """Clear all the things that dependent on database."""
        self.history_commit: Optional[CommitModel] = None
        self.file_name = QFileInfo("Untitled")
        self.last_time = datetime.datetime.now()
        self.changed = False
        self.Stack = 0
        self.__command_clear()
        for row in range(self.CommitTable.rowCount()):
            self.CommitTable.removeRow(0)
        self.BranchList.clear()
        self.AuthorList.clear()
        self.FileAuthor.clear()
        self.FileDescription.clear()
        self.branch_current.clear()
        self.commit_search_text.clear()
        self.commit_current_id.setValue(0)
        self.__close_database()

    def setFileName(self, file_name: str):
        """Set file name."""
        self.file_name = QFileInfo(file_name)

    def __connect_database(self, file_name: str):
        """Connect database."""
        self.__close_database()
        _db.init(file_name)
        _db.connect()
        _db.create_tables([CommitModel, UserModel, BranchModel], safe=True)

    @pyqtSlot()
    def __close_database(self):
        if not _db.deferred:
            _db.close()

    def save(self, file_name: str, is_branch: bool = False):
        """Save database, append commit to new branch function."""
        author_name = self.FileAuthor.text() or self.FileAuthor.placeholderText()
        branch_name = '' if is_branch else self.branch_current.text()
        commit_text = self.FileDescription.text()
        while not author_name:
            author_name, ok = QInputDialog.getText(
                self,
                "Author",
                "Please enter author's name:",
                QLineEdit.Normal,
                "Anonymous"
            )
            if not ok:
                return
        while not branch_name.isidentifier():
            branch_name, ok = QInputDialog.getText(
                self,
                "Branch",
                "Please enter a branch name:",
                QLineEdit.Normal,
                "master"
            )
            if not ok:
                return
        while not commit_text:
            commit_text, ok = QInputDialog.getText(
                self,
                "Commit",
                "Please add a comment:",
                QLineEdit.Normal,
                "Update mechanism."
            )
            if not ok:
                return
        if (file_name != self.file_name.absoluteFilePath()) and isfile(file_name):
            os_remove(file_name)
            print("The original file has been overwritten.")
        self.__connect_database(file_name)
        is_error = False
        with _db.atomic():
            if author_name in (user.name for user in UserModel.select()):
                author_model = (
                    UserModel
                    .select()
                    .where(UserModel.name == author_name)
                    .get()
                )
            else:
                author_model = UserModel(name=author_name)
            if branch_name in (branch.name for branch in BranchModel.select()):
                branch_model = (
                    BranchModel
                    .select()
                    .where(BranchModel.name == branch_name)
                    .get()
                )
            else:
                branch_model = BranchModel(name=branch_name)
            args = {
                'author': author_model,
                'description': commit_text,
                'mechanism': _compress(self.__point_expr_func()),
                'linkcolor': _compress(self.__link_expr_func()),
                'storage': _compress(list(self.__storage_data_func())),
                'pathdata': _compress(self.__path_data_func()),
                'collectiondata': _compress(self.__collect_data_func()),
                'triangledata': _compress(self.__triangle_data_func()),
                'inputsdata': _compress(tuple((b, d) for b, d, a in self.__inputs_data_func())),
                'algorithmdata': _compress(self.__algorithm_data_func()),
                'branch': branch_model,
            }
            try:
                args['previous'] = (
                    CommitModel
                    .select()
                    .where(CommitModel.id == self.commit_current_id.value())
                    .get()
                )
            except CommitModel.DoesNotExist:
                args['previous'] = None
            new_commit = CommitModel(**args)
            try:
                author_model.save()
                branch_model.save()
                new_commit.save()
            except Exception as e:
                print(str(e))
                _db.rollback()
                is_error = True
            else:
                self.history_commit = CommitModel.select().order_by(CommitModel.id)
        if is_error:
            os_remove(file_name)
            print("The file was removed.")
            return
        self.read(file_name)
        print(f"Saving \"{file_name}\" successful.")
        size = QFileInfo(file_name).size()
        print("Size: " + (
            f"{size / 1024 / 1024:.02f} MB"
            if size / 1024 // 1024 else
            f"{size / 1024:.02f} KB"
        ))

    def read(self, file_name: str):
        """Load database commit."""
        self.__connect_database(file_name)
        history_commit = CommitModel.select().order_by(CommitModel.id)
        commit_count = len(history_commit)
        if not commit_count:
            QMessageBox.warning(
                self,
                "Warning",
                "This file is a non-committed database."
            )
            return
        self.__clear_func()
        self.reset()
        self.history_commit = history_commit
        for commit in self.history_commit:
            self.__add_commit(commit)
        print(f"{commit_count} commit(s) was find in database.")
        self.__load_commit(self.history_commit.order_by(-CommitModel.id).get())
        self.file_name = QFileInfo(file_name)
        self.__workbook_saved()

    def importMechanism(self, file_name: str):
        """Pick and import the latest mechanism from a branch."""
        self.__connect_database(file_name)
        commit_all = CommitModel.select().join(BranchModel)
        branch_all = BranchModel.select().order_by(BranchModel.name)
        if self.history_commit:
            self.__connect_database(self.file_name.absoluteFilePath())
        else:
            self.__close_database()
        branch_name, ok = QInputDialog.getItem(
            self,
            "Branch",
            "Select the latest commit in the branch to load.",
            [branch.name for branch in branch_all],
            0,
            False
        )
        if not ok:
            return
        try:
            commit = (
                commit_all
                .where(BranchModel.name == branch_name)
                .order_by(CommitModel.date)
                .get()
            )
        except CommitModel.DoesNotExist:
            QMessageBox.warning(
                self,
                "Warning",
                "This file is a non-committed database."
            )
        else:
            self.__import_commit(commit)

    def __add_commit(self, commit: CommitModel):
        """Add commit data to all widgets.

        + Commit ID
        + Date
        + Description
        + Author
        + Previous commit
        + Branch
        + Add to table widget.
        """
        row = self.CommitTable.rowCount()
        self.CommitTable.insertRow(row)

        self.commit_current_id.setValue(commit.id)
        button = LoadCommitButton(commit.id, self)
        button.loaded.connect(self.__load_commit_id)
        self.load_id.connect(button.set_loaded)
        self.CommitTable.setCellWidget(row, 0, button)

        self.CommitTable.setItem(row, 2, QTableWidgetItem(commit.description))

        author_name = commit.author.name
        for row in range(self.AuthorList.count()):
            if author_name == self.AuthorList.item(row).text():
                break
        else:
            self.AuthorList.addItem(author_name)

        branch_name = commit.branch.name
        for row in range(self.BranchList.count()):
            if branch_name == self.BranchList.item(row).text():
                break
        else:
            self.BranchList.addItem(branch_name)
        self.branch_current.setText(branch_name)
        t = commit.date
        for i, text in enumerate((
            f"{t.year:02d}-{t.month:02d}-{t.day:02d} "
            f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}",
            commit.description,
            author_name,
            f"#{commit.previous.id}" if commit.previous else "None",
            branch_name
        )):
            item = QTableWidgetItem(text)
            item.setToolTip(text)
            self.CommitTable.setItem(row, i + 1, item)

    def __load_commit_id(self, id_int: int):
        """Check the id_int is correct."""
        try:
            commit = self.history_commit.where(CommitModel.id == id_int).get()
        except CommitModel.DoesNotExist:
            QMessageBox.warning(self, "Warning", "Commit ID is not exist.")
        except AttributeError:
            QMessageBox.warning(self, "Warning", "Nothing submitted.")
        else:
            self.__load_commit(commit)

    def __load_commit(self, commit: CommitModel):
        """Load the commit pointer."""
        if self.__check_file_changed():
            return
        # Reset the main window status.
        self.__clear_func()
        # Load the commit to widgets.
        print(f"Loading commit # {commit.id}.")
        self.load_id.emit(commit.id)
        self.commit_current_id.setValue(commit.id)
        self.branch_current.setText(commit.branch.name)
        # Load the expression.
        self.__add_links_func(_decompress(commit.linkcolor))
        self.__parse_func(_decompress(commit.mechanism))
        # Load inputs data.
        input_data: Sequence[Tuple[int, int]] = _decompress(commit.inputsdata)
        self.__load_inputs_func(input_data)
        # Load the storage.
        storage_data: List[Tuple[str, str]] = _decompress(commit.storage)
        self.__add_storage_func(storage_data)
        # Load path data.
        path_data: Dict[str, Sequence[Tuple[float, float]]] = _decompress(commit.pathdata)
        self.__load_path_func(path_data)
        # Load collection data.
        collection_data: List[Tuple[Tuple[int, int], ...]] = _decompress(commit.collectiondata)
        self.__load_collect_func(collection_data)
        # Load triangle data.
        triangle_data: Dict[str, Dict[str, Any]] = _decompress(commit.triangledata)
        self.__load_triangle_func(triangle_data)
        # Load algorithm data.
        algorithm_data: List[Dict[str, Any]] = _decompress(commit.algorithmdata)
        self.__load_algorithm_func(algorithm_data)

        # Workbook loaded.
        self.__workbook_saved()
        print("The specified phase has been loaded.")

        # Show overview dialog.
        dlg = OverviewDialog(
            self,
            f"{commit.branch.name} - commit # {commit.id}",
            storage_data,
            input_data,
            path_data,
            collection_data,
            triangle_data,
            algorithm_data
        )
        dlg.show()
        dlg.exec_()

    def __import_commit(self, commit: CommitModel):
        """Just load the expression. (No clear step!)"""
        self.__parse_func(_decompress(commit.mechanism))
        print("The specified phase has been merged.")

    @pyqtSlot(name='on_commit_stash_clicked')
    def stash(self):
        """Reload the least commit ID."""
        self.__load_commit_id(self.commit_current_id.value())

    def loadExample(self, is_import: bool = False) -> bool:
        """Load example to new workbook."""
        if self.__check_file_changed():
            return False
        # load example by expression.
        example_name, ok = QInputDialog.getItem(
            self,
            "Examples",
            "Select an example to load:",
            sorted(example_list),
            0,
            False
        )
        if not ok:
            return False
        expr, inputs = example_list[example_name]
        if not is_import:
            self.reset()
            self.__clear_func()
        self.__parse_func(expr)
        if not is_import:
            # Import without input data.
            self.__load_inputs_func(inputs)
        self.file_name = QFileInfo(example_name)
        self.__workbook_saved()
        print(f"Example \"{example_name}\" has been loaded.")
        return True

    @pyqtSlot(str, name='on_commit_search_text_textEdited')
    def __set_search_text(self, text: str):
        """Commit filter (by description and another)."""
        if not text:
            for row in range(self.CommitTable.rowCount()):
                self.CommitTable.setRowHidden(row, False)
            return
        for row in range(self.CommitTable.rowCount()):
            self.CommitTable.setRowHidden(row, not (
                (text in self.CommitTable.item(row, 2).text()) or
                (text in self.CommitTable.item(row, 3).text())
            ))

    @pyqtSlot(str, name='on_AuthorList_currentTextChanged')
    def __set_author(self, text: str):
        """Change default author's name when select another author."""
        self.FileAuthor.setPlaceholderText(text)

    @pyqtSlot(name='on_branch_checkout_clicked')
    def __checkout_branch(self):
        """Switch to the last commit of branch."""
        if not self.BranchList.currentRow() > -1:
            return
        branch_name = self.BranchList.currentItem().text()
        if branch_name == self.branch_current.text():
            return
        least_commit = (
            self.history_commit
            .join(BranchModel)
            .where(BranchModel.name == branch_name)
            .order_by(-CommitModel.date)
            .get()
        )
        self.__load_commit(least_commit)

    @pyqtSlot(name='on_branch_delete_clicked')
    def __delete_branch(self):
        """Delete all commits in the branch."""
        if not self.BranchList.currentRow() > -1:
            return
        branch_name = self.BranchList.currentItem().text()
        if branch_name == self.branch_current.text():
            QMessageBox.warning(
                self,
                "Warning",
                "Cannot delete current branch."
            )
            return
        file_name = self.file_name.absoluteFilePath()
        # Connect on database to remove all the commit in this branch.
        with _db.atomic():
            CommitModel.delete().where(CommitModel.branch.in_(
                BranchModel
                .select()
                .where(BranchModel.name == branch_name)
            )).execute()
            BranchModel.delete().where(BranchModel.name == branch_name).execute()
        _db.close()
        print(f"Branch {branch_name} was deleted.")
        # Reload database.
        self.read(file_name)
