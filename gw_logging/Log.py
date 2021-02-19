from tkinter import Text, END


class Log:
    def __init__(self, txt_log):
        """
        :type txt_log: Text
        """
        self.i_log = txt_log

    def add(self, lg):
        """
        :type lg: str
        """
        self.i_log.configure(state="normal")
        self.i_log.insert(END, f"\n{lg}")
        self.i_log.configure(state="disabled")
