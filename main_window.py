import tkinter
from tkinter import filedialog

#------------------#
# button functions #
#------------------#

# function for button close window
def close_window():
    main.destroy()

# function for browsing directory path
def open_directory():
    directory_path = filedialog.askdirectory()
    print(directory_path)

#--------------------------#
# main window with buttons #
#--------------------------#

# main application window
main = tkinter.Tk()

# button browse path for BFME II
browse_path_1 = tkinter.Button(main, text = "Browse", command=open_directory)
browse_path_1.pack()

# button browse path for BFME II ROTWK

# button close window
button_close = tkinter.Button(main, text = "Close", command = close_window)
button_close.pack()

# loop for main application window
main.mainloop()