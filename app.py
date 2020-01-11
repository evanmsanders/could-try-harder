# Could Try Harder - Simple report comment builder for teachers.
# Copyright (C) 2020 Evan M. Sanders
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import re
import could_try_harder
import config
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, QComboBox, QFileDialog, QInputDialog, QMessageBox

class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("{} {}".format(config.APP_NAME, config.APP_VERSION))
        self.setMinimumWidth(600)
        self.setStyleSheet(config.STYLESHEET)

        # Widgets
        self.import_label = QLabel('Import a CSV class list to add a new class of reports.')
        self.import_button = QPushButton('Import CSV...')
        self.saved_label = QLabel('You have the following saved classes:')
        self.saved_listwidget = QListWidget(self)
        self.edit_comment_bank_button = QPushButton('Edit Comment Bank')
        self.edit_reports_button = QPushButton('Edit Reports')
        self.export_reports_button = QPushButton('Export Reports')
        self.delete_class_button = QPushButton('Delete')

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.import_label)
        self.layout.addWidget(self.import_button)
        self.layout.addWidget(self.saved_label)
        self.layout.addWidget(self.saved_listwidget)
        self.layout.addWidget(self.edit_comment_bank_button)
        self.layout.addWidget(self.edit_reports_button)
        self.layout.addWidget(self.export_reports_button)
        self.layout.addWidget(self.delete_class_button)

        # Initial run of listbox update
        self.update_saved_list()

        # Slot connections
        self.import_button.clicked.connect(self.import_csv)
        self.saved_listwidget.itemSelectionChanged.connect(self.do_update_selection)
        self.edit_comment_bank_button.clicked.connect(self.edit_comment_bank)
        self.edit_reports_button.clicked.connect(self.edit_reports)
        self.export_reports_button.clicked.connect(self.export_reports)
        self.delete_class_button.clicked.connect(self.delete_class)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

    @Slot()
    def import_csv(self):
        # TODO proper validation for input will mean building this dialog out
        # properly using QLineEdit
        subject_name, ok = QInputDialog().getText(self, "Subject Name", "Enter a name or code for the subject:")
        if subject_name and ok:
            filename, filt = QFileDialog.getOpenFileName(self, "Import CSV", os.path.expanduser("~"), "Comma Separated (*.csv)")
            if could_try_harder.import_class_list(filename, subject_name):
                self.update_saved_list()
            else:
                # TODO better error handling here
                print("Import Failed")
                return

    def update_saved_list(self):
        self.saved_listwidget.clear()
        self.saved_listwidget.addItems(could_try_harder.get_saved_list())
        self.do_update_selection()

    @Slot()
    def do_update_selection(self):
        if self.saved_listwidget.selectedItems():
            state = True
        else:
            state = False
        self.edit_comment_bank_button.setEnabled(state)
        self.edit_reports_button.setEnabled(state)
        self.export_reports_button.setEnabled(state)
        self.delete_class_button.setEnabled(state)

    @Slot()
    def edit_comment_bank(self):
        subject_name = self.saved_listwidget.currentItem().text()
        self.edit_comment_bank_window = EditCommentBankWindow(subject_name)
        self.edit_comment_bank_window.show()

    @Slot()
    def edit_reports(self):
        subject_name = self.saved_listwidget.currentItem().text()
        self.edit_reports_window = EditReportsWindow(subject_name)
        self.edit_reports_window.show()

    @Slot()
    def export_reports(self):
        subject_name = self.saved_listwidget.currentItem().text()
        filename, filt = QFileDialog.getSaveFileName(self, "Export", os.path.expanduser("~"), "Text Files (*.txt)")
        if filename:
            if not could_try_harder.export(subject_name, filename):
                # TODO better error handling here
                print("Export failed.")
                return

    @Slot()
    def delete_class(self):
        confirm_msg = QMessageBox(self)
        confirm_msg.setWindowTitle("Confirm")
        confirm_msg.setText("This will delete the class, comment bankd and reports.")
        confirm_msg.setInformativeText("Continue?")
        confirm_msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        confirm_msg.setDefaultButton(QMessageBox.Yes)
        confirm = confirm_msg.exec()
        if confirm == QMessageBox.Yes:
            subject_name = self.saved_listwidget.currentItem().text()
            if not could_try_harder.delete(subject_name):
                # TODO better error handling here
                print("Delete failed.")
            self.update_saved_list()

class EditCommentBankWindow(QMainWindow):

    def __init__(self, subject_name):
        QMainWindow.__init__(self)
        self.setWindowTitle("Edit Comment Bank: {} - {} {}".format(subject_name, config.APP_NAME, config.APP_VERSION))
        self.setMinimumWidth(1200)
        self.setStyleSheet(config.STYLESHEET)

        self.subject = could_try_harder.load(subject_name)
        self.saved_list = could_try_harder.get_saved_list()

        # Widgets
        self.intro_comment_label = QLabel("Introductory Comment:")
        self.intro_comment_label.setProperty("styleClass", "heading")
        self.intro_comment_textedit = QTextEdit()
        self.comment_bank_label = QLabel("Comment Bank")
        self.comment_bank_label.setProperty("styleClass", "heading")
        self.comment_bank_listwidget = QListWidget()
        self.placeholder_instructions_label = QLabel(config.PLACEHOLDER_INSTRUCTIONS)
        self.add_comment_label = QLabel("Add Comment:")
        self.add_comment_entry = QLineEdit()
        self.add_comment_button = QPushButton("Add")
        self.update_comment_label = QLabel("Update Comment:")
        self.update_comment_entry = QLineEdit()
        self.update_comment_button = QPushButton("Update")
        self.delete_comment_button = QPushButton("Delete Comment")
        self.import_comments_combo = QComboBox()
        self.import_comments_button = QPushButton("Import...")
        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")

        # Layout
        self.layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.intro_comment_layout = QVBoxLayout()
        self.intro_comment_layout.addWidget(self.intro_comment_label)
        self.intro_comment_layout.addWidget(self.intro_comment_textedit)
        self.top_layout.addLayout(self.intro_comment_layout)
        self.top_layout.addWidget(self.placeholder_instructions_label)
        self.layout.addLayout(self.top_layout)
        self.middle_layout = QVBoxLayout()
        self.middle_layout.addWidget(self.comment_bank_label)
        self.middle_layout.addWidget(self.comment_bank_listwidget)
        self.comment_actions_layout = QHBoxLayout()
        self.comment_actions_layout.addWidget(self.delete_comment_button, 0, Qt.AlignLeft)
        self.comment_actions_layout.addWidget(self.import_comments_combo, 1, Qt.AlignRight)
        self.comment_actions_layout.addWidget(self.import_comments_button, 0, Qt.AlignRight)
        self.middle_layout.addLayout(self.comment_actions_layout)
        self.update_comment_layout = QGridLayout()
        self.update_comment_layout.addWidget(self.update_comment_label, 0, 0)
        self.update_comment_layout.addWidget(self.update_comment_entry, 0, 1)
        self.update_comment_layout.addWidget(self.update_comment_button, 0, 2)
        self.update_comment_layout.addWidget(self.add_comment_label, 1, 0)
        self.update_comment_layout.addWidget(self.add_comment_entry, 1, 1)
        self.update_comment_layout.addWidget(self.add_comment_button, 1, 2)
        self.middle_layout.addLayout(self.update_comment_layout)
        self.layout.addLayout(self.middle_layout)
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.cancel_button, 0, Qt.AlignLeft)
        self.bottom_layout.addWidget(self.save_button, 0, Qt.AlignRight)
        self.layout.addLayout(self.bottom_layout)

        # Slot connections
        self.comment_bank_listwidget.itemSelectionChanged.connect(self.do_update_comment_bank_selection)
        self.import_comments_button.clicked.connect(self.do_import_comments)
        self.update_comment_button.clicked.connect(self.do_update_comment)
        self.update_comment_entry.returnPressed.connect(self.do_update_comment)
        self.add_comment_button.clicked.connect(self.do_add_comment)
        self.add_comment_entry.returnPressed.connect(self.do_add_comment)
        self.delete_comment_button.clicked.connect(self.do_delete_comment)
        self.cancel_button.clicked.connect(self.do_cancel)
        self.save_button.clicked.connect(self.do_save)

        # Initial UI update
        self.update_ui()

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def update_ui(self):
        self.update_import_comments_list()
        self.update_intro_comment()
        self.update_comment_bank()

    def update_import_comments_list(self):
        self.import_comments_combo.clear()
        self.import_comments_combo.insertItems(0, self.saved_list)

    def update_intro_comment(self):
        self.intro_comment_textedit.clear()
        self.intro_comment_textedit.insertPlainText(self.subject['intro_comment'])

    def update_comment_bank(self):
        self.comment_bank_listwidget.clear()
        self.comment_bank_listwidget.addItems(self.subject['comment_bank'])
        self.do_update_comment_bank_selection()

    @Slot()
    def do_import_comments(self):
        # TODO confirm dialog first
        confirm_msg = QMessageBox(self)
        confirm_msg.setWindowTitle("Confirm")
        confirm_msg.setText("This will override current comments.")
        confirm_msg.setInformativeText("Do you want to continue?")
        confirm_msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        confirm_msg.setDefaultButton(QMessageBox.Yes)
        confirm = confirm_msg.exec()
        if confirm == QMessageBox.Yes:
            if self.import_comments_combo.count() > 0:
                new_subject = could_try_harder.load(self.import_comments_combo.currentText())
                if new_subject:
                    self.subject['intro_comment'] = new_subject['intro_comment']
                    self.subject['comment_bank'] = new_subject['comment_bank']
                    self.update_ui()
                else:
                    # TODO better error handling here
                    print('Tried to import empty subject.')
                    return
        return

    @Slot()
    def do_update_comment_bank_selection(self):
        if self.comment_bank_listwidget.selectedItems():
            state = True
        else:
            state = False
        self.delete_comment_button.setEnabled(state)
        self.update_comment_button.setEnabled(state)
        # Update the text in the update comment line edit
        self.update_comment_entry.clear()
        if self.comment_bank_listwidget.currentItem():
            self.update_comment_entry.insert(self.comment_bank_listwidget.currentItem().text())

    @Slot()
    def do_update_comment(self):
        if self.update_comment_entry.text():
            self.comment_bank_listwidget.currentItem().setText(could_try_harder.do_style(self.update_comment_entry.text().strip()))
            self.do_update_comment_bank_selection()

    @Slot()
    def do_add_comment(self):
        if self.add_comment_entry.text():
            self.comment_bank_listwidget.addItem(could_try_harder.do_style(self.add_comment_entry.text().strip()))
            self.add_comment_entry.clear()
            self.do_update_comment_bank_selection()

    @Slot()
    def do_delete_comment(self):
        self.comment_bank_listwidget.takeItem(self.comment_bank_listwidget.currentRow())
        self.do_update_comment_bank_selection()

    @Slot()
    def do_cancel(self):
        self.close()

    @Slot()
    def do_save(self):
        self.subject['intro_comment'] = could_try_harder.do_style(self.intro_comment_textedit.toPlainText().strip())
        self.subject['comment_bank'] = []
        for i in range(self.comment_bank_listwidget.count()):
            self.subject['comment_bank'].append(self.comment_bank_listwidget.item(i).text())
        if could_try_harder.save(self.subject):
            self.close()
        else:
            # TODO better error handling here
            print("Save failed.")

class EditReportsWindow(QMainWindow):

    def __init__(self, subject_name):
        QMainWindow.__init__(self)
        self.setWindowTitle("Edit Reports: {} - {} {}".format(subject_name, config.APP_NAME, config.APP_VERSION))
        self.setMinimumWidth(1200)
        self.setStyleSheet(config.STYLESHEET)

        self.subject = could_try_harder.load(subject_name)
        self.student = {}

        # Used to keep track of current student
        self.s_index = 0
        self.load_student()

        # Widgets
        self.previous_student_button = QPushButton("Previous Student")
        self.student_name_label = QLabel()
        self.student_name_label.setProperty("styleClass", "title")
        self.next_student_button = QPushButton("Next Student")
        self.intro_comment_label = QLabel("Introductory Comment")
        self.intro_comment_label.setProperty("styleClass", "heading")
        self.intro_comment = QLabel()
        self.comment_bank_label = QLabel("Comment Bank")
        self.comment_bank_label.setProperty("styleClass", "heading")
        self.comment_bank_listwidget = QListWidget()
        self.add_comment_button = QPushButton("Add Selected Comment")
        self.comment_label = QLabel("Student Comment")
        self.comment_label.setProperty("styleClass", "heading")
        self.comment_textedit = QTextEdit()
        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")

        # Layout
        self.layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.previous_student_button, 0, Qt.AlignLeft)
        self.top_layout.addWidget(self.student_name_label, 1, Qt.AlignCenter)
        self.top_layout.addWidget(self.next_student_button, 0, Qt.AlignRight)
        self.layout.addLayout(self.top_layout)
        self.middle_layout = QVBoxLayout()
        self.middle_layout.addWidget(self.intro_comment_label)
        self.middle_layout.addWidget(self.intro_comment)
        self.middle_layout.addWidget(self.comment_bank_label)
        self.middle_layout.addWidget(self.comment_bank_listwidget)
        self.middle_layout.addWidget(self.add_comment_button)
        self.middle_layout.addWidget(self.comment_label)
        self.middle_layout.addWidget(self.comment_textedit)
        self.layout.addLayout(self.middle_layout)
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.cancel_button, 0, Qt.AlignLeft)
        self.bottom_layout.addWidget(self.save_button, 0, Qt.AlignRight)
        self.layout.addLayout(self.bottom_layout)

        # Slots
        self.previous_student_button.clicked.connect(self.do_previous_student)
        self.next_student_button.clicked.connect(self.do_next_student)
        self.comment_bank_listwidget.itemSelectionChanged.connect(self.do_update_comment_bank_selection)
        self.add_comment_button.clicked.connect(self.do_add_comment)
        self.cancel_button.clicked.connect(self.do_cancel)
        self.save_button.clicked.connect(self.do_save)

        # Initial UI Update
        self.update_ui()

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def update_ui(self):
        # Page title
        self.student_name_label.setText(self.student['first_name'] + " " + self.student['last_name'])

        # Enable/Disabled Next/Previous Buttons
        if self.s_index <= 0:
            self.previous_student_button.setEnabled(False)
        else:
            self.previous_student_button.setEnabled(True)
        if self.s_index < len(self.subject['students']) - 1:
            self.next_student_button.setEnabled(True)
        else:
            self.next_student_button.setEnabled(False)

        self.do_update_comment_bank_selection()

        # Intro comment
        self.intro_comment.setText(could_try_harder.do_placeholders(self.subject['intro_comment'], self.student['first_name'], self.student['pronouns']))

        # Comment Bank
        self.comment_bank_listwidget.clear()
        for comment in self.subject['comment_bank']:
            self.comment_bank_listwidget.addItem(could_try_harder.do_placeholders(comment, self.student['first_name'], self.student['pronouns']))

        # Student Comment
        self.comment_textedit.clear()
        self.comment_textedit.insertPlainText(self.student['comment'])

    def load_student(self):
        """
        Loads student into the self.student dict temporarily
        """
        self.student = self.subject['students'][self.s_index]

    def save_comment(self):
        """
        Saves student comment into the self.subject dict temporarily. Not saved into the save file.
        """
        comment = self.comment_textedit.toPlainText()
        comment = could_try_harder.do_placeholders(comment, self.student['first_name'], self.student['pronouns'])
        comment = could_try_harder.do_style(comment)

        self.subject['students'][self.s_index]['comment'] = comment

    @Slot()
    def do_next_student(self):
        if self.s_index < len(self.subject['students']) - 1:
            self.save_comment()
            self.s_index += 1
            self.load_student()
            self.update_ui()

    @Slot()
    def do_previous_student(self):
        if self.s_index > 0:
            self.save_comment()
            self.s_index -= 1
            self.load_student()
            self.update_ui()

    @Slot()
    def do_update_comment_bank_selection(self):
        # Enable/Disable the Add Comment button
        if self.comment_bank_listwidget.selectedItems():
            self.add_comment_button.setEnabled(True)
        else:
            self.add_comment_button.setEnabled(False)

    @Slot()
    def do_add_comment(self):
        # Add a space if we need to.
        if not self.comment_textedit.textCursor().atStart() and not self.comment_textedit.textCursor().block().text().endswith(" "):
            self.comment_textedit.insertPlainText(" ")
        self.comment_textedit.insertPlainText(self.comment_bank_listwidget.currentItem().text())

    @Slot()
    def do_save(self):
        self.save_comment()
        if could_try_harder.save(self.subject):
            self.close()
        else:
            # TODO better error handling here
            print("Save failed")

    @Slot()
    def do_cancel(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
