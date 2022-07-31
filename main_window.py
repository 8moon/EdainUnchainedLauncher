import configparser
import os
import shutil
import tkinter
import zipfile
import customtkinter
import gdown
from tkinter import *
from tkinter import filedialog


# ------------------#
# global variables #
# ------------------#

# ------------------#
# button functions #
# ------------------#


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
def install_mod():
    edain_unchained_installation_temp = read_ini('launcher_options.ini', 'GAMEPATH',
                                                 'BFMEIIROTWK') + '/edain_unchained_installation_temp'
    # check if mod is installed in latest version
    newest_version = check_newest_version()
    if read_ini('launcher_options.ini', 'MODINFO', 'EDAIN_UNCHAINED_VERSION') == newest_version:
        print('newest version already installed')
        return  # is version check and abort necessary or should it be force installation/update?
    # check if temp folder for installation/update exists and delete if needed
    if os.path.isdir(edain_unchained_installation_temp):
        shutil.rmtree(edain_unchained_installation_temp)
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
    os.replace(edain_unchained_installation_temp + '/asset.dat',
               read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII') + '/asset.dat')
    os.replace(edain_unchained_installation_temp + '/englishpatch201.big',
               read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/lang/englishpatch201.big')
    for item in os.listdir(edain_unchained_installation_temp):
        extracted_file_name = edain_unchained_installation_temp + '/' + item
        os.replace(extracted_file_name, read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + item)
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_installation_temp):
        shutil.rmtree(edain_unchained_installation_temp)
    # update launcher_options.ini
    write_ini('launcher_options.ini', 'MODINFO', 'EDAIN_UNCHAINED_VERSION', newest_version)


# function for checking the newest game version from google drive
def check_newest_version():
    # store paths in variable
    edain_unchained_version_temp = read_ini('launcher_options.ini', 'GAMEPATH',
                                            'BFMEIIROTWK') + '/edain_unchained_version_temp'
    # check if temp folder for check newest game version exists and delete if needed
    if os.path.isdir(edain_unchained_version_temp):
        shutil.rmtree(edain_unchained_version_temp)
    # create temp folder for check update
    os.mkdir(edain_unchained_version_temp)
    # download folder content from google drive into temp folder
    version_folder_url = read_ini('launcher_options.ini', 'URL', 'EDAIN_UNCHAINED_VERSION_INFO_FOLDER')
    gdown.download_folder(url=version_folder_url, output=edain_unchained_version_temp, quiet=False, use_cookies=False)
    newest_version = read_ini(edain_unchained_version_temp + '/eu_version_info.ini', 'MODINFO',
                              'EDAIN_UNCHAINED_VERSION')
    # print("newest version: " + newest_version + "\n")
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_version_temp):
        shutil.rmtree(edain_unchained_version_temp)
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


# function for starting the game
def start_game():
    os.chdir(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK'))
    os.system('lotrbfme2ep1.exe')
    close_window()


# function for deactivating the submod
def deactivate_submod():
    config = configparser.ConfigParser()
    config.read('launcher_options.ini')

    for (file, filename) in config.items('FILENAME'):
        os.rename(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename,
                  read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak')


# function for activating the submod
def activate_submod():
    config = configparser.ConfigParser()
    config.read('launcher_options.ini')

    for (file, filename) in config.items('FILENAME'):
        os.rename(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak',
                  read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename)


def change_appearance_mode(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)


# --------------------------#
# main window with buttons #
# --------------------------#

# main application window
main = customtkinter.CTk()
main.geometry('700x420')
main.title('Edain Unchained Launcher')

# ============ create two frames ============

# configure grid layout (2x1)
main.grid_rowconfigure(0, weight=1)
main.grid_columnconfigure(1, weight=1)

frame_left = customtkinter.CTkFrame(master=main, width=180, corner_radius=0)
frame_left.grid(row=0, column=0, sticky='nswe')

frame_right = customtkinter.CTkFrame(master=main)
frame_right.grid(row=0, column=1, sticky='nswe', padx=20, pady=20)

# ============ frame_left ============

# configure grid layout (1x11)
frame_left.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing (top)
frame_left.grid_rowconfigure(7, weight=1)  # empty row as spacing (Appearance Mode is at bottom)
frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing (bottom)
frame_left.grid_rowconfigure(2, minsize=20)  # empty row with minsize as spacing (after eu_label)

# edain unchained label
eu_label = customtkinter.CTkLabel(frame_left, text='Edain Unchained', text_font=("Ringbearer", 16))
eu_label.grid(row=1, column=0, pady=10, padx=10)

# button start game
button_start_game = customtkinter.CTkButton(frame_left, text='Start game', command=start_game)
button_start_game.grid(row=6, column=0, pady=10, padx=20)

# button deactivate submod
button_deactivate_submod = customtkinter.CTkButton(frame_left, text='deactivate submod', command=deactivate_submod)
button_deactivate_submod.grid(row=3, column=0, pady=10, padx=20)

# button activate submod
button_activate_submod = customtkinter.CTkButton(frame_left, text='activate submod', command=activate_submod)
button_activate_submod.grid(row=4, column=0, pady=10, padx=20)

# label Appearance Mode
label_appearance_mode = customtkinter.CTkLabel(frame_left, text="Appearance Mode:")
label_appearance_mode.grid(row=9, column=0, pady=0, padx=20, sticky="w")

# options for Appearance Mode
option_appearance_mode = customtkinter.CTkOptionMenu(frame_left, values=["Light", "Dark", "System"],
                                                     command=change_appearance_mode)
option_appearance_mode.grid(row=10, column=0, pady=10, padx=20, sticky="w")
option_appearance_mode.set('Dark')

# ============ frame_right ============

# configure grid layout (1x7)
frame_right.rowconfigure(1, weight=1)
frame_right.rowconfigure(3, weight=1)
frame_right.rowconfigure(5, weight=1)
frame_right.columnconfigure(0, weight=1)

frame_gamepath = customtkinter.CTkFrame(master=frame_right)
frame_gamepath.grid(row=1, column=0, columnspan=2, rowspan=2, pady=20, padx=20, sticky="nsew")
frame_gamepath.grid_rowconfigure(0, weight=1)
frame_gamepath.grid_rowconfigure(1, weight=1)
frame_gamepath.grid_columnconfigure(0, weight=1)
frame_gamepath.grid_columnconfigure(1, weight=1)

frame_update = customtkinter.CTkFrame(master=frame_right)
frame_update.grid(row=3, column=0, columnspan=1, rowspan=2, pady=20, padx=20, sticky="nsew")
frame_update.grid_rowconfigure(0, weight=1)
frame_update.grid_rowconfigure(1, weight=1)
frame_update.grid_columnconfigure(0, weight=1)

frame_feedback = customtkinter.CTkFrame(master=frame_right)
frame_feedback.grid(row=5, column=0, columnspan=1, rowspan=2, pady=20, padx=20, sticky="nsew")
frame_feedback.grid_rowconfigure(0, weight=1)
frame_feedback.grid_rowconfigure(1, weight=1)
frame_feedback.grid_columnconfigure(0, weight=1)

# button browse path for BFME II
browse_path_bfmeii = tkinter.Button(frame_gamepath, text='browse_path_bfmeii', width=25, height=1, )
browse_path_bfmeii.config(command=lambda button=browse_path_bfmeii: open_directory(button))
browse_path_bfmeii.grid(row=0, column=0, pady=10, padx=20)

# label for bfmeii current path
bfmeII_path_label = tkinter.StringVar()
label_bfmeii = customtkinter.CTkLabel(frame_gamepath, textvariable=bfmeII_path_label, height=1, )
bfmeII_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII'))
label_bfmeii.grid(row=0, column=1, pady=10, padx=20)

# button browse path for BFME II ROTWK
browse_path_bfmeiirotwk = tkinter.Button(frame_gamepath, text='browse_path_bfmeiirotwk', width=25, height=1, )
browse_path_bfmeiirotwk.config(command=lambda button=browse_path_bfmeiirotwk: open_directory(button))
browse_path_bfmeiirotwk.grid(row=1, column=0, pady=10, padx=20)

# label for bfmeiirotwk current path
bfmeIIrotwk_path_label = tkinter.StringVar()
label_bfmeiirotwk = customtkinter.CTkLabel(frame_gamepath, textvariable=bfmeIIrotwk_path_label, height=1, )
bfmeIIrotwk_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK'))
label_bfmeiirotwk.grid(row=1, column=1, pady=10, padx=20)

# button check for updates
check_for_updates = tkinter.Button(frame_update, text='Check for Updates', width=20, height=1, command=check_update)
check_for_updates.grid(row=0, column=0, pady=10, padx=20)

# button install edain unchained submod
install_edain_unchained_button_text = tkinter.StringVar()
install_edain_unchained_button_text.set(
    'Installation')  # if 1 > 0 else install_edain_unchained_button_text.set('Update')
install_edain_unchained = tkinter.Button(frame_update, textvariable=install_edain_unchained_button_text, width=20,
                                         height=1,
                                         command=install_mod)
install_edain_unchained.grid(row=1, column=0, pady=10, padx=20)

# feedback label
label_feedback = customtkinter.CTkLabel(frame_feedback, text='Do something!', width=50, height=2)
label_feedback.grid(row=0, column=0, pady=0, padx=15, sticky="ew")

# feedback progressbar
progressbar = customtkinter.CTkProgressBar(frame_feedback)
progressbar.grid(row=1, column=0, sticky="ew", padx=15, pady=0)

# loop for main application window
main.mainloop()
