import os
import re
import sys
import platform

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QDialog,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QComboBox,
)

from app import CommandThread, read_python_version, read_dependencies_from_pyproject
from app.dialog_form import CustomDialog


class UVGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UV GUI - Python Package Manager")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        uv_self_layout = QHBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        self.install_uv_button = QPushButton("Install uv")
        self.update_uv_button = QPushButton("Upgrade uv")
        self.install_uv_button.clicked.connect(self.install_uv)
        self.update_uv_button.clicked.connect(self.update_uv)
        uv_self_layout.addWidget(self.install_uv_button)
        uv_self_layout.addWidget(self.update_uv_button)

        # Project management
        self.project_label = QLabel("Current Project: None")
        self.project_label.setStyleSheet("font-weight: bold;")
        self.project_button = QPushButton("Select Project")
        self.project_button.clicked.connect(self.select_project)
        self.init_button = QPushButton("Init Project")
        self.init_button.clicked.connect(self.init_project)
        self.python_version_box = QComboBox(self)
        self.python_version_box.addItems([f"3.{x}" for x in range(7, 14)])
        self.python_version_box.setFixedWidth(70)

        # 添加 GitHub 按钮
        self.github_button = QPushButton(self)
        self.github_button.setIcon(QIcon("github-icon.png"))  # GitHub 图标路径

        # 设置按钮位置到右上角
        self.github_button.setGeometry(self.width() - 40, 60, 60, 60)
        self.github_button.clicked.connect(self.open_github)

        # 窗口大小调整事件，用于更新按钮位置
        self.github_button.raise_()

        # Dependency management
        self.dependency_list = QListWidget()
        self.refresh_button = QPushButton("Refresh Dependencies")
        self.refresh_button.clicked.connect(self.refresh_dependencies)
        self.add_button = QPushButton("Add Dependency")
        self.add_button.clicked.connect(self.add_dependency)
        self.remove_button = QPushButton("Remove Dependency")
        self.remove_button.clicked.connect(self.remove_dependency)

        # Command output
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)

        # Add widgets to layouts
        top_layout.addWidget(self.project_label)
        top_layout.addWidget(self.project_button)
        version_label = QLabel("python version:")
        version_label.setFixedWidth(100)
        top_layout.addWidget(version_label)
        top_layout.addWidget(self.python_version_box)
        top_layout.addWidget(self.init_button)
        bottom_layout.addWidget(self.refresh_button)
        bottom_layout.addWidget(self.add_button)
        bottom_layout.addWidget(self.remove_button)

        main_layout.addLayout(uv_self_layout)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(QLabel("Dependencies:"))
        main_layout.addWidget(self.dependency_list)
        main_layout.addLayout(bottom_layout)
        main_layout.addWidget(QLabel("Command Output:"))
        main_layout.addWidget(self.command_output)

        central_widget.setLayout(main_layout)

    def install_uv(self):
        system = platform.system()
        if system in ["Darwin", "Linux"]:
            try:
                self.run_command(
                    "curl -LsSf https://astral.sh/uv/install.sh | sh",
                    is_shell=True,
                    refresh=False,
                )
            except Exception as _:
                self.run_command(
                    "wget -qO- https://astral.sh/uv/install.sh | sh",
                    is_shell=True,
                    refresh=False,
                )
        elif system == "Window":
            self.run_command(
                'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"',
                is_shell=True,
                refresh=False,
            )
        else:
            self.command_output.append("unsupport system")

    def update_uv(self):
        self.run_command(["uv", "self", "update"], refresh=False)

    def select_project(self):
        project_dir = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if project_dir:
            self.project_label.setText(f"Current Project: {project_dir}")
            self.project_dir = project_dir
            self.python_version_box.setCurrentText(read_python_version(project_dir))
            os.environ["VIRTUAL_ENV"] = self.project_dir + "/.venv"
            self.refresh_dependencies()

    def init_project(self):
        if not self.check_project_selected():
            return
        python_version = self.python_version_box.currentText()
        self.run_command(
            ["uv", "init", ".", f"--python={python_version}"], cwd=self.project_dir
        )

    def refresh_dependencies(self):
        if not hasattr(self, "project_dir"):
            QMessageBox.warning(self, "Warning", "Please select a project first!")
            return
        try:
            depends = read_dependencies_from_pyproject(self.project_dir)
            self.dependency_list.clear()
            self.dependency_list.addItems(depends)
            self.command_output.append("refreshing dependencies: ok")
        except Exception as e:
            self.command_output.append(f"Error refreshing dependencies: {e}")

    def check_project_selected(self):
        """Check if a project is selected and show a warning if not."""
        if not hasattr(self, "project_dir"):
            QMessageBox.warning(self, "Warning", "Please select a project first!")
            return False
        return True

    def add_dependency(self):
        if not self.check_project_selected():
            return
        dialog = CustomDialog()
        if dialog.exec_() == QDialog.Accepted:
            dependency, is_upgrade, is_verbose, index_url = dialog.get_values()
            if dependency:
                try:
                    dependencies = dependency.split()
                    command = (
                        ["uv", "add"]
                        + (["-v"] if is_verbose else [])
                        + (["-U"] if is_upgrade else [])
                        + dependencies
                    )
                    if index_url.strip():
                        command += ["-i", index_url]
                    self.run_command(command, cwd=self.project_dir)
                except Exception as e:
                    self.command_output.append(f"Error adding dependency: {e}")

    def remove_dependency(self):
        if not self.check_project_selected():
            return
        selected_item = self.dependency_list.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self, "Warning", "Please select a dependency to remove!"
            )
            return
        dependency = re.sub("<|>|=", " ", selected_item.text()).split()[0]
        try:
            self.run_command(["uv", "remove", dependency], cwd=self.project_dir)
        except Exception as e:
            self.command_output.append(f"Error removing dependency: {e}")

    def run_command(self, command, cwd=None, is_shell=False, refresh=True):
        """Run a shell command and return its output."""
        self.command_output.append("run command start")
        self.command_thread = CommandThread(command, cwd, is_shell)
        self.command_thread.output_signal.connect(self.append_output)
        if refresh:
            self.command_thread.finished_signal.connect(self.refresh_dependencies)
        self.command_thread.start()

    def append_output(self, text):
        # 将输出追加到 QTextEdit
        self.command_output.append(text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.github_button.move(self.width() - 60, 0)  # 动态调整位置

    def open_github(self):
        QDesktopServices.openUrl(QUrl("https://github.com/milisp/uv-gui"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UVGui()
    window.show()
    sys.exit(app.exec_())
