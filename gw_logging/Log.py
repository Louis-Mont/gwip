from tkinter import Text, END


class Log:
    def __init__(self, txt_log):
        """
        :type txt_log: Text
        """
        self.i_log = txt_log
        self.draw_logs = True

    def add(self, lg):
        """
        :type lg: str
        """
        if self.draw_logs:
            self.i_log.configure(state="normal")
            self.i_log.insert(END, f"\n{lg}")
            self.i_log.configure(state="disabled")
