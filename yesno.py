from tkinter import Tk, RAISED, Label, Button, DISABLED, NORMAL


def _yesno_close(frame: Tk, popup: Tk, action=None):
    """
    The actions taken when the window is closed
    :param frame: The frame the window inherits from
    :param popup: The window to terminate
    :param action: What the window is doing when closing when not equal to None
    """
    # frame.state = NORMAL
    popup.destroy()
    if action is not None:
        action()


def yesno(frame: Tk, title: str, text: str, yes_action=None, no_action=None):
    """
    Generates a yes or no window popup using Tk().
    Closing the app will not execute any functions.
    :param frame: The frame the window inherits from
    :param title: Title of the window
    :param text: Text written inside it
    :param yes_action: What to do when yes is clicked
    :param no_action: What to do when no is clicked
    """
    popup = Tk()
    popup.title(f"{title}")
    text = Label(popup, text=f"{text}", relief=RAISED)
    text.pack(side="top", fill="x", pady=10)
    btn_yes = Button(popup, text="yes", command=lambda: _yesno_close(frame, popup, yes_action))
    btn_no = Button(popup, text="no", command=lambda: _yesno_close(frame, popup, no_action))
    btn_yes.pack()
    btn_no.pack()

    # frame.state = DISABLED
    popup.protocol("WM_DELETE_WINDOW", lambda: _yesno_close(frame, popup))
    popup.mainloop()
