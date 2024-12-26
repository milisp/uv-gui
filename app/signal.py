import subprocess

from PyQt5.QtCore import QThread, pyqtSignal


class CommandThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, command, cwd, is_shell=False):
        super().__init__()
        self.command = command
        self.cwd = cwd
        self.is_shell = is_shell

    def run(self):
        # 使用 subprocess.Popen 运行外部命令
        process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self.cwd,
            shell=self.is_shell,
            text=True,
        )
        # 实时读取输出并发送信号
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                self.output_signal.emit(output.strip())
        self.finished_signal.emit()
