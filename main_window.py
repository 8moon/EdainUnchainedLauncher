import configparser
import os
import shutil
import sys
import tkinter
import urllib.request
import zipfile
from cProfile import label
from distutils.command.config import config
from multiprocessing import current_process
from tkinter import RAISED, Label, StringVar, filedialog

import gdown
import requests

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
    if button.cget('text') == 'browse_path_bfmeii':
        write_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII', directory_path)
        bfmeII_path_label.set(directory_path)
    elif button.cget('text') == 'browse_path_bfmeiirotwk':
        write_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK', directory_path)
        bfmeIIrotwk_path_label.set(directory_path)

# function for installing or updating edain unchained with source from download repository
# asset.dat goes into bfmeii folder location
# _____________harad_sounds.big goes into bfmeiirotwk folder
# ______________Edain_Unchained.big goes into bfmeiirotwk folder
# ___________________harad_art.big goes into bfmeiirotwk folder
# englishpatch201.big goes into bfmeiirotwk/lang
def install_mod(): # -> Add version check and abort update if game is installed
    edain_unchained_installation_temp = read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/edain_unchained_installation_temp'
    # check if mod is installed in latest version by comparing name of zipfiles --> TO DO
    newest_version = check_newest_version()
    if read_ini('launcher_options.ini', 'MODINFO', 'EDAIN_UNCHAINED_VERSION') == newest_version:
        print('newest version already installed')
        return
    # check if temp folder for installation/update exists and delete if needed
    if os.path.isdir(edain_unchained_installation_temp): shutil.rmtree(edain_unchained_installation_temp)
    # create temp folder for installation/update
    os.mkdir(edain_unchained_installation_temp)
    # download folder content from google drive into temp folder
    folder_url = read_ini('launcher_options.ini', 'URL', 'EDAIN_UNCHAINED_DOWNLOAD_FOLDER')
    gdown.download_folder(url=folder_url, output=edain_unchained_installation_temp, quiet=False, use_cookies=False)
    # unzip files into temp directory and delete zip files
    for item in os.listdir(edain_unchained_installation_temp):
        if item.endswith('.zip'):
            file_name = edain_unchained_installation_temp + '/' + item
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(edain_unchained_installation_temp)
            zip_ref.close()
            os.remove(file_name)
    # move override unzipped files from temp folder into target directory
    os.replace(edain_unchained_installation_temp + '/asset.dat', read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII') + '/asset.dat')
    os.replace(edain_unchained_installation_temp + '/englishpatch201.big', read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/lang/englishpatch201.big')
    for item in os.listdir(edain_unchained_installation_temp):
        extracted_file_name = edain_unchained_installation_temp + '/' + item
        os.replace(extracted_file_name, read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + item)
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_installation_temp): shutil.rmtree(edain_unchained_installation_temp)
    # update launcher_options.ini
    write_ini('launcher_options.ini', 'MODINFO', 'EDAIN_UNCHAINED_VERSION', newest_version)

# function for checking the newest game version from google drive
def check_newest_version():
    # store paths in variable
    edain_unchained_version_temp = read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/edain_unchained_version_temp'
    # check if temp folder for check newest game version exists and delete if needed
    if os.path.isdir(edain_unchained_version_temp): shutil.rmtree(edain_unchained_version_temp)
    # create temp folder for check update
    os.mkdir(edain_unchained_version_temp)
    # download folder content from google drive into temp folder
    version_folder_url = read_ini('launcher_options.ini', 'URL', 'EDAIN_UNCHAINED_VERSION_INFO_FOLDER')
    gdown.download_folder(url=version_folder_url, output=edain_unchained_version_temp, quiet=False, use_cookies=False)
    newest_version = read_ini(edain_unchained_version_temp + '/eu_version_info.ini', 'MODINFO', 'EDAIN_UNCHAINED_VERSION')
    # print("newest version: " + newest_version + "\n")
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_version_temp): shutil.rmtree(edain_unchained_version_temp)
    return newest_version

# funciton for checking for updates
def check_update():
    # compare local mod version with current mod version
    local_version = read_ini('launcher_options.ini', 'MODINFO', 'EDAIN_UNCHAINED_VERSION')
    print('local version: ' + local_version + '\n')
    newest_version = check_newest_version()
    print('newest version: ' + newest_version + '\n')
    print('Game is up to date\n') if local_version == newest_version else print('Update available\n')

# function for reading ini files
def read_ini(filepath, section, subsection):
    config = configparser.ConfigParser()
    config.read(filepath)
    return config[section][subsection]

# function for writing into ini files
def write_ini(filepath, section, subsection, update_text):
    config = configparser.ConfigParser()
    config.read(filepath)
    config[section][subsection] = update_text
    with open(filepath, 'w') as configfile:
        config.write(configfile)
    
#--------------------------#
# main window with buttons #
#--------------------------#

# main application window
main = tkinter.Tk()
main.geometry('500x200')

# button browse path for BFME II
browse_path_bfmeii = tkinter.Button(main, text = 'browse_path_bfmeii')
browse_path_bfmeii.config(command = lambda button = browse_path_bfmeii : open_directory(button))
browse_path_bfmeii.pack()

# label for bfmeii current path
bfmeII_path_label = tkinter.StringVar()
label_bfmeii = Label(main, textvariable = bfmeII_path_label, relief = RAISED)
bfmeII_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII'))
label_bfmeii.pack()

# button browse path for BFME II ROTWK
browse_path_bfmeiirotwk = tkinter.Button(main, text = 'browse_path_bfmeiirotwk')
browse_path_bfmeiirotwk.config(command = lambda button = browse_path_bfmeiirotwk : open_directory(button))
browse_path_bfmeiirotwk.pack()

# label for bfmeiirotwk current path
bfmeIIrotwk_path_label = tkinter.StringVar()
label_bfmeiirotwk = Label(main, textvariable = bfmeIIrotwk_path_label, relief = RAISED)
bfmeIIrotwk_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK'))
label_bfmeiirotwk.pack()

# button check for updates
check_for_updates = tkinter.Button(main, text = 'Check for Updates', command = check_update)
check_for_updates.pack()

# button install edain unchained submod
install_edain_unchained_button_text = tkinter.StringVar()
install_edain_unchained_button_text.set('Installation') # if 1 > 0 else install_edain_unchained_button_text.set('Update')
install_edain_unchained = tkinter.Button(main, textvariable = install_edain_unchained_button_text, command = install_mod)
install_edain_unchained.pack()

# button close window
button_close = tkinter.Button(main, text = 'Close', command = close_window)
button_close.pack()

# loop for main application window
main.mainloop()
