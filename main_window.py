from cProfile import label
import configparser
from distutils.command.config import config
import tkinter
from tkinter import RAISED, Label, StringVar, filedialog

#------------------#
# global variables #
#------------------#

#------------------#
# button functions #
#------------------#

# function for button close window
def close_window():
    main.destroy()

# function for browsing directory path of bfmeii and bfmeiirotwk
def open_directory(button):
    directory_path = filedialog.askdirectory()
    # write directory path into launcher_options.ini
    if button.cget("text") == "browse_path_bfmeii":
        config['GAMEPATH']['BFMEII'] = directory_path 
        bfmeII_path_label.set(directory_path)
    elif button.cget("text") == "browse_path_bfmeiirotwk":
        config['GAMEPATH']['BFMEIIROTWK'] = directory_path
        bfmeIIrotwk_path_label.set(directory_path)
    with open('launcher_options.ini', 'w') as configfile:
        config.write(configfile)

# function for reading launcher_options.ini
def read_launcher_options(section, subsection):
    config = configparser.ConfigParser()
    config.read('launcher_options.ini')
    return config[section][subsection]

#--------------------------#
# main window with buttons #
#--------------------------#

# main application window
main = tkinter.Tk()
main.geometry("500x200")

# button browse path for BFME II
browse_path_bfmeii = tkinter.Button(main, text = "browse_path_bfmeii")
browse_path_bfmeii.config(command = lambda button = browse_path_bfmeii : open_directory(button))
browse_path_bfmeii.pack()

# label variables for gamepath text
bfmeII_path_label = tkinter.StringVar()
bfmeIIrotwk_path_label = tkinter.StringVar()

# label for bfmeii current path
label_bfmeii = Label(main, textvariable = bfmeII_path_label, relief = RAISED)
# read current bfmeII path from launcher_options.ini
config = configparser.ConfigParser()
config.read('launcher_options.ini')
bfmeII_path_label.set(config['GAMEPATH']['BFMEII'])
label_bfmeii.pack()

# button browse path for BFME II ROTWK
browse_path_bfmeiirotwk = tkinter.Button(main, text = "browse_path_bfmeiirotwk")
browse_path_bfmeiirotwk.config(command = lambda button = browse_path_bfmeiirotwk : open_directory(button))
browse_path_bfmeiirotwk.pack()

# label for bfmeiirotwk current path
label_bfmeiirotwk = Label(main, textvariable = bfmeIIrotwk_path_label, relief = RAISED)
# read current bfmeiirotwk path from launcher_options.ini
config = configparser.ConfigParser()
config.read('launcher_options.ini')
bfmeIIrotwk_path_label.set(config['GAMEPATH']['BFMEIIROTWK'])
label_bfmeiirotwk.pack()

# button close window
button_close = tkinter.Button(main, text = "Close", command = close_window)
button_close.pack()

# loop for main application window
main.mainloop()