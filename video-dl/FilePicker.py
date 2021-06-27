import os
import tkinter
from tkinter import filedialog as tkFileDialog
from typing import List, Literal, Tuple, Union


def GetFilePathByGUI(
    file_type=(["すべてのファイル", "*"],),
    initial_dir=os.path.dirname(__file__),
) -> Union[Tuple[str, ...], Literal['']]:
    # ファイル選択ダイアログの表示
    root = tkinter.Tk()
    root.withdraw()
    # Make it almost invisible - no decorations, 0 size, top left corner.
    root.overrideredirect(True)
    root.geometry("0x0+0+0")
    root.deiconify()
    root.lift()
    root.focus_force()

    iDir = os.path.abspath(initial_dir)
    file_path_list = tkFileDialog.askopenfilenames(filetypes=file_type, initialdir=iDir)
    root.destroy()
    return file_path_list


def GetDirPathByGUI(
    initial_dir=os.path.dirname(__file__),
) -> Tuple[str, List[str]]:
    # ファイル選択ダイアログの表示
    root = tkinter.Tk()
    root.withdraw()
    # Make it almost invisible - no decorations, 0 size, top left corner.
    root.overrideredirect(True)
    root.geometry("0x0+0+0")
    root.deiconify()
    root.lift()
    root.focus_force()

    iDir = os.path.abspath(initial_dir)
    dir_path: str = ""
    file_path_list: Union[str, List[str]] = ""

    dir_path = tkFileDialog.askdirectory(initialdir=iDir)
    file_path_list = []
    for current_dir, _, file_name_list in os.walk(dir_path):
        for file_name in file_name_list:
            file_path_list.append(os.path.join(current_dir, file_name))
    root.destroy()
    return dir_path, file_path_list
