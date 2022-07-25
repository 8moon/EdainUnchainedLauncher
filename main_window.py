import configparser
import os
import sys
import tkinter
from cProfile import label
from distutils.command.config import config
from tkinter import RAISED, Label, StringVar, filedialog
import urllib.request
import shutil
import zipfile
import requests
import gdown

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

# function for installing or updating edain unchained with source from download repository
def install_mod():
    # check if mod is installed in latest version --> TO DO
    # check if temp folder for installation/update exists and delete if needed --> TO DO
    # create temp folder for installation/update --> TO DO
    # download folder content from google drive into temp folder --> TO DO
    folder_url = r'https://drive.google.com/drive/folders/1iAZZdiWQxQFZpdez8MFu1TLl0y2lNB-s'
    gdown.download_folder(url=folder_url, output=r'C:\Users\thoma\Desktop\Edain Unchained Test files', quiet=False, use_cookies=False)
    # unzip files into temp directory --> TO DO
    zipfile_path = r'C:\Users\thoma\Desktop\Edain Unchained Test files\file_01.zip'
    target_zipfile_path = r'C:\Users\thoma\Desktop\Edain Unchained Test files\bfmeii folder'
    with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
        zip_ref.extractall(target_zipfile_path)
    # move override unzipped files from temp folder into target directory --> TO DO
    # cleanup temp directory afterwards --> TO DO
    os.remove(zipfile_path) if os.path.exists(zipfile_path) else print("zipfile_path does not exist")

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

# button install or update edain unchained submod
# asset.dat goes into bfmeii folder location
# _____________harad_sounds.big goes into bfmeiirotwk folder
# ______________Edain_Unchained.big goes into bfmeiirotwk folder
# ___________________harad_art.big goes into bfmeiirotwk folder
install_edain_unchained_button_text = tkinter.StringVar()
install_edain_unchained_button_text.set("Update") if 1 > 0 else install_edain_unchained_button_text.set("Install")
install_edain_unchained = tkinter.Button(main, textvariable = install_edain_unchained_button_text, command = install_mod)
install_edain_unchained.pack()

# button close window
button_close = tkinter.Button(main, text = "Close", command = close_window)
button_close.pack()

# loop for main application window
main.mainloop()
