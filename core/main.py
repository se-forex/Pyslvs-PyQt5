# -*- coding: utf-8 -*-
'''
PySolvespace - PyQt 5 GUI with Solvespace Library
Copyright (C) 2016 Yuan Chang
E-mail: daan0014119@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
'''
from .modules import *
_translate = QCoreApplication.translate
#Self UI Ports
from .Ui_main import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        #File & Default Setting
        self.File = File()
        self.load_settings()
        self.FileState = QUndoStack()
        #QPainter Window
        self.qpainterWindow = DynamicCanvas()
        self.mplLayout.insertWidget(0, self.qpainterWindow)
        self.qpainterWindow.show()
        self.Resolve()
        #Solve & Script & DOF & Mask & Parameter
        self.Solvefail = False
        self.Script = ""
        self.DOF = 0
        self.Mask_Change()
        self.init_Right_click_menu()
        self.Parameter_digital.setValidator(QRegExpValidator(QRegExp('^[-]?([1-9][0-9]{1,'+str(self.Default_Bits-2)+'})?[0-9][.][0-9]{1,'+str(self.Default_Bits)+'}$')))
        if len(sys.argv)>2: self.argvLoadFile()
    
    #LoadFile
    def argvLoadFile(self):
        if ".csv" in sys.argv[1].lower():
            try: self.loadWorkbook(sys.argv[1])
            except: print("Error when loading file.")
        elif "example" in sys.argv[1].lower():
            try:
                ExampleNum = int(sys.argv[1].lower().replace("example", ''))
                if ExampleNum==0: self.on_actionCrank_rocker_triggered()
                elif ExampleNum==1: self.on_actionDrag_link_triggered()
                elif ExampleNum==2: self.on_actionDouble_rocker_triggered()
                elif ExampleNum==3: self.on_actionParallelogram_linkage_triggered()
                elif ExampleNum==4: self.on_actionMutiple_Link_triggered()
                elif ExampleNum==5: self.on_actionTwo_Mutiple_Link_triggered()
                elif ExampleNum==6: self.on_actionReverse_Parsing_Rocker_triggered()
            except: print("Error when loading example.")
    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            for url in mimeData.urls():
                FilePath = url.toLocalFile()
                if QFileInfo(FilePath).suffix()=="csv": event.acceptProposedAction()
    def dropEvent(self, event):
        FilePath = event.mimeData().urls()[-1].toLocalFile()
        self.checkChange(FilePath, [], "Loaded drag-in file:\n"+FilePath)
        event.acceptProposedAction()
    
    def load_settings(self):
        option_info = Pyslvs_Settings_ini()
        self.Default_Environment_variables = option_info.Environment_variables
        self.Default_canvas_view = option_info.Zoom_factor
        self.Default_Bits = 8
    
    def init_Right_click_menu(self):
        #qpainterWindow Right-click menu
        self.qpainterWindow.setContextMenuPolicy(Qt.CustomContextMenu)
        self.qpainterWindow.customContextMenuRequested.connect(self.on_painter_context_menu)
        self.popMenu_painter = QMenu(self)
        self.action_painter_right_click_menu_add = QAction("Add a Point", self)
        self.popMenu_painter.addAction(self.action_painter_right_click_menu_add)
        self.action_painter_right_click_menu_fix_add = QAction("Add a Fixed Point", self)
        self.popMenu_painter.addAction(self.action_painter_right_click_menu_fix_add)
        self.action_painter_right_click_menu_path_add = QAction("Add a Path Point [Path Solving]", self)
        self.popMenu_painter.addAction(self.action_painter_right_click_menu_path_add)
        self.popMenu_painter.addSeparator()
        self.action_painter_right_click_menu_dimension_add = QAction("Show Dimension", self)
        self.popMenu_painter.addAction(self.action_painter_right_click_menu_dimension_add)
        self.action_painter_right_click_menu_dimension_path_track = QAction("Show Path Track", self)
        self.popMenu_painter.addAction(self.action_painter_right_click_menu_dimension_path_track)
        self.mouse_pos_x = 0.0
        self.mouse_pos_y = 0.0
        self.qpainterWindow.mouse_track.connect(self.context_menu_mouse_pos)
        #Entiteis_Point Right-click menu
        self.Entiteis_Point_Widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Entiteis_Point_Widget.customContextMenuRequested.connect(self.on_point_context_menu)
        self.popMenu_point = QMenu(self)
        self.action_point_right_click_menu_copy = QAction("Copy Coordinate", self)
        self.popMenu_point.addAction(self.action_point_right_click_menu_copy)
        self.action_point_right_click_menu_coverage = QAction("Coverage Coordinate", self)
        self.popMenu_point.addAction(self.action_point_right_click_menu_coverage)
        self.action_point_right_click_menu_add = QAction("Add a Point", self)
        self.popMenu_point.addAction(self.action_point_right_click_menu_add)
        self.action_point_right_click_menu_edit = QAction("Edit this Point", self)
        self.popMenu_point.addAction(self.action_point_right_click_menu_edit)
        self.popMenu_point.addSeparator()
        self.action_point_right_click_menu_delete = QAction("Delete this Point", self)
        self.popMenu_point.addAction(self.action_point_right_click_menu_delete) 
        #Entiteis_Link Right-click menu
        self.Entiteis_Link_Widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Entiteis_Link_Widget.customContextMenuRequested.connect(self.on_link_context_menu)
        self.popMenu_link = QMenu(self)
        self.action_link_right_click_menu_add = QAction("Add a Link", self)
        self.popMenu_link.addAction(self.action_link_right_click_menu_add)
        self.action_link_right_click_menu_edit = QAction("Edit this Link", self)
        self.popMenu_link.addAction(self.action_link_right_click_menu_edit)
        self.action_link_right_click_menu_shaft = QAction("Turn this Link to Shaft", self)
        self.popMenu_link.addAction(self.action_link_right_click_menu_shaft)
        self.action_link_right_click_menu_reversion = QAction("Reverse Node point Y Coordinate", self)
        self.popMenu_link.addAction(self.action_link_right_click_menu_reversion)
        self.popMenu_link.addSeparator()
        self.action_link_right_click_menu_delete = QAction("Delete this Link", self)
        self.popMenu_link.addAction(self.action_link_right_click_menu_delete) 
        #Entiteis_Chain Right-click menu
        self.Entiteis_Stay_Chain_Widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Entiteis_Stay_Chain_Widget.customContextMenuRequested.connect(self.on_chain_context_menu)
        self.popMenu_chain = QMenu(self)
        self.action_chain_right_click_menu_add = QAction("Add a Chain", self)
        self.popMenu_chain.addAction(self.action_chain_right_click_menu_add)
        self.action_chain_right_click_menu_edit = QAction("Edit this Chain", self)
        self.popMenu_chain.addAction(self.action_chain_right_click_menu_edit)
        self.popMenu_chain.addSeparator()
        self.action_chain_right_click_menu_delete = QAction("Delete this Chain", self)
        self.popMenu_chain.addAction(self.action_chain_right_click_menu_delete) 
        #Drive_Shaft Right-click menu
        self.Drive_Shaft_Widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Drive_Shaft_Widget.customContextMenuRequested.connect(self.on_shaft_context_menu)
        self.popMenu_shaft = QMenu(self)
        self.action_shaft_right_click_menu_add = QAction("Add a Drive Shaft", self)
        self.popMenu_shaft.addAction(self.action_shaft_right_click_menu_add)
        self.action_shaft_right_click_menu_edit = QAction("Edit this Drive Shaft", self)
        self.popMenu_shaft.addAction(self.action_shaft_right_click_menu_edit)
        self.popMenu_shaft.addSeparator()
        self.action_shaft_right_click_menu_move_up = QAction("Move up", self)
        self.popMenu_shaft.addAction(self.action_shaft_right_click_menu_move_up)
        self.action_shaft_right_click_menu_move_down = QAction("Move down", self)
        self.popMenu_shaft.addAction(self.action_shaft_right_click_menu_move_down)
        self.popMenu_shaft.addSeparator()
        self.action_shaft_right_click_menu_delete = QAction("Delete this Drive Shaft", self)
        self.popMenu_shaft.addAction(self.action_shaft_right_click_menu_delete) 
        #Slider Right-click menu
        self.Slider_Widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Slider_Widget.customContextMenuRequested.connect(self.on_slider_context_menu)
        self.popMenu_slider = QMenu(self)
        self.action_slider_right_click_menu_add = QAction("Add a Slider", self)
        self.popMenu_slider.addAction(self.action_slider_right_click_menu_add)
        self.action_slider_right_click_menu_edit = QAction("Edit this Slider", self)
        self.popMenu_slider.addAction(self.action_slider_right_click_menu_edit)
        self.popMenu_slider.addSeparator()
        self.action_slider_right_click_menu_delete = QAction("Delete this Slider", self)
        self.popMenu_slider.addAction(self.action_slider_right_click_menu_delete) 
        #Rod Right-click menu
        self.Rod_Widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Rod_Widget.customContextMenuRequested.connect(self.on_rod_context_menu)
        self.popMenu_rod = QMenu(self)
        self.action_rod_right_click_menu_add = QAction("Add a Rod", self)
        self.popMenu_rod.addAction(self.action_rod_right_click_menu_add)
        self.action_rod_right_click_menu_edit = QAction("Edit this Rod", self)
        self.popMenu_rod.addAction(self.action_rod_right_click_menu_edit)
        self.popMenu_rod.addSeparator()
        self.action_rod_right_click_menu_delete = QAction("Delete this Rod", self)
        self.popMenu_rod.addAction(self.action_rod_right_click_menu_delete)
        #Parameter Right-click menu
        self.Parameter_Widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Parameter_Widget.customContextMenuRequested.connect(self.on_parameter_context_menu)
        self.popMenu_parameter = QMenu(self)
        self.action_parameter_right_click_menu_copy = QAction("Copy Parameter", self)
        self.popMenu_parameter.addAction(self.action_parameter_right_click_menu_copy)
        self.action_parameter_right_click_menu_add = QAction("Add a Parameter", self)
        self.popMenu_parameter.addAction(self.action_parameter_right_click_menu_add)
        self.popMenu_parameter.addSeparator()
        self.action_parameter_right_click_menu_move_up = QAction("Move up", self)
        self.popMenu_parameter.addAction(self.action_parameter_right_click_menu_move_up)
        self.action_parameter_right_click_menu_move_down = QAction("Move down", self)
        self.popMenu_parameter.addAction(self.action_parameter_right_click_menu_move_down)
        self.popMenu_parameter.addSeparator()
        self.action_parameter_right_click_menu_delete = QAction("Delete this Parameter", self)
        self.popMenu_parameter.addAction(self.action_parameter_right_click_menu_delete)
        #Action Enabled
        self.actionEnabled()
    
    #TODO: Right-click menu event
    @pyqtSlot(float, float)
    def context_menu_mouse_pos(self, x, y):
        self.mouse_pos_x = x
        self.mouse_pos_y = y
    def on_painter_context_menu(self, point):
        self.action_painter_right_click_menu_path_add.setVisible(hasattr(self, 'PathSolvingDlg'))
        action = self.popMenu_painter.exec_(self.qpainterWindow.mapToGlobal(point))
        table1 = self.Entiteis_Point
        table2 = self.Entiteis_Point_Style
        x = self.mouse_pos_x
        y = self.mouse_pos_y
        if action == self.action_painter_right_click_menu_add:
            self.File.Points.editTable(table1, str(x), str(y), False)
            self.File.Points.styleAdd(table2, "Green", "5", "Green")
            self.Resolve()
        elif action == self.action_painter_right_click_menu_fix_add:
            self.File.Points.editTable(table1, str(x), str(y), True)
            self.File.Points.styleAdd(table2, "Green", "10", "Green")
            self.Resolve()
        elif action == self.action_painter_right_click_menu_path_add: self.PathSolving_add_rightClick(x, y)
        elif action == self.action_painter_right_click_menu_dimension_add:
            if self.actionDisplay_Dimensions.isChecked()==False: self.action_painter_right_click_menu_dimension_add.setText("Hide Dimension")
            elif self.actionDisplay_Dimensions.isChecked()==True: self.action_painter_right_click_menu_dimension_add.setText("Show Dimension")
            self.action_painter_right_click_menu_dimension_add.setChecked(not self.actionDisplay_Dimensions.isChecked())
            self.actionDisplay_Dimensions.setChecked(not self.actionDisplay_Dimensions.isChecked())
        elif action == self.action_painter_right_click_menu_dimension_path_track:
            if self.Path_data_show.checkState()==True: self.action_painter_right_click_menu_dimension_path_track.setText("Hide Path Track")
            elif self.Path_data_show.checkState()==False: self.action_painter_right_click_menu_dimension_path_track.setText("Show Path Track")
            self.Path_data_show.setChecked(not self.Path_data_show.checkState())
            self.on_Path_data_show_clicked()
    def on_point_context_menu(self, point):
        self.action_point_right_click_menu_delete.setEnabled(self.Entiteis_Point.rowCount()>1 and self.Entiteis_Point.currentRow()!=0)
        self.action_point_right_click_menu_edit.setEnabled(self.Entiteis_Point.rowCount()>1 and self.Entiteis_Point.currentRow()!=0)
        self.action_point_right_click_menu_coverage.setVisible(self.Entiteis_Point.currentColumn()==4 and self.Entiteis_Point.currentRow()!=0)
        action = self.popMenu_point.exec_(self.Entiteis_Point_Widget.mapToGlobal(point))
        table_pos = self.Entiteis_Point.currentRow() if self.Entiteis_Point.currentRow()>=1 else 1
        if action == self.action_point_right_click_menu_copy: self.Coordinate_Copy(self.Entiteis_Point)
        elif action == self.action_point_right_click_menu_coverage: self.File.Points.coverageCoordinate(self.Entiteis_Point, self.Entiteis_Point.currentRow())
        elif action == self.action_point_right_click_menu_add: self.on_action_New_Point_triggered()
        elif action == self.action_point_right_click_menu_edit: self.on_actionEdit_Point_triggered(table_pos)
        elif action == self.action_point_right_click_menu_delete: self.on_actionDelete_Point_triggered(table_pos)
    def on_link_context_menu(self, point):
        action = self.popMenu_link.exec_(self.Entiteis_Link_Widget.mapToGlobal(point))
        if action == self.action_link_right_click_menu_add: self.on_action_New_Line_triggered()
        elif action == self.action_link_right_click_menu_edit: self.on_actionEdit_Linkage_triggered(self.Entiteis_Link.currentRow())
        elif action == self.action_link_right_click_menu_shaft: self.link2Shaft(self.Entiteis_Link.currentRow())
        elif action == self.action_link_right_click_menu_reversion:
            self.File.lineNodeReversion(self.Entiteis_Point, self.Entiteis_Link.currentRow())
            self.Resolve()
            self.workbookNoSave()
        elif action == self.action_link_right_click_menu_delete: self.on_actionDelete_Linkage_triggered(self.Entiteis_Link.currentRow())
    def on_chain_context_menu(self, point):
        action = self.popMenu_chain.exec_(self.Entiteis_Stay_Chain_Widget.mapToGlobal(point))
        if action == self.action_chain_right_click_menu_add: self.on_action_New_Stay_Chain_triggered()
        elif action == self.action_chain_right_click_menu_edit: self.on_actionEdit_Stay_Chain_triggered(self.Entiteis_Stay_Chain.currentRow())
        elif action == self.action_chain_right_click_menu_delete: self.on_actionDelete_Stay_Chain_triggered(self.Entiteis_Stay_Chain.currentRow())
    def on_shaft_context_menu(self, point):
        self.action_shaft_right_click_menu_move_up.setEnabled(self.Drive_Shaft.rowCount()>0 and self.Drive_Shaft.currentRow()>0)
        self.action_shaft_right_click_menu_move_down.setEnabled(self.Drive_Shaft.rowCount()>0 and self.Drive_Shaft.currentRow()<self.Drive_Shaft.rowCount()-1)
        action = self.popMenu_shaft.exec_(self.Drive_Shaft_Widget.mapToGlobal(point))
        if action == self.action_shaft_right_click_menu_add: self.on_action_Set_Drive_Shaft_triggered()
        elif action == self.action_shaft_right_click_menu_edit: self.on_action_Edit_Drive_Shaft_triggered(self.Drive_Shaft.currentRow())
        elif action == self.action_shaft_right_click_menu_move_up:
            self.move_up(self.Drive_Shaft, self.Drive_Shaft.currentRow(), "Shaft")
            self.File.Shafts.update(self.Drive_Shaft)
            self.File.Path.shaftChange(self.Drive_Shaft.currentRow(), self.Drive_Shaft.currentRow()-1)
            self.qpainterWindow.path_track(self.File.Path.data, self.File.Path.runList, self.File.Path.shaftList)
            self.Reload_Canvas()
        elif action == self.action_shaft_right_click_menu_move_down:
            self.move_down(self.Drive_Shaft, self.Drive_Shaft.currentRow(), "Shaft")
            self.File.Shafts.update(self.Drive_Shaft)
            self.File.Path.shaftChange(self.Drive_Shaft.currentRow(), self.Drive_Shaft.currentRow()+1)
            self.qpainterWindow.path_track(self.File.Path.data, self.File.Path.runList, self.File.Path.shaftList)
            self.Reload_Canvas()
        elif action == self.action_shaft_right_click_menu_delete: self.on_actionDelete_Drive_Shaft_triggered(self.Drive_Shaft.currentRow())
    def on_slider_context_menu(self, point):
        action = self.popMenu_slider.exec_(self.Slider_Widget.mapToGlobal(point))
        if action == self.action_slider_right_click_menu_add: self.on_action_Set_Slider_triggered()
        elif action == self.action_slider_right_click_menu_edit: self.on_action_Edit_Slider_triggered(self.Slider.currentRow())
        elif action == self.action_slider_right_click_menu_delete: self.on_actionDelete_Slider_triggered(self.Slider.currentRow())
    def on_rod_context_menu(self, point):
        action = self.popMenu_rod.exec_(self.Rod_Widget.mapToGlobal(point))
        if action == self.action_rod_right_click_menu_add: self.on_action_Set_Rod_triggered()
        elif action == self.action_rod_right_click_menu_edit: self.on_action_Edit_Rod_triggered(self.Rod.currentRow())
        elif action == self.action_rod_right_click_menu_delete: self.on_actionDelete_Piston_Spring_triggered(self.Rod.currentRow())
    def on_parameter_context_menu(self, point):
        self.action_parameter_right_click_menu_copy.setVisible(self.Parameter_list.currentColumn()==1)
        self.action_parameter_right_click_menu_move_up.setEnabled((not bool(self.Parameter_list.rowCount()<=1))and(self.Parameter_list.currentRow()>=1))
        self.action_parameter_right_click_menu_move_down.setEnabled((not bool(self.Parameter_list.rowCount()<=1))and(self.Parameter_list.currentRow()<=self.Parameter_list.rowCount()-2))
        self.action_parameter_right_click_menu_delete.setEnabled(self.Parameter_list.rowCount()>=1)
        action = self.popMenu_parameter.exec_(self.Parameter_Widget.mapToGlobal(point))
        if action == self.action_parameter_right_click_menu_copy: self.Coordinate_Copy(self.Parameter_list)
        elif action == self.action_parameter_right_click_menu_add: self.on_parameter_add()
        elif action == self.action_parameter_right_click_menu_move_up: self.on_parameter_del()
        elif action == self.action_parameter_right_click_menu_move_down:
            try:
                table.insertRow(row+2)
                for i in range(2):
                    name_set = QTableWidgetItem(table.item(row+2, i).text())
                    name_set.setFlags(Qt.ItemIsEnabled)
                    table.setItem(row+2, i, name_set)
                commit_set = QTableWidgetItem(table.item(row+2, 2).text())
                commit_set.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                table.removeRow(row)
                self.workbookNoSave()
            except: pass
        elif action == self.action_parameter_right_click_menu_delete:
            self.Parameter_list.removeRow(self.Parameter_list.currentRow())
            self.workbookNoSave()
            self.Mask_Change()
    
    #Table move up & down & copy
    def move_up(self, table, row, name):
        try:
            table.insertRow(row-1)
            for i in range(table.columnCount()): table.setItem(row-1, i, QTableWidgetItem(table.item(row+1, i).text()))
            table.removeRow(row+1)
            for j in range(table.rowCount()):
                name_set = QTableWidgetItem(name+str(j))
                name_set.setFlags(Qt.ItemIsEnabled)
                table.setItem(j, 0, name_set)
            self.workbookNoSave()
        except: pass
    def move_down(self, table, row, name):
        try:
            table.insertRow(row+2)
            for i in range(table.columnCount()): table.setItem(row+2, i, QTableWidgetItem(table.item(row, i).text()))
            table.removeRow(row)
            for j in range(table.rowCount()):
                name_set = QTableWidgetItem(name+str(j))
                name_set.setFlags(Qt.ItemIsEnabled)
                table.setItem(j, 0, QTableWidgetItem(name+str(j)))
            self.workbookNoSave()
        except: pass
    def Coordinate_Copy(self, table):
        clipboard = QApplication.clipboard()
        clipboard.setText(table.currentItem().text())
    def link2Shaft(self, row):
        cen = self.File.Lines.list[row]['start']
        ref = self.File.Lines.list[row]['end']
        self.on_action_Set_Drive_Shaft_triggered(cen, ref)
    
    @pyqtSlot(int, int)
    def on_Entiteis_Point_cellDoubleClicked(self, row, column):
        if row>0: self.on_actionEdit_Point_triggered(row)
    @pyqtSlot(int, int)
    def on_Entiteis_Link_cellDoubleClicked(self, row, column): self.on_actionEdit_Linkage_triggered(row)
    @pyqtSlot(int, int)
    def on_Entiteis_Stay_Chain_cellDoubleClicked(self, row, column): self.on_actionEdit_Stay_Chain_triggered(row)
    @pyqtSlot(int, int)
    def on_Drive_Shaft_cellDoubleClicked(self, row, column): self.on_action_Edit_Drive_Shaft_triggered(row)
    @pyqtSlot(int, int)
    def on_Slider_cellDoubleClicked(self, row, column): self.on_action_Edit_Slider_triggered(row)
    @pyqtSlot(int, int)
    def on_Rod_cellDoubleClicked(self, row, column): self.on_action_Edit_Rod_triggered(row)
    
    #Close Event
    def closeEvent(self, event):
        try:
            self.PathSolvingDlg.deleteLater()
            del self.PathSolvingDlg
        except: pass
        if self.File.form['changed']:
            reply = QMessageBox.question(self, 'Saving Message', "Are you sure to quit?\nAny Changes won't be saved.",
                (QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel), QMessageBox.Save)
            if reply == QMessageBox.Discard or reply == QMessageBox.Ok:
                print("Exit.")
                event.accept()
            elif reply == QMessageBox.Save:
                self.on_actionSave_triggered()
                if not self.File.form['changed']:
                    print("Exit.")
                    event.accept()
                else: event.ignore()
            else: event.ignore()
        else:
            print("Exit.")
            event.accept()
    
    #Scripts
    @pyqtSlot()
    def on_action_See_Python_Scripts_triggered(self):
        dlg = Script_Dialog(self.Script)
        dlg.show()
        dlg.exec()
    
    #Resolve
    def Resolve(self):
        table_point, table_line, table_chain, table_shaft, table_slider, table_rod = self.File.Obstacles_Exclusion()
        #Solve
        result = False
        result, DOF, script = slvsProcess(table_point, table_line, table_chain, table_shaft, table_slider, table_rod, self.Parameter_list, self.File.Shafts.current)
        self.Script = script
        if result:
            self.Solvefail = False
            self.File.Points.currentPos(self.Entiteis_Point, result)
            self.DOF = DOF
            self.DOF_view.setPlainText(str(self.DOF-6+self.Drive_Shaft.rowCount())+" ("+str(self.DOF-6)+")")
            self.DOFLable.setText("<html><head/><body><p><span style=\" color:#000000;\">DOF:</span></p></body></html>")
            self.Reload_Canvas()
        else:
            self.DOF_view.setPlainText("Failed.")
            self.DOFLable.setText("<html><head/><body><p><span style=\" font-weight:600; color:#ff0000;\">DOF:</span></p></body></html>")
            self.Solvefail = True
            if "-w" in sys.argv: print("Rebuild the cavanc failed.")
    #Reload Canvas
    def Reload_Canvas(self):
        self.qpainterWindow.update_figure(
            float(self.LineWidth.text()), float(self.PathWidth.text()),
            self.File.Points.list, self.File.Lines.list, self.File.Chains.list, self.File.Shafts.list, self.File.Sliders.list, self.File.Rods.list,
            self.Parameter_list, self.Entiteis_Point_Style, self.ZoomText.toPlainText(), self.Font_size.value(),
            self.actionDisplay_Dimensions.isChecked(), self.actionDisplay_Point_Mark.isChecked(),
            self.action_Black_Blackground.isChecked())
    
    #Workbook Change
    def workbookNoSave(self):
        self.File.form['changed'] = True
        self.setWindowTitle(self.windowTitle().replace("*", "")+"*")
        self.actionEnabled()
    #Action Enabled
    def actionEnabled(self):
        #Warning
        self.reqLine.setVisible(not self.Entiteis_Point.rowCount()>1)
        self.reqChain.setVisible(not self.Entiteis_Point.rowCount()>2)
        self.reqShaft.setVisible(not self.Entiteis_Point.rowCount()>1)
        self.reqSlider.setVisible(not self.Entiteis_Link.rowCount()>0)
        self.reqRod.setVisible(not self.Entiteis_Point.rowCount()>2)
        self.reqPath.setVisible(not self.Drive_Shaft.rowCount()>0)
        self.reqPathSolving.setVisible(not self.File.PathSolvingReqs.list)
        #Add
        self.action_New_Line.setEnabled(self.Entiteis_Point.rowCount()>1)
        self.action_New_Stay_Chain.setEnabled(self.Entiteis_Point.rowCount()>2)
        self.action_Set_Drive_Shaft.setEnabled(self.Entiteis_Point.rowCount()>1)
        self.action_Set_Slider.setEnabled(self.Entiteis_Link.rowCount()>0)
        self.action_Set_Rod.setEnabled(self.Entiteis_Point.rowCount()>2)
        self.action_link_right_click_menu_add.setEnabled(self.Entiteis_Point.rowCount()>1)
        self.action_chain_right_click_menu_add.setEnabled(self.Entiteis_Point.rowCount()>2)
        self.action_shaft_right_click_menu_add.setEnabled(self.Entiteis_Point.rowCount()>1)
        self.action_slider_right_click_menu_add.setEnabled(self.Entiteis_Link.rowCount()>0)
        self.action_rod_right_click_menu_add.setEnabled(self.Entiteis_Point.rowCount()>2)
        #Edit
        self.actionEdit_Point.setEnabled(self.Entiteis_Point.rowCount()>1)
        self.actionEdit_Linkage.setEnabled(self.Entiteis_Link.rowCount()>0)
        self.actionEdit_Stay_Chain.setEnabled(self.Entiteis_Stay_Chain.rowCount()>0)
        self.action_Edit_Drive_Shaft.setEnabled(self.Drive_Shaft.rowCount()>0)
        self.action_Edit_Slider.setEnabled(self.Slider.rowCount()>0)
        self.action_Edit_Rod.setEnabled(self.Rod.rowCount()>0)
        self.action_link_right_click_menu_edit.setEnabled(self.Entiteis_Link.rowCount()>0)
        self.action_chain_right_click_menu_edit.setEnabled(self.Entiteis_Stay_Chain.rowCount()>0)
        self.action_shaft_right_click_menu_edit.setEnabled(self.Drive_Shaft.rowCount()>0)
        self.action_slider_right_click_menu_edit.setEnabled(self.Slider.rowCount()>0)
        self.action_rod_right_click_menu_edit.setEnabled(self.Rod.rowCount()>=1)
        #Delete
        self.actionDelete_Point.setEnabled(self.Entiteis_Point.rowCount()>1)
        self.actionDelete_Linkage.setEnabled(self.Entiteis_Link.rowCount()>0)
        self.actionDelete_Stay_Chain.setEnabled(self.Entiteis_Stay_Chain.rowCount()>0)
        self.actionDelete_Drive_Shaft.setEnabled(self.Drive_Shaft.rowCount()>0)
        self.actionDelete_Slider.setEnabled(self.Slider.rowCount()>0)
        self.actionDelete_Piston_Spring.setEnabled(self.Rod.rowCount()>0)
        self.action_link_right_click_menu_delete.setEnabled(self.Entiteis_Link.rowCount()>0)
        self.action_chain_right_click_menu_delete.setEnabled(self.Entiteis_Stay_Chain.rowCount()>0)
        self.action_shaft_right_click_menu_delete.setEnabled(self.Drive_Shaft.rowCount()>0)
        self.action_slider_right_click_menu_delete.setEnabled(self.Slider.rowCount()>0)
        self.action_rod_right_click_menu_delete.setEnabled(self.Rod.rowCount()>=1)
        #Panel
        self.PathTrack.setEnabled(self.Drive_Shaft.rowCount()>0)
        self.Measurement.setEnabled(self.Entiteis_Point.rowCount()>1)
        self.AuxLine.setEnabled(self.Entiteis_Point.rowCount()>1)
        self.Drive.setEnabled(self.Drive_Shaft.rowCount()>0)
        self.Drive_rod.setEnabled(self.Rod.rowCount()>0)
        #Others
        self.action_point_right_click_menu_copy.setVisible(self.Entiteis_Point.currentColumn()==4)
        self.action_link_right_click_menu_shaft.setEnabled(self.Entiteis_Link.rowCount()>0)
        self.action_link_right_click_menu_reversion.setEnabled(self.Entiteis_Link.rowCount()>0)
    
    @pyqtSlot()
    def on_action_Full_Screen_triggered(self): print("Full Screen.")
    @pyqtSlot()
    def on_actionNormalmized_triggered(self): print("Normal Screen.")
    @pyqtSlot()
    def on_action_Get_Help_triggered(self):
        print("Open http://project.mde.tw/blog/slvs-library-functions.html")
        webbrowser.open("http://project.mde.tw/blog/slvs-library-functions.html")
    @pyqtSlot()
    def on_actionGit_hub_Site_triggered(self):
        print("Open https://github.com/40323230/python-solvespace")
        webbrowser.open("https://github.com/40323230/python-solvespace")
    @pyqtSlot()
    def on_actionGithub_Wiki_triggered(self):
        print("Open https://github.com/40323230/Pyslvs-manual/tree/master")
        webbrowser.open("https://github.com/40323230/Pyslvs-manual/tree/master")
    @pyqtSlot()
    def on_actionHow_to_use_triggered(self):
        dlg = Help_info_show()
        dlg.show()
        dlg.exec()
    @pyqtSlot()
    def on_action_About_Pyslvs_triggered(self):
        dlg = version_show()
        dlg.show()
        dlg.exec()
    @pyqtSlot()
    def on_action_About_Python_Solvspace_triggered(self):
        dlg = Info_show()
        dlg.show()
        dlg.exec()
    
    #TODO: Example
    @pyqtSlot()
    def on_action_New_Workbook_triggered(self): self.checkChange("[New Workbook]", new_workbook(), 'Generating New Workbook...')
    @pyqtSlot()
    def on_action_Load_Workbook_triggered(self): self.checkChange(say='Open file...')
    @pyqtSlot()
    def on_actionCrank_rocker_triggered(self): self.checkChange("[Example] Crank Rocker", example_crankRocker())
    @pyqtSlot()
    def on_actionDrag_link_triggered(self): self.checkChange("[Example] Drag-link", example_DragLink())
    @pyqtSlot()
    def on_actionDouble_rocker_triggered(self): self.checkChange("[Example] Double Rocker", example_doubleRocker())
    @pyqtSlot()
    def on_actionParallelogram_linkage_triggered(self): self.checkChange("[Example] Parallelogram Linkage", example_parallelogramLinkage())
    @pyqtSlot()
    def on_actionMutiple_Link_triggered(self): self.checkChange("[Example] Mutiple Link", example_mutipleLink())
    @pyqtSlot()
    def on_actionTwo_Mutiple_Link_triggered(self): self.checkChange("[Example] Two Pairs Mutiple Link", example_twoMutipleLink())
    @pyqtSlot()
    def on_actionReverse_Parsing_Rocker_triggered(self): self.checkChange("[Example] Reverse Parsing Rocker", example_reverseParsingRocker())
    #Workbook Functions
    def checkChange(self, name=False, data=[], say='Loading Example...'):
        if self.File.form['changed']:
            warning_reset = reset_show()
            warning_reset.show()
            if warning_reset.exec_():
                print(say)
                self.loadWorkbook(name, data)
        else:
            print(say)
            self.loadWorkbook(name, data)
    def loadWorkbook(self, fileName=False, data=[]):
        self.closePanel()
        self.File.reset(
            self.Entiteis_Point, self.Entiteis_Point_Style,
            self.Entiteis_Link, self.Entiteis_Stay_Chain,
            self.Drive_Shaft, self.Slider,
            self.Rod, self.Parameter_list)
        self.qpainterWindow.removePath()
        self.Resolve()
        print("Reset workbook.")
        if fileName==False: fileName, _ = QFileDialog.getOpenFileName(self, 'Open file...', self.Default_Environment_variables, 'CSV File(*.csv);;Text File(*.txt)')
        if QFileInfo(fileName).suffix()=="csv" or ("[Example]" in fileName) or ("[New Workbook]" in fileName):
            if data==[]:
                print("Get: "+fileName)
                with open(fileName, newline="") as stream:
                    reader = csv.reader(stream, delimiter=' ', quotechar='|')
                    for row in reader: data += ' '.join(row).split('\t,')
            if self.File.check(data):
                self.File.read(
                    fileName, data,
                    self.Entiteis_Point, self.Entiteis_Point_Style,
                    self.Entiteis_Link, self.Entiteis_Stay_Chain,
                    self.Drive_Shaft, self.Slider,
                    self.Rod, self.Parameter_list)
                for i in range(1, self.Entiteis_Point_Style.rowCount()): self.Entiteis_Point_Style.cellWidget(i, 3).currentIndexChanged.connect(self.Point_Style_set)
                self.File.form['changed'] = False
                self.setWindowTitle(_translate("MainWindow", "Pyslvs - "+fileName))
                self.Resolve()
                if (bool(self.File.Path.data) and bool(self.File.Path.runList)): self.Path_data_exist.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600; color:#ff0000;\">Path Data Exist</span></p></body></html>"))
                else: self.Path_data_exist.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600; color:#000000;\">No Path Data</span></p></body></html>"))
                self.Path_Clear.setEnabled(bool(self.File.Path.data) and bool(self.File.Path.runList))
                self.Path_coordinate.setEnabled(bool(self.File.Path.data) and bool(self.File.Path.runList))
                self.Path_data_show.setEnabled(bool(self.File.Path.data) and bool(self.File.Path.runList))
                self.qpainterWindow.path_track(self.File.Path.data, self.File.Path.runList, self.File.Path.shaftList)
                self.FileState = QUndoStack()
                print("Successful Load the workbook...")
                self.actionEnabled()
                if not("[New Workbook]" in fileName):
                    dlg = fileInfo_show()
                    dlg.rename(self.File.form['fileName'], self.File.form['author'], self.File.form['description'], self.File.form['lastTime'])
                    dlg.show()
                    if dlg.exec_(): pass
            else:
                print("Failed to load!")
    def closePanel(self):
        try:
            self.PathSolvingDlg.deleteLater()
            del self.PathSolvingDlg
        except: pass
        try:
            self.MeasurementWidget.deleteLater()
            del self.MeasurementWidget
            self.Measurement.setChecked(False)
        except: pass
        try:
            self.DriveWidget.deleteLater()
            del self.DriveWidget
            self.Drive.setChecked(False)
        except: pass
        try:
            self.qpainterWindow.AuxLine['show'] = False
            self.AuxLineWidget.deleteLater()
            del self.AuxLineWidget
            self.AuxLine.setChecked(False)
        except: pass
        self.reset_Auxline()
    
    @pyqtSlot()
    def on_action_Property_triggered(self):
        dlg = editFileInfo_show()
        self.File.updateTime()
        dlg.rename(self.File.form['fileName'], self.File.form['author'], self.File.form['description'], self.File.form['lastTime'])
        dlg.show()
        if dlg.exec_():
            self.File.form['author'] = dlg.authorName_input.text()
            self.File.form['description'] = dlg.descriptionText.toPlainText()
            self.workbookNoSave()
    
    @pyqtSlot()
    def on_actionSave_triggered(self):
        print("Saving this Workbook...")
        if "[New Workbook]" in self.File.form['fileName'] or "[Example]" in self.File.form['fileName']:
            fileName, sub = QFileDialog.getSaveFileName(self, 'Save file...', self.Default_Environment_variables, 'Spreadsheet(*.csv)')
        else:
            fileName = self.windowTitle().replace("Pyslvs - ", "").replace("*", "")
        if fileName:
            self.save(fileName)
    @pyqtSlot()
    def on_actionSave_as_triggered(self):
        print("Saving to another Workbook...")
        fileName, sub = QFileDialog.getSaveFileName(self, 'Save file...', self.Default_Environment_variables, 'Spreadsheet(*.csv)')
        if fileName:
            self.save(fileName)
    def save(self, fileName):
        fileName = fileName.replace(".csv", "")+".csv"
        with open(fileName, 'w', newline="") as stream:
            writer = csv.writer(stream)
            self.File.write(
                fileName, writer,
                self.Entiteis_Point, self.Entiteis_Point_Style,
                self.Entiteis_Link, self.Entiteis_Stay_Chain,
                self.Drive_Shaft, self.Slider,
                self.Rod, self.Parameter_list)
        print("Successful Save: "+fileName)
        self.File.form['changed'] = False
        self.setWindowTitle(_translate("MainWindow", "Pyslvs - "+fileName))
    
    @pyqtSlot()
    def on_action_Output_to_Solvespace_triggered(self):
        fileName, sub = QFileDialog.getSaveFileName(self, 'Save file...', self.Default_Environment_variables, 'Solvespace models(*.slvs)')
        if fileName:
            self.Slvs_Script = solvespace.slvs_formate(self.Entiteis_Point, self.Entiteis_Link, self.Entiteis_Stay_Chain,
                self.Drive_Shaft, self.Slider, self.Rod, self.Parameter_list)
            fileName = fileName.replace(".slvs", "")+".slvs"
            self.File.writeSlvsFile(fileName)
            print("Successful Save: "+fileName)
            self.setWindowTitle(_translate("MainWindow", "Pyslvs - "+fileName))
    
    @pyqtSlot()
    def on_action_Output_to_Script_triggered(self):
        print("Saving to script...")
        fileName, sub = QFileDialog.getSaveFileName(self, 'Save file...', self.Default_Environment_variables, 'Python Script(*.py)')
        if fileName:
            fileName = fileName.replace(".py", "")
            if sub == "Python Script(*.py)": fileName += ".py"
            with open(fileName, 'w', newline="") as f: f.write(self.Script)
            print("Saved to:"+str(fileName))
    
    @pyqtSlot()
    def on_action_Output_to_Picture_triggered(self):
        print("Saving to picture...")
        fileName, sub = QFileDialog.getSaveFileName(self, 'Save file...', self.Default_Environment_variables,
            "Portable Network Graphics (*.png);;Joint Photographic Experts Group (*.jpg);;Joint Photographic Experts Group (*.jpeg);;Bitmap Image file (*.bmp);;\
            Business Process Model (*.bpm);;Tagged Image File Format (*.tiff);;Tagged Image File Format (*.tif);;Windows Icon (*.ico);;Wireless Application Protocol Bitmap (*.wbmp);;\
            X BitMap (*.xbm);;X Pixmap (*.xpm)")
        if fileName:
            print("Formate: "+sub)
            sub = sub[sub.find('.')+1:sub.find(')')]
            fileName = fileName.replace('.'+sub, "")
            fileName += '.'+sub
            pixmap = self.qpainterWindow.grab()
            pixmap.save(fileName, format = sub)
            print("Saved to:"+str(fileName))
    
    @pyqtSlot()
    def on_actionOutput_to_DXF_triggered(self):
        print("Saving to DXF...")
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save file...', self.Default_Environment_variables, 'AutoCAD DXF (*.dxf)')
        if fileName:
            fileName = fileName.replace(".dxf", "")
            fileName += ".dxf"
            dxfCode(fileName, self.File.Points.list, self.File.Lines.list, self.File.Chains.list, self.File.Shafts.list, self.File.Sliders.list, self.File.Rods.list, self.Parameter_list)
    
    @pyqtSlot()
    def on_action_Output_to_S_QLite_Data_Base_triggered(self):
        print("Saving to Data Base...")
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save file...', self.Default_Environment_variables, 'Data Base(*.db)')
        if fileName:
            fileName = fileName.replace(".db", "")
            fileName += ".db"
            #TODO: SQLite
    
    #TODO: Table actions
    def on_parameter_add(self):
        self.File.Parameters.editTable(self.Parameter_list)
        self.workbookNoSave()
        self.Mask_Change()
    def on_parameter_del(self):
        self.File.Parameters.deleteTable(self.Parameter_list)
        self.Resolve()
        self.workbookNoSave()
        self.Mask_Change()
    @pyqtSlot()
    def on_Parameter_add_clicked(self): self.on_parameter_add()
    
    @pyqtSlot()
    def on_action_New_Point_triggered(self):
        table1 = self.Entiteis_Point
        table2 = self.Entiteis_Point_Style
        dlg = New_point(self.Mask, table1)
        dlg.show()
        if dlg.exec_():
            self.File.Points.editTable(table1,
                dlg.X_coordinate.text() if not dlg.X_coordinate.text()in["", "n", "-"] else dlg.X_coordinate.placeholderText(),
                dlg.Y_coordinate.text() if not dlg.Y_coordinate.text()in["", "n", "-"] else dlg.Y_coordinate.placeholderText(),
                bool(dlg.Fix_Point.checkState()))
            fix = "10" if dlg.Fix_Point.checkState() else "5"
            self.File.Points.styleAdd(table2, "Green", fix, "Green")
            self.Resolve()
            self.workbookNoSave()
    @pyqtSlot()
    def on_Point_add_button_clicked(self):
        table1 = self.Entiteis_Point
        table2 = self.Entiteis_Point_Style
        x = self.X_coordinate.text() if not self.X_coordinate.text()in["", "n", "-"] else self.X_coordinate.placeholderText()
        y = self.Y_coordinate.text() if not self.Y_coordinate.text()in["", "n", "-"] else self.Y_coordinate.placeholderText()
        self.File.Points.editTable(table1, x, y, False)
        self.File.Points.styleAdd(table2, "Green", "5", "Green")
        self.Resolve()
        self.workbookNoSave()
    
    @pyqtSlot()
    def on_actionEdit_Point_triggered(self, pos=1):
        table1 = self.Entiteis_Point
        dlg = edit_point_show(self.Mask, table1, pos)
        dlg.Another_point.connect(self.Change_Edit_Point)
        self.point_feedback.connect(dlg.change_feedback)
        self.Change_Edit_Point(pos)
        dlg.show()
        if dlg.exec_():
            table2 = self.Entiteis_Point_Style
            self.File.Points.editTable(table1,
                dlg.X_coordinate.text() if not dlg.X_coordinate.text()in["", "n", "-"] else dlg.X_coordinate.placeholderText(),
                dlg.Y_coordinate.text() if not dlg.Y_coordinate.text()in["", "n", "-"] else dlg.Y_coordinate.placeholderText(),
                bool(dlg.Fix_Point.checkState()), pos)
            self.File.Points.styleFix(table2, bool(dlg.Fix_Point.checkState()), pos)
            self.Resolve()
            self.workbookNoSave()
    point_feedback = pyqtSignal(float, float, bool)
    @pyqtSlot(int)
    def Change_Edit_Point(self, pos):
        table = self.Entiteis_Point
        x = float(table.item(pos, 1).text())
        y = float(table.item(pos, 2).text())
        fix = table.item(pos, 3).checkState()
        self.point_feedback.emit(x, y, fix)
    
    @pyqtSlot()
    def on_action_New_Line_triggered(self):
        table1 = self.Entiteis_Point
        table2 = self.Entiteis_Link
        dlg = New_link(self.Mask, table1, table2.rowCount())
        dlg.show()
        if dlg.exec_():
            a = dlg.Start_Point.currentText()
            b = dlg.End_Point.currentText()
            if self.File.Lines.repeatedCheck(table2, a, b): self.on_action_New_Line_triggered()
            elif a == b:
                dlg = same_show()
                dlg.show()
                if dlg.exec_(): self.on_action_New_Line_triggered()
            else:
                self.File.Lines.editTable(table2,
                    dlg.Start_Point.currentText(), dlg.End_Point.currentText(),
                    dlg.Length.text()if not dlg.Length.text()in["", "n"] else dlg.Length.placeholderText())
                self.Resolve()
                self.workbookNoSave()
    
    @pyqtSlot()
    def on_actionEdit_Linkage_triggered(self, pos=0):
        table1 = self.Entiteis_Point
        table2 = self.Entiteis_Link
        dlg = edit_link_show(self.Mask, table1, table2, pos)
        dlg.Another_line.connect(self.Change_Edit_Line)
        self.link_feedback.connect(dlg.change_feedback)
        self.Change_Edit_Line(pos)
        dlg.show()
        if dlg.exec_():
            a = dlg.Start_Point.currentText()
            b = dlg.End_Point.currentText()
            if a == b:
                dlg = same_show()
                dlg.show()
                if dlg.exec_(): self.on_actionEdit_Linkage_triggered()
            else:
                self.File.Lines.editTable(table2,
                    dlg.Start_Point.currentText(),  dlg.End_Point.currentText(),
                    dlg.Length.text() if not dlg.Length.text()in["", "n"] else dlg.Length.placeholderText(), pos)
                self.Resolve()
                self.workbookNoSave()
    link_feedback = pyqtSignal(int, int, float)
    @pyqtSlot(int)
    def Change_Edit_Line(self, pos):
        table = self.Entiteis_Link
        start = int(table.item(pos, 1).text().replace("Point", ""))
        end = int(table.item(pos, 2).text().replace("Point", ""))
        len = float(table.item(pos, 3).text())
        self.link_feedback.emit(start, end, len)
    
    @pyqtSlot()
    def on_action_New_Stay_Chain_triggered(self):
        table1 = self.Entiteis_Point
        table2 = self.Entiteis_Stay_Chain
        dlg = chain_show(self.Mask, table1, table2.rowCount())
        dlg.show()
        if dlg.exec_():
            p1 = dlg.Point1.currentText()
            p2 = dlg.Point2.currentText()
            p3 = dlg.Point3.currentText()
            if (p1 == p2) | (p2 == p3) | (p1 == p3):
                dlg = same_show()
                dlg.show()
                if dlg.exec_(): self.on_action_New_Stay_Chain_triggered()
            else:
                self.File.Chains.editTable(table2, p1, p2, p3,
                    dlg.p1_p2.text() if not dlg.p1_p2.text()in["", "n"] else dlg.p1_p2.placeholderText(),
                    dlg.p2_p3.text() if not dlg.p2_p3.text()in["", "n"] else dlg.p2_p3.placeholderText(),
                    dlg.p1_p3.text() if not dlg.p1_p3.text()in["", "n"] else dlg.p1_p3.placeholderText())
                self.Resolve()
                self.workbookNoSave()
    
    @pyqtSlot()
    def on_actionEdit_Stay_Chain_triggered(self, pos=0):
        table1 = self.Entiteis_Point
        table2 = self.Entiteis_Stay_Chain
        dlg = edit_stay_chain_show(self.Mask, table1, table2, pos)
        dlg.Another_chain.connect(self.Change_Edit_Chain)
        self.chain_feedback.connect(dlg.change_feedback)
        self.Change_Edit_Chain(pos)
        dlg.show()
        if dlg.exec_():
            p1 = dlg.Point1.currentText()
            p2 = dlg.Point2.currentText()
            p3 = dlg.Point3.currentText()
            if (p1 == p2) | (p2 == p3) | (p1 == p3):
                dlg = same_show()
                dlg.show()
                if dlg.exec_(): self.on_actionEdit_Stay_Chain_triggered()
            else:
                self.File.Chains.editTable(table2, p1, p2, p3,
                    dlg.p1_p2.text() if not dlg.p1_p2.text()in["", "n"] else dlg.p1_p2.placeholderText(),
                    dlg.p2_p3.text() if not dlg.p2_p3.text()in["", "n"] else dlg.p2_p3.placeholderText(),
                    dlg.p1_p3.text() if not dlg.p1_p3.text()in["", "n"] else dlg.p1_p3.placeholderText(), pos)
                self.Resolve()
                self.workbookNoSave()
    chain_feedback = pyqtSignal(int, int, int, float, float, float)
    @pyqtSlot(int)
    def Change_Edit_Chain(self, pos):
        table = self.Entiteis_Stay_Chain
        Point1 = int(table.item(pos, 1).text().replace("Point", ""))
        Point2 = int(table.item(pos, 2).text().replace("Point", ""))
        Point3 = int(table.item(pos, 3).text().replace("Point", ""))
        p1_p2 = float(table.item(pos, 4).text())
        p2_p3 = float(table.item(pos, 5).text())
        p1_p3 = float(table.item(pos, 6).text())
        self.chain_feedback.emit(Point1, Point2, Point3, p1_p2, p2_p3, p1_p3)
    
    @pyqtSlot()
    def on_action_Set_Drive_Shaft_triggered(self, cen=0, ref=0):
        table1 = self.Entiteis_Point
        table2 = self.Drive_Shaft
        dlg = shaft_show(table1, table2.rowCount(), cen, ref)
        dlg.show()
        if dlg.exec_():
            a = dlg.Shaft_Center.currentText()
            b = dlg.References.currentText()
            c = dlg.Start_Angle.text()
            d = dlg.End_Angle.text()
            e = dlg.Demo_angle.text() if dlg.Demo_angle_enable.checkState() else dlg.Start_Angle.text()
            if a==b or c==d:
                dlg = same_show()
                dlg.show()
                if dlg.exec_(): self.on_action_Set_Drive_Shaft_triggered()
            else:
                self.File.Shafts.editTable(table2, a, b, c, d, e, bool(dlg.isParallelogram.checkState()))
                self.Resolve()
                self.workbookNoSave()
    
    @pyqtSlot()
    def on_action_Edit_Drive_Shaft_triggered(self, pos=0):
        table1 = self.Entiteis_Point
        table2 = self.Drive_Shaft
        dlg = edit_shaft_show(table1, table2, pos)
        dlg.Another_shaft.connect(self.Change_Edit_Shaft)
        self.shaft_feedback.connect(dlg.change_feedback)
        self.Change_Edit_Shaft(pos)
        dlg.show()
        if dlg.exec_():
            a = dlg.Shaft_Center.currentText()
            b = dlg.References.currentText()
            c = dlg.Start_Angle.text()
            d = dlg.End_Angle.text()
            if a==b or c==d:
                dlg = same_show()
                dlg.show()
                if dlg.exec_(): self.on_action_Set_Drive_Shaft_triggered()
            else:
                self.File.Shafts.editTable(table2, a, b, c, d, table2.item(dlg.Shaft.currentIndex(), 5), bool(dlg.isParallelogram.checkState()), pos)
                self.Resolve()
                self.workbookNoSave()
    shaft_feedback = pyqtSignal(int, int, float, float)
    @pyqtSlot(int)
    def Change_Edit_Shaft(self, pos):
        table = self.Drive_Shaft
        center = int(table.item(pos, 1).text().replace("Point", ""))
        references = int(table.item(pos, 2).text().replace("Point", ""))
        start = float(table.item(pos, 3).text())
        end = float(table.item(pos, 4).text())
        self.shaft_feedback.emit(center, references, start, end)
    
    @pyqtSlot()
    def on_action_Set_Slider_triggered(self):
        table1 = self.Entiteis_Point
        table2 = self.Entiteis_Link
        table3 = self.Slider
        dlg = slider_show(table1, table2, table3.rowCount())
        dlg.show()
        if dlg.exec_():
            a = dlg.Slider_Center.currentText()
            b = dlg.References.currentText()
            c = dlg.References.currentIndex()
            if (table2.item(c, 1).text()==a) or (table2.item(c, 2).text()==a):
                dlg = restriction_conflict_show()
                dlg.show()
                if dlg.exec_(): self.on_action_Set_Slider_triggered()
            else:
                self.File.Sliders.editTable(table3, a, b)
                self.Resolve()
                self.workbookNoSave()
    
    @pyqtSlot()
    def on_action_Edit_Slider_triggered(self, pos=0):
        table1 = self.Entiteis_Point
        table2 = self.Entiteis_Link
        table3 = self.Slider
        dlg = edit_slider_show(table1, table2, table3, pos)
        dlg.Another_slider.connect(self.Change_Edit_Slider)
        self.slider_feedback.connect(dlg.change_feedback)
        self.Change_Edit_Slider(pos)
        dlg.show()
        if dlg.exec_():
            a = dlg.Slider_Center.currentText()
            b = dlg.References.currentText()
            c = dlg.References.currentIndex()
            if (table2.item(c, 1).text()==a) or (table2.item(c, 2).text()==a):
                dlg = restriction_conflict_show()
                dlg.show()
                if dlg.exec_(): self.on_action_Edit_Slider_triggered()
            else:
                self.File.Sliders.editTable(table3, a, b, pos)
                self.Resolve()
                self.workbookNoSave()
    slider_feedback = pyqtSignal(int, int)
    @pyqtSlot(int)
    def Change_Edit_Slider(self, pos):
        table = self.Slider
        point = int(table.item(pos, 1).text().replace("Ponit", ""))
        line = int(table.item(pos, 2).text().replace("Line", ""))
        self.slider_feedback.emit(point, line)
    
    @pyqtSlot()
    def on_action_Set_Rod_triggered(self):
        table1 = self.Entiteis_Point
        table2 = self.Rod
        dlg = rod_show(table1, table2.rowCount())
        dlg.show()
        if dlg.exec_():
            a = dlg.Start.currentText()
            b = dlg.End.currentText()
            c = str(float(dlg.Position.text()))
            if a == b:
                dlg = same_show()
                dlg.show()
                if dlg.exec_(): self.on_action_Set_Drive_Shaft_triggered()
            else:
                self.File.Rods.editTable(table2, a, b, c)
                self.Resolve()
                self.workbookNoSave()
    
    @pyqtSlot()
    def on_action_Edit_Rod_triggered(self, pos=0):
        table1 = self.Entiteis_Point
        table2 = self.Rod
        dlg = edit_rod_show(table1, table2, pos)
        dlg.Another_rod.connect(self.Change_Edit_Rod)
        self.rod_feedback.connect(dlg.change_feedback)
        self.Change_Edit_Rod(pos)
        dlg.show()
        if dlg.exec_():
            a = dlg.Start.currentText()
            b = dlg.End.currentText()
            c = str(min(float(dlg.len1.text()), float(dlg.len2.text())))
            d = str(max(float(dlg.len1.text()), float(dlg.len2.text())))
            if a == b:
                dlg = same_show()
                dlg.show()
                if dlg.exec_(): self.on_action_Set_Drive_Shaft_triggered()
            else:
                self.File.Rods.editTable(table2, a, b, c, d, pos)
                self.Resolve()
                self.workbookNoSave()
    rod_feedback = pyqtSignal(int, int, int, float)
    @pyqtSlot(int)
    def Change_Edit_Rod(self, pos):
        table = self.Rod
        center = int(table.item(pos, 1).text().replace("Point", ""))
        start = int(table.item(pos, 2).text().replace("Point", ""))
        end = int(table.item(pos, 3).text().replace("Point", ""))
        position = float(table.item(pos, 4).text())
        self.rod_feedback.emit(center, start, end, position)
    
    @pyqtSlot()
    def on_actionDelete_Point_triggered(self, pos = 1):
        dlg = deleteDlg(QIcon(QPixmap(":/icons/delete.png")), QIcon(QPixmap(":/icons/point.png")), self.Entiteis_Point, pos)
        dlg.show()
        if dlg.exec_():
            self.File.Points.deleteTable(self.Entiteis_Point,
                self.Entiteis_Point_Style, self.Entiteis_Link,
                self.Entiteis_Stay_Chain, self.Drive_Shaft,
                self.Slider, self.Rod, dlg)
            self.Resolve()
            self.workbookNoSave()
    
    @pyqtSlot()
    def on_actionDelete_Linkage_triggered(self, pos = 0):
        dlg = deleteDlg(QIcon(QPixmap(":/icons/deleteline.png")), QIcon(QPixmap(":/icons/line.png")), self.Entiteis_Link, pos)
        dlg.show()
        if dlg.exec_():
            self.File.Lines.deleteTable(self.Entiteis_Link, self.Slider, dlg)
            self.Resolve()
            self.workbookNoSave()
    
    @pyqtSlot()
    def on_actionDelete_Stay_Chain_triggered(self, pos = 0):
        table = self.Entiteis_Stay_Chain
        dlg = deleteDlg(QIcon(QPixmap(":/icons/deletechain.png")), QIcon(QPixmap(":/icons/equal.png")), table, pos)
        dlg.show()
        if dlg.exec_():
            for i in range(table.rowCount()):
                if (dlg.Entity.currentText() == table.item(i, 0).text()):
                    table.removeRow(i)
                    for j in range(i, table.rowCount()): table.setItem(j, 0, QTableWidgetItem(name+str(j)))
                    break
            self.Resolve()
            self.workbookNoSave()
    
    @pyqtSlot()
    def on_actionDelete_Drive_Shaft_triggered(self, pos = 0):
        table = self.Drive_Shaft
        dlg = deleteDlg(QIcon(QPixmap(":/icons/deleteshaft.png")), QIcon(QPixmap(":/icons/circle.png")), table, pos)
        dlg.show()
        if dlg.exec_():
            for i in range(table.rowCount()):
                if (dlg.Entity.currentText() == table.item(i, 0).text()):
                    table.removeRow(i)
                    for j in range(i, table.rowCount()): table.setItem(j, 0, QTableWidgetItem(name+str(j)))
                    break
            self.Resolve()
            self.workbookNoSave()
    
    @pyqtSlot()
    def on_actionDelete_Slider_triggered(self, pos = 0):
        table = self.Slider
        dlg = deleteDlg(QIcon(QPixmap(":/icons/deleteslider.png")), QIcon(QPixmap(":/icons/pointonx.png")), table, pos)
        dlg.show()
        if dlg.exec_():
            for i in range(table.rowCount()):
                if (dlg.Entity.currentText() == table.item(i, 0).text()):
                    table.removeRow(i)
                    for j in range(i, table.rowCount()): table.setItem(j, 0, QTableWidgetItem(name+str(j)))
                    break
            self.Resolve()
            self.workbookNoSave()
    
    @pyqtSlot()
    def on_actionDelete_Piston_Spring_triggered(self, pos = 0):
        table = self.Rod
        dlg = deleteDlg(QIcon(QPixmap(":/icons/deleterod.png")), QIcon(QPixmap(":/icons/spring.png")), table, pos)
        dlg.show()
        if dlg.exec_():
            for i in range(table.rowCount()):
                if (dlg.Entity.currentText() == table.item(i, 0).text()):
                    table.removeRow(i)
                    for j in range(i, table.rowCount()): table.setItem(j, 0, QTableWidgetItem(name+str(j)))
                    break
            self.Resolve()
            self.workbookNoSave()
    
    @pyqtSlot()
    def on_ResetCanvas_clicked(self):
        self.ZoomBar.setValue(self.Default_canvas_view)
        self.qpainterWindow.points['origin']['x'] = self.qpainterWindow.width()/2
        self.qpainterWindow.points['origin']['y'] = self.qpainterWindow.height()/2
        self.Reload_Canvas()
    @pyqtSlot()
    def on_FitW_clicked(self):
        self.Fit2H()
        self.Fit2W()
    def Fit2W(self):
        for i in range(10):
            max_pt = max(self.qpainterWindow.points['x'])
            min_pt = min(self.qpainterWindow.points['x'])
            self.qpainterWindow.points['origin']['x'] = (self.qpainterWindow.width()-(max_pt+min_pt))/2
            self.ZoomBar.setValue(self.ZoomBar.value()*self.qpainterWindow.width()/(max_pt+min_pt+100))
            self.Reload_Canvas()
    @pyqtSlot()
    def on_FitH_clicked(self):
        self.Fit2W()
        self.Fit2H()
    def Fit2H(self):
        for i in range(10):
            max_pt = max(self.qpainterWindow.points['y'])
            min_pt = min(self.qpainterWindow.points['y'])
            self.qpainterWindow.points['origin']['y'] = (self.qpainterWindow.height()-(max_pt+min_pt))/2
            self.ZoomBar.setValue(self.ZoomBar.value()*self.qpainterWindow.height()/(max_pt-min_pt+100))
            self.Reload_Canvas()
    @pyqtSlot(int)
    def on_ZoomBar_valueChanged(self, value):
        self.ZoomText.setPlainText(str(value)+"%")
        self.Reload_Canvas()
    #Wheel Event
    def wheelEvent(self, event):
        if self.mapFromGlobal(QCursor.pos()).x()>=470:
            if event.angleDelta().y()>0: self.ZoomBar.setValue(self.ZoomBar.value()+10)
            if event.angleDelta().y()<0: self.ZoomBar.setValue(self.ZoomBar.value()-10)
    
    @pyqtSlot()
    def on_actionReload_Drawing_triggered(self): self.Resolve()
    @pyqtSlot(QTableWidgetItem)
    def on_Entiteis_Point_Style_itemChanged(self, item):
        self.Reload_Canvas()
        self.workbookNoSave()
    @pyqtSlot(int)
    def on_LineWidth_valueChanged(self, p0): self.Reload_Canvas()
    @pyqtSlot(int)
    def on_Font_size_valueChanged(self, p0): self.Reload_Canvas()
    @pyqtSlot(int)
    def on_PathWidth_valueChanged(self, p0): self.Reload_Canvas()
    @pyqtSlot(bool)
    def on_actionDisplay_Dimensions_toggled(self, p0): self.Reload_Canvas()
    @pyqtSlot(bool)
    def on_actionDisplay_Point_Mark_toggled(self, p0): self.Reload_Canvas()
    @pyqtSlot(bool)
    def on_action_Black_Blackground_toggled(self, p0): self.Reload_Canvas()
    @pyqtSlot(int)
    def Point_Style_set(self, index):
        self.Reload_Canvas()
        self.workbookNoSave()
    @pyqtSlot()
    def on_Path_data_show_clicked(self):
        self.qpainterWindow.points['Path']['show'] = self.Path_data_show.checkState()
        self.Reload_Canvas()
    @pyqtSlot()
    def on_Path_points_show_clicked(self):
        self.qpainterWindow.points['slvsPath']['show'] = self.Path_points_show.checkState()
        self.Reload_Canvas()
    
    @pyqtSlot()
    def on_PathTrack_clicked(self):
        table1 = self.Entiteis_Point
        dlg = Path_Track_show()
        self.actionDisplay_Point_Mark.setChecked(True)
        for i in range(table1.rowCount()):
            if not table1.item(i, 3).checkState(): dlg.Point_list.addItem(table1.item(i, 0).text())
        dlg.loadData(self.File.Points.list, self.File.Lines.list, self.File.Chains.list, self.File.Shafts.list, self.File.Sliders.list, self.File.Rods.list, self.Parameter_list)
        dlg.show()
        if dlg.exec_():
            self.File.Path.runList = list()
            for i in range(dlg.Run_list.count()): self.File.Path.runList += [dlg.Run_list.item(i).text()]
            self.File.Path.shaftList = dlg.work.ShaftList
            self.File.Path.data = dlg.Path_data
            self.Path_data_exist.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600; color:#ff0000;\">Path Data Exist</span></p></body></html>"))
            self.Path_Clear.setEnabled(True)
            self.Path_coordinate.setEnabled(True)
            self.Path_data_show.setEnabled(True)
            self.qpainterWindow.path_track(self.File.Path.data, self.File.Path.runList, self.File.Path.shaftList)
            self.workbookNoSave()
    @pyqtSlot()
    def on_Path_Clear_clicked(self):
        self.qpainterWindow.removePath()
        self.Reload_Canvas()
        self.Path_data_exist.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600; color:#000000;\">No Path Data</span></p></body></html>"))
        self.Path_Clear.setEnabled(False)
        self.Path_coordinate.setEnabled(False)
        self.Path_data_show.setEnabled(False)
    @pyqtSlot()
    def on_Path_coordinate_clicked(self):
        dlg = path_point_data_show()
        self.File.Path.setup(dlg.path_data, self.File.Path.data, self.File.Path.runList)
        dlg.show()
        dlg.exec()
    
    #TODO: Path Solving
    @pyqtSlot(bool)
    def on_PathSolving_toggled(self, p0):
        if not hasattr(self, 'PathSolvingDlg'):
            self.PathSolvingDlg = Path_Solving_show(self.Mask, self.File.PathSolvingReqs.list, self.File.PathSolvingReqs.result, self.width())
            self.PathSolving.toggled.connect(self.PathSolvingDlg.reject)
            self.PathSolvingDlg.addPathPoint.connect(self.PathSolving_add)
            self.PathSolvingDlg.deletePathPoint.connect(self.PathSolving_delete)
            self.PathSolvingDlg.rejected.connect(self.PathSolving_return)
            self.PathSolvingDlg.Generate.clicked.connect(self.PathSolving_send)
            self.PathSolvingDlg.moveupPathPoint.connect(self.PathSolving_moveup)
            self.PathSolvingDlg.movedownPathPoint.connect(self.PathSolving_movedown)
            self.PathSolvingDlg.mergeMechanism.connect(self.PathSolving_merge)
            self.PathSolvingDlg.Listbox.deleteResult.connect(self.PathSolving_deleteResult)
            self.PathSolvingDlg.Listbox.mergeResult.connect(self.PathSolving_mergeResult)
            self.PathSolvingStart.connect(self.PathSolvingDlg.start)
            self.PathSolvingDlg.show()
            self.PointTab.addTab(self.PathSolvingDlg.Listbox, QIcon(QPixmap(":/icons/bezier.png")), "Thinking list")
            self.PathSolvingDlg.Listbox.show()
            self.PointTab.setCurrentIndex(self.PointTab.count()-1)
            if self.PathSolvingDlg.exec_(): pass
        else:
            try:
                self.PathSolvingDlg.deleteLater()
                del self.PathSolvingDlg
            except: pass
    @pyqtSlot()
    def PathSolving_return(self): self.PathSolving.setChecked(False)
    def PathSolving_add_rightClick(self, x, y):
        self.PathSolvingDlg.addPath(x, y)
        self.PathSolving_add(x, y)
    @pyqtSlot(float, float)
    def PathSolving_add(self, x=0, y=0):
        self.File.PathSolvingReqs.add(x, y)
        self.qpainterWindow.path_solving(self.File.PathSolvingReqs.list, self.File.PathSolvingReqs.result)
        self.workbookNoSave()
        self.actionEnabled()
    @pyqtSlot(int)
    def PathSolving_delete(self, row):
        self.File.PathSolvingReqs.remove(row)
        self.qpainterWindow.path_solving(self.File.PathSolvingReqs.list, self.File.PathSolvingReqs.result)
        self.workbookNoSave()
        self.actionEnabled()
    @pyqtSlot(int)
    def PathSolving_moveup(self, row):
        self.File.PathSolvingReqs.moveUP(row)
        self.qpainterWindow.path_solving(self.File.PathSolvingReqs.list, self.File.PathSolvingReqs.result)
    @pyqtSlot(int)
    def PathSolving_movedown(self, row):
        self.File.PathSolvingReqs.moveDown(row)
        self.qpainterWindow.path_solving(self.File.PathSolvingReqs.list, self.File.PathSolvingReqs.result)
    PathSolvingStart = pyqtSignal(list)
    @pyqtSlot()
    def PathSolving_send(self): self.PathSolvingStart.emit(self.File.PathSolvingReqs.list)
    @pyqtSlot(list)
    def PathSolving_merge(self, mechanism_data): self.File.PathSolvingReqs.resultMerge(mechanism_data)
    @pyqtSlot(int)
    def PathSolving_deleteResult(self, row): self.File.PathSolvingReqs.removeResult(row)
    @pyqtSlot(int)
    def PathSolving_mergeResult(self, row):
        self.File.Generate_Merge(row, slvsProcess(generateResult=self.File.PathSolvingReqs.result[row]),
            self.Entiteis_Point, self.Entiteis_Point_Style, self.Entiteis_Link, self.Entiteis_Stay_Chain, self.Drive_Shaft)
        self.Resolve()
        self.workbookNoSave()
    
    @pyqtSlot()
    def on_Drive_clicked(self):
        if not hasattr(self, 'DriveWidget'):
            self.DriveWidget = Drive_show()
            for i in range(self.Drive_Shaft.rowCount()): self.DriveWidget.Shaft.insertItem(i, QIcon(QPixmap(":/icons/circle.png")), self.Drive_Shaft.item(i, 0).text())
            self.PointTab.addTab(self.DriveWidget, QIcon(QPixmap(":/icons/same-orientation.png")), 'Drive Shaft')
            self.PointTab.setCurrentIndex(self.PointTab.count()-1)
            self.DriveWidget.Degree_change.connect(self.Change_demo_angle)
            self.DriveWidget.Shaft_change.connect(self.Shaft_limit)
            self.Shaft_limit(0)
        else:
            try:
                self.File.Shafts.current = 0
                self.DriveWidget.deleteLater()
                del self.DriveWidget
            except: pass
    @pyqtSlot(int)
    def Shaft_limit(self, pos):
        self.DriveWidget.Degree.setMinimum(int(self.File.Shafts.list[self.File.Shafts.current]['start'])*100)
        self.DriveWidget.Degree.setMaximum(int(self.File.Shafts.list[self.File.Shafts.current]['end'])*100)
        try: self.DriveWidget.Degree.setValue(int(self.File.Shafts.list[self.File.Shafts.current]['demo'])*100)
        except: self.DriveWidget.Degree.setValue(int((self.DriveWidget.Degree.maximum()+self.DriveWidget.Degree.minimum())/2))
        self.DriveWidget.Degree_text.setValue(float(self.DriveWidget.Degree.value()/100))
    @pyqtSlot(int, float)
    def Change_demo_angle(self, index, angle):
        self.File.Shafts.setDemo(self.Drive_Shaft, index, angle)
        self.File.Shafts.current = index
        self.Resolve()
        self.workbookNoSave()
    
    @pyqtSlot()
    def on_Measurement_clicked(self):
        if not hasattr(self, 'MeasurementWidget'):
            table = self.Entiteis_Point
            self.MeasurementWidget = Measurement_show(table)
            self.PointTab.addTab(self.MeasurementWidget, QIcon(QPixmap(":/icons/ref.png")), 'Measurement')
            self.PointTab.setCurrentIndex(self.PointTab.count()-1)
            self.qpainterWindow.change_event.connect(self.MeasurementWidget.Detection_do)
            self.actionDisplay_Dimensions.setChecked(True)
            self.actionDisplay_Point_Mark.setChecked(True)
            self.qpainterWindow.mouse_track.connect(self.MeasurementWidget.show_mouse_track)
            self.MeasurementWidget.point_change.connect(self.distance_solving)
            self.distance_changed.connect(self.MeasurementWidget.change_distance)
            self.MeasurementWidget.Mouse.setPlainText("Detecting")
        else:
            try:
                self.MeasurementWidget.deleteLater()
                del self.MeasurementWidget
            except: pass
    distance_changed = pyqtSignal(float)
    @pyqtSlot(int, int)
    def distance_solving(self, start, end):
        start = self.Entiteis_Point.item(start, 4).text().replace("(", "").replace(")", "")
        end = self.Entiteis_Point.item(end, 4).text().replace("(", "").replace(")", "")
        x = float(start.split(", ")[0])-float(end.split(", ")[0])
        y = float(start.split(", ")[1])-float(end.split(", ")[1])
        self.distance_changed.emit(round(math.sqrt(x**2+y**2), 9))
    
    @pyqtSlot()
    def on_AuxLine_clicked(self):
        if not hasattr(self, 'AuxLineWidget'):
            self.qpainterWindow.AuxLine['show'] = True
            self.qpainterWindow.AuxLine['horizontal'] = True
            self.qpainterWindow.AuxLine['vertical'] = True
            table = self.Entiteis_Point
            self.AuxLineWidget = AuxLine_show(table, self.qpainterWindow.AuxLine['pt'], self.qpainterWindow.AuxLine['color'], self.qpainterWindow.AuxLine['limit_color'])
            self.AuxLineWidget.Point_change.connect(self.draw_Auxline)
            self.PointTab.addTab(self.AuxLineWidget, QIcon(QPixmap(":/icons/auxline.png")), 'Auxiliary Line')
            self.PointTab.setCurrentIndex(self.PointTab.count()-1)
        else:
            self.qpainterWindow.AuxLine['show'] = False
            try:
                self.AuxLineWidget.deleteLater()
                del self.AuxLineWidget
            except: pass
        self.Reload_Canvas()
    @pyqtSlot(int, int, int, bool, bool, bool, bool, bool)
    def draw_Auxline(self, pt, color, color_l, axe_H, axe_V, max_l, min_l, pt_change):
        self.qpainterWindow.AuxLine['pt'] = pt
        self.qpainterWindow.AuxLine['color'] = color
        self.qpainterWindow.AuxLine['limit_color'] = color_l
        if pt_change:
            self.qpainterWindow.Reset_Aux_limit()
            self.Reload_Canvas()
        self.qpainterWindow.AuxLine['horizontal'] = axe_H
        self.qpainterWindow.AuxLine['vertical'] = axe_V
        self.qpainterWindow.AuxLine['isMax'] = max_l
        self.qpainterWindow.AuxLine['isMin'] = min_l
        self.Reload_Canvas()
    def reset_Auxline(self):
        self.qpainterWindow.AuxLine['Max']['x'] = 0
        self.qpainterWindow.AuxLine['Max']['y'] = 0
        self.qpainterWindow.AuxLine['Min']['x'] = 0
        self.qpainterWindow.AuxLine['Min']['y'] = 0
        self.qpainterWindow.AuxLine['pt'] = 0
        self.qpainterWindow.AuxLine['color'] = 6
        self.qpainterWindow.AuxLine['limit_color'] = 8
    
    def Mask_Change(self):
        row_Count = str(self.Parameter_list.rowCount()-1)
        param = '(('
        for i in range(len(row_Count)): param += '[1-'+row_Count[i]+']' if i==0 and not len(row_Count)<=1 else '[0-'+row_Count[i]+']'
        param += ')|'
        param_100 = '[0-9]{0,'+str(len(row_Count)-2)+'}' if len(row_Count)>2 else ''
        param_20 = '([1-'+str(int(row_Count[0])-1)+']'+param_100+')?' if self.Parameter_list.rowCount()>19 else ''
        if len(row_Count)>1: param += param_20+'[0-9]'
        param += ')'
        param_use = '^[n]'+param+'$|' if self.Parameter_list.rowCount()>=1 else ''
        mask = '('+param_use+'^[-]?([1-9][0-9]{0,'+str(self.Default_Bits-2)+'})?[0-9][.][0-9]{1,'+str(self.Default_Bits)+'}$)'
        self.Mask = QRegExpValidator(QRegExp(mask))
        self.X_coordinate.setValidator(self.Mask)
        self.Y_coordinate.setValidator(self.Mask)
    
    @pyqtSlot(int, int, int, int)
    def on_Parameter_list_currentCellChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        try:
            self.Parameter_num.setPlainText("n"+str(currentRow))
            self.Parameter_digital.setPlaceholderText(str(self.Parameter_list.item(currentRow, 1).text()))
            self.Parameter_digital.clear()
        except:
            self.Parameter_num.setPlainText("N/A")
            self.Parameter_digital.setPlaceholderText("0.0")
            self.Parameter_digital.clear()
        self.Parameter_num.setEnabled(self.Parameter_list.rowCount()>0 and currentRow>-1)
        self.Parameter_digital.setEnabled(self.Parameter_list.rowCount()>0 and currentRow>-1)
        self.Parameter_lable.setEnabled(self.Parameter_list.rowCount()>0 and currentRow>-1)
        self.Parameter_update.setEnabled(self.Parameter_list.rowCount()>0 and currentRow>-1)
    @pyqtSlot()
    def on_Parameter_update_clicked(self):
        try: self.Parameter_list.setItem(self.Parameter_list.currentRow(), 1, QTableWidgetItem(self.Parameter_digital.text() if self.Parameter_digital.text() else Parameter_digital.placeholderText()))
        except: pass
    @pyqtSlot(int, int, int, int)
    def on_Entiteis_Point_currentCellChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        self.X_coordinate.setPlaceholderText(self.Entiteis_Point.item(currentRow, 1).text())
        self.Y_coordinate.setPlaceholderText(self.Entiteis_Point.item(currentRow, 2).text())
    @pyqtSlot(int, int)
    def on_Parameter_list_cellChanged(self, row, column):
        if column in [1, 2]: self.Parameter_list.item(row, column).setToolTip(self.Parameter_list.item(row, column).text())
    
    @pyqtSlot()
    def on_action_Prefenece_triggered(self):
        dlg = options_show()
        color_list = self.qpainterWindow.re_Color
        for i in range(len(color_list)): dlg.LinkingLinesColor.insertItem(i, color_list[i])
        for i in range(len(color_list)): dlg.StayChainColor.insertItem(i, color_list[i])
        for i in range(len(color_list)): dlg.AuxiliaryLineColor.insertItem(i, color_list[i])
        for i in range(len(color_list)): dlg.AuxiliaryLimitLineColor.insertItem(i, color_list[i])
        for i in range(len(color_list)): dlg.TextColor.insertItem(i, color_list[i])
        dlg.show()
        if dlg.exec_(): pass
    
    @pyqtSlot()
    def on_actionUndo_triggered(self):
        self.FileState.undo()
        print("Undo.")
    @pyqtSlot()
    def on_actionRedo_triggered(self):
        self.FileState.redo()
        print("Redo.")
