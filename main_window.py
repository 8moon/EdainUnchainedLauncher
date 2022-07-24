from cProfile import label
import configparser
from distutils.command.config import config
import tkinter
from tkinter import RAISED, Label, StringVar, filedialog

#------------------#
# button functions #
#------------------#

# function for button close window
def close_window():
    main.destroy()

# function for browsing directory path
def open_directory(button):
    directory_path = filedialog.askdirectory()
    # write directory path into launcher_options.ini
    config = configparser.ConfigParser()
    config.read('launcher_options.ini')
    #config['GAMEPATH']['BFMEII'] = directory_path
    if button.cget("text") == "browse_path_1":
        config['GAMEPATH']['BFMEII'] = directory_path 
    elif button.cget("text") == "browse_path_2":
        config['GAMEPATH']['BFMEIIROTWK'] = directory_path
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

# button browse path for BFME II
browse_path_1 = tkinter.Button(main, text = "browse_path_1")
browse_path_1.config(command = lambda button = browse_path_1 : open_directory(button))
browse_path_1.pack()

# label for browse_path_1
bfmeII_path = StringVar()
label = Label(main, textvariable = bfmeII_path, relief = RAISED)
# read current bfmeII path from launcher_options.ini
config = configparser.ConfigParser()
config.read('launcher_options.ini')
bfmeII_path.set(config['GAMEPATH']['BFMEII'])
label.pack()

# button browse path for BFME II ROTWK
browse_path_2 = tkinter.Button(main, text = "browse_path_2")
browse_path_2.config(command = lambda button = browse_path_2 : open_directory(button))
browse_path_2.pack()

# button close window
button_close = tkinter.Button(main, text = "Close", command = close_window)
button_close.pack()

# loop for main application window
main.mainloop()