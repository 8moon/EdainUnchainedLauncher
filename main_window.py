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
# asset.dat goes into bfmeii folder location
# _____________harad_sounds.big goes into bfmeiirotwk folder
# ______________Edain_Unchained.big goes into bfmeiirotwk folder
# ___________________harad_art.big goes into bfmeiirotwk folder
# englishpatch201.big goes into bfmeiirotwk/lang
def install_mod():
    edain_unchained_installation_temp = read_launcher_options("GAMEPATH", "BFMEIIROTWK") + "/edain_unchained_installation_temp"
    # check if mod is installed in latest version by comparing name of zipfiles --> TO DO
    # check if temp folder for installation/update exists and delete if needed --> TO DO
    if os.path.isdir(edain_unchained_installation_temp): shutil.rmtree(edain_unchained_installation_temp)
    # create temp folder for installation/update --> TO DO
    os.mkdir(edain_unchained_installation_temp)
    # download folder content from google drive into temp folder --> TO DO
    folder_url = r'https://drive.google.com/drive/folders/1iAZZdiWQxQFZpdez8MFu1TLl0y2lNB-s'
    gdown.download_folder(url=folder_url, output=edain_unchained_installation_temp, quiet=False, use_cookies=False)
    # unzip files into temp directory and delete zip files
    for item in os.listdir(edain_unchained_installation_temp):
        if item.endswith(".zip"):
            file_name = edain_unchained_installation_temp + "/" + item
            # print(file_name + "\n")
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(edain_unchained_installation_temp)
            zip_ref.close()
            os.remove(file_name)
    # move override unzipped files from temp folder into target directory --> TO DO
    os.replace(edain_unchained_installation_temp + "/asset.dat", read_launcher_options("GAMEPATH", "BFMEII") + "/asset.dat")
    os.replace(edain_unchained_installation_temp + "/englishpatch201.big", read_launcher_options("GAMEPATH", "BFMEIIROTWK") + "/lang/englishpatch201.big")
    for item in os.listdir(edain_unchained_installation_temp):
        extracted_file_name = edain_unchained_installation_temp + "/" + item
        os.replace(extracted_file_name, read_launcher_options("GAMEPATH", "BFMEIIROTWK") + "/" + item)
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_installation_temp): shutil.rmtree(edain_unchained_installation_temp)
    # update launcher_options.ini --> TO DO

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

install_edain_unchained_button_text = tkinter.StringVar()
install_edain_unchained_button_text.set("Update") if 1 > 0 else install_edain_unchained_button_text.set("Install")
install_edain_unchained = tkinter.Button(main, textvariable = install_edain_unchained_button_text, command = install_mod)
install_edain_unchained.pack()

# button close window
button_close = tkinter.Button(main, text = "Close", command = close_window)
button_close.pack()

# loop for main application window
main.mainloop()
