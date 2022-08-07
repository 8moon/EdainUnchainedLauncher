import configparser
import os
import os.path
import shutil
import threading
import time
import tkinter
import tkinter.ttk
import zipfile
from tkinter import filedialog, messagebox

import customtkinter
import gdown

# ------------------#
# global variables #
# ------------------#

isDownloading = False
fileDownloading = ''


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


def install_all():
    deactivate_all_buttons()
    label_feedback.configure(text='Starting download ...')
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
    gdown.download_folder(url=version_folder_url, output=edain_unchained_version_temp, quiet=False,
                          use_cookies=False)

    edain_unchained_installation_temp = read_ini('launcher_options.ini', 'GAMEPATH',
                                                 'BFMEIIROTWK') + '/edain_unchained_installation_temp'
    # check if mod is installed in latest version
    newest_version = check_newest_version('MODINFO', 'EDAIN_UNCHAINED_VERSION')

    # check if temp folder for installation/update exists and delete if needed
    if os.path.isdir(edain_unchained_installation_temp):
        shutil.rmtree(edain_unchained_installation_temp)
    # create temp folder for installation/update
    os.mkdir(edain_unchained_installation_temp)

    config = configparser.ConfigParser()
    config.read('launcher_options.ini')

    # download folder content from google drive into temp folder
    folder_url = read_ini('launcher_options.ini', 'URL', 'EDAIN_UNCHAINED_DOWNLOAD_FOLDER')

    global isDownloading
    isDownloading = True
    global fileDownloading
    fileDownloading = 'file'

    try:
        threading.Thread(target=download_all_progressbar).start()
        gdown.download_folder(url=folder_url, output=edain_unchained_installation_temp, quiet=False, use_cookies=False)
        isDownloading = False
    except OSError:
        isDownloading = False
        label_feedback.configure(text='Error downloading submod-files')

    edain_unchained_installation_temp = read_ini('launcher_options.ini', 'GAMEPATH',
                                                 'BFMEIIROTWK') + '/edain_unchained_installation_temp'
    # unzip files into temp directory and delete zip files
    for item in os.listdir(edain_unchained_installation_temp):
        if item.endswith('.zip'):
            print('File: ' + item)
            file_name = edain_unchained_installation_temp + '/' + item
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(edain_unchained_installation_temp)
            zip_ref.close()
            os.remove(file_name)
    # move override unzipped files from temp folder into target directory
    if os.path.exists(edain_unchained_installation_temp + '/asset.dat'):
        os.replace(edain_unchained_installation_temp + '/asset.dat',
                   read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII') + '/asset.dat')
    if os.path.exists(edain_unchained_installation_temp + '/englishpatch201.big'):
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
    for (file, filename) in config.items('FILEVERSION'):
        print(file + filename)
        write_ini('launcher_options.ini', 'FILEVERSION', file, check_newest_version('FILEVERSION', file))
    # update version label in launcher
    eu_version_label.configure(
        text='Version ' + read_ini('launcher_options.ini', 'MODINFO', 'edain_unchained_version'))
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_version_temp):
        shutil.rmtree(edain_unchained_version_temp)
    label_feedback.configure(text='Latest Edain Unchained Version is installed!')
    activate_all_buttons()

def download_all_progressbar():
    while isDownloading:
        file_size = 0
        for temp_file in os.scandir(
                read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/edain_unchained_installation_temp'):
            file_size += os.path.getsize(temp_file)
            print('FILE: ' + str(round(file_size, 2)))
            label_feedback.configure(text='Downloading submod: ' + str(round((file_size/1000000), 2)) + 'MB')
        time.sleep(1)

def install_files():
    deactivate_all_buttons()
    label_feedback.configure(text='Checking for updates ...')
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
    gdown.download_folder(url=version_folder_url, output=edain_unchained_version_temp, quiet=False,
                          use_cookies=False)

    edain_unchained_installation_temp = read_ini('launcher_options.ini', 'GAMEPATH',
                                                 'BFMEIIROTWK') + '/edain_unchained_installation_temp'
    # check if mod is installed in latest version
    newest_version = check_newest_version('MODINFO', 'EDAIN_UNCHAINED_VERSION')

    # check if temp folder for installation/update exists and delete if needed
    if os.path.isdir(edain_unchained_installation_temp):
        shutil.rmtree(edain_unchained_installation_temp)
    # create temp folder for installation/update
    os.mkdir(edain_unchained_installation_temp)

    config = configparser.ConfigParser()
    config.read('launcher_options.ini')

    for (file, filename) in config.items('FILEVERSION'):
        newest_file_version = check_newest_version('FILEVERSION', file)
        local_file_version = read_ini('launcher_options.ini', 'FILEVERSION', file)
        if local_file_version != newest_file_version:
            file_url = check_newest_version('FILEURL', file)
            edain_unchained_installation_temp = read_ini('launcher_options.ini', 'GAMEPATH',
                                                         'BFMEIIROTWK') + '/edain_unchained_installation_temp/' + file + '.zip'
            print('TEST URL: ' + edain_unchained_installation_temp)
            label_feedback.configure(text='Downloading ' + file)

            global isDownloading
            isDownloading = True
            global fileDownloading
            fileDownloading = file

            try:
                threading.Thread(target=download_progressbar).start()
                gdown.download(url=file_url, output=edain_unchained_installation_temp, quiet=False, use_cookies=False)
                isDownloading = False
            except OSError:
                isDownloading = False
                label_feedback.configure(text='Error downloading file: ' + file)

    edain_unchained_installation_temp = read_ini('launcher_options.ini', 'GAMEPATH',
                                                 'BFMEIIROTWK') + '/edain_unchained_installation_temp'
    # unzip files into temp directory and delete zip files
    for item in os.listdir(edain_unchained_installation_temp):
        if item.endswith('.zip'):
            print('File: ' + item)
            file_name = edain_unchained_installation_temp + '/' + item
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(edain_unchained_installation_temp)
            zip_ref.close()
            os.remove(file_name)
    # move override unzipped files from temp folder into target directory
    if os.path.exists(edain_unchained_installation_temp + '/asset.dat'):
        os.replace(edain_unchained_installation_temp + '/asset.dat',
                   read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII') + '/asset.dat')
    if os.path.exists(edain_unchained_installation_temp + '/englishpatch201.big'):
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
    for (file, filename) in config.items('FILEVERSION'):
        print(file + filename)
        write_ini('launcher_options.ini', 'FILEVERSION', file, check_newest_version('FILEVERSION', file))
    # update version label in launcher
    eu_version_label.configure(
        text='Version ' + read_ini('launcher_options.ini', 'MODINFO', 'edain_unchained_version'))
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_version_temp):
        shutil.rmtree(edain_unchained_version_temp)
    label_feedback.configure(text='Latest Edain Unchained Version is installed!')
    activate_all_buttons()


# function for installing or updating edain unchained with source from download repository
# asset.dat goes into bfmeii folder location
# _____________harad_sounds.big goes into bfmeiirotwk folder
# ______________Edain_Unchained.big goes into bfmeiirotwk folder
# ___________________harad_art.big goes into bfmeiirotwk folder
# englishpatch201.big goes into bfmeiirotwk/lang
def start_install_thread(button):
    if check_game_paths():
        # reinstall everything
        if button.cget('text') == 'Repair':
            approve_installation1 = tkinter.messagebox.askyesno(title='Repair Submod',
                                                                message='Do you want to download and install all submod files again?')
            if approve_installation1:
                threading.Thread(target=install_all).start()
        # update only new files
        if button.cget('text') == 'Update':
            approve_installation2 = tkinter.messagebox.askyesno(title='Update Submod',
                                                                message='Do you want to update the submod?')
            if approve_installation2:
                threading.Thread(target=install_files).start()


def download_progressbar():
    while isDownloading:
        for temp_file in os.listdir(
                read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/edain_unchained_installation_temp'):
            if temp_file.startswith(fileDownloading):
                file_size = os.path.getsize(read_ini('launcher_options.ini', 'GAMEPATH',
                                                     'BFMEIIROTWK') + '/edain_unchained_installation_temp/' + temp_file)
                file_size = file_size / 1000000
                print('FILE: ' + str(round(file_size, 2)))
                label_feedback.configure(
                    text='Downloading file: ' + fileDownloading + ' ' + str(round(file_size, 2)) + 'MB')
        time.sleep(1)


def deactivate_all_buttons():
    button_start_game['state'] = "disabled"
    button_activate_submod['state'] = "disabled"
    button_deactivate_submod['state'] = "disabled"
    install_edain_unchained['state'] = "disabled"
    check_for_updates['state'] = "disabled"


def activate_all_buttons():
    button_start_game['state'] = "normal"
    button_activate_submod['state'] = "normal"
    button_deactivate_submod['state'] = "normal"
    install_edain_unchained['state'] = "normal"
    check_for_updates['state'] = "normal"


# function for checking the newest game version from google drive
def check_newest_version(section, subsection):
    try:
        # store paths in variable
        edain_unchained_version_temp = read_ini('launcher_options.ini', 'GAMEPATH',
                                                'BFMEIIROTWK') + '/edain_unchained_version_temp'
        newest_version = read_ini(edain_unchained_version_temp + '/eu_version_info.ini', section, subsection)
        # print("newest version: " + newest_version + "\n")
        eu_version_label.configure(
            text='Version ' + read_ini('launcher_options.ini', 'MODINFO', 'edain_unchained_version'))
        print(section + ' ' + subsection + ' -Version: ' + newest_version)
        return newest_version
    except OSError:
        label_feedback.configure(text='Server cannot be reached!')
        return ''


# funciton for checking for updates
def check_update():
    try:
        # compare local mod version with current mod version
        local_version = read_ini('launcher_options.ini', 'MODINFO', 'EDAIN_UNCHAINED_VERSION')
        print('local version: ' + local_version + '\n')
        newest_version = check_newest_version('MODINFO', 'EDAIN_UNCHAINED_VERSION')
        print('newest version: ' + newest_version + '\n')
        label_feedback.configure(
            text='Game is up to date!') if local_version == newest_version else label_feedback.configure(
            text='Update is available!')
    except OSError:
        label_feedback.configure(text='Cannot check for updates!')


# function for reading ini files
def read_ini(filepath, section, subsection):
    try:
        config = configparser.ConfigParser()
        config.read(filepath)
        return config[section][subsection]
    except FileNotFoundError:
        label_feedback.configure(text='Can not read from launcher_options.ini!')


# function for writing into ini files
def write_ini(filepath, section, subsection, update_text):
    try:
        config = configparser.ConfigParser()
        config.read(filepath)
        config[section][subsection] = update_text
        with open(filepath, 'w') as configfile:
            config.write(configfile)
    except FileNotFoundError:
        label_feedback.configure(text='Can not write in launcher_options.ini!')


# function for starting the game
def start_game():
    try:
        label_feedback.configure(text='DESTROY YOUR ENEMY!')
        os.chdir(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK'))
        os.system('lotrbfme2ep1.exe')
        close_window()
    except OSError:
        label_feedback.configure(text='No lotrbfme2ep1.exe found!')


# function for deactivating the submod
def deactivate_submod():
    if check_game_paths():
        try:
            config = configparser.ConfigParser()
            config.read('launcher_options.ini')

            for (file, filename) in config.items('FILENAME'):
                if file != 'eu_asset' and file != 'eu_lang':
                    if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak') is False:
                        os.rename(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename,
                                  read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak')

            label_feedback.configure(text='Submod is deactivated!')
        except OSError:
            file_number = 1
            file_exists = 1
            for (file, filename) in config.items('FILENAME'):
                file_number += 1
                if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak'):
                    file_exists += 1
            if file_number == file_exists:
                label_feedback.configure(text='Submod is already deactivated!')
            else:
                message = 'Files are missing: '
                for (file, filename) in config.items('FILENAME'):
                    if (os.path.exists(
                            read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak') is False):
                        message = message + '\n' + filename
                    else:
                        os.rename(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak',
                                  read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename)

                label_feedback.configure(text='Something went wrong!')
                tkinter.messagebox.showerror(title='Deactivate submod', message=message)


# function for activating the submod
def activate_submod():
    if check_game_paths():
        try:
            config = configparser.ConfigParser()
            config.read('launcher_options.ini')

            for (file, filename) in config.items('FILENAME'):
                if os.path.exists(
                        read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename) is False:
                    os.rename(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak',
                              read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename)

            label_feedback.configure(text='Submod is activated!')
        except OSError:
            file_number = 1
            file_exists = 1
            for (file, filename) in config.items('FILENAME'):
                file_number += 1
                if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename):
                    file_exists += 1
            if file_number == file_exists:
                label_feedback.configure(text='Submod is already activated!')
            else:
                message = 'Files are missing: '
                for (file, filename) in config.items('FILENAME'):
                    if (os.path.exists(
                            read_ini('launcher_options.ini', 'GAMEPATH',
                                     'BFMEIIROTWK') + '/' + filename) is False):
                        message = message + '\n' + filename + '.bak'

                label_feedback.configure(text='Something went wrong!')
                tkinter.messagebox.showerror(title='Activate submod', message=message)


def check_game_paths():
    message = ''
    if read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII') != '':
        if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII')):
            if read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') != '':
                if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK')):
                    if os.path.exists((read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/lang')):
                        message = ''
                    else:
                        message = 'You have no lang folder in your BFME II ROTWK folder'
                else:
                    message = 'Your BFME II ROTWK game-path does not exist'
            else:
                message = 'Your BFME II ROTWK game-path is not given'
        else:
            message = 'Your BFME II game-path does not exist'
    else:
        message = 'Your BFME II game-path is not given'

    if message != '':
        tkinter.messagebox.showerror(title='Wrong Gamepaths', message=message)
        return False
    return True


# function for changing the backround color
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
frame_left.grid_rowconfigure(3, minsize=20)  # empty row with minsize as spacing (after eu_label)

# edain unchained label
eu_label = customtkinter.CTkLabel(frame_left, text='Edain Unchained', text_font=("Ringbearer", 16))
eu_label.grid(row=1, column=0, pady=10, padx=10)

# edain unchained version label
eu_version_label = customtkinter.CTkLabel(frame_left, text_font=("Ringbearer", 12))
eu_version_label.configure(text='Version ' + read_ini('launcher_options.ini', 'MODINFO', 'edain_unchained_version'))
eu_version_label.grid(row=2, column=0, pady=10, padx=10)

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
label_appearance_mode = customtkinter.CTkLabel(frame_left, text='Appearance Mode:')
label_appearance_mode.grid(row=9, column=0, pady=0, padx=20, sticky='w')

# options for Appearance Mode
option_appearance_mode = customtkinter.CTkOptionMenu(frame_left, values=['Light', 'Dark', 'System'],
                                                     command=change_appearance_mode)
option_appearance_mode.grid(row=10, column=0, pady=10, padx=20, sticky='w')
option_appearance_mode.set('Dark')

# ============ frame_right ============

# configure grid layout (1x7)
frame_right.rowconfigure(1, weight=1)
frame_right.rowconfigure(3, weight=1)
frame_right.rowconfigure(5, weight=1)
frame_right.columnconfigure(0, weight=1)

frame_gamepath = customtkinter.CTkFrame(master=frame_right)
frame_gamepath.grid(row=1, column=0, columnspan=2, rowspan=2, pady=20, padx=20, sticky='nsew')
frame_gamepath.grid_rowconfigure(0, weight=1)
frame_gamepath.grid_rowconfigure(1, weight=1)
frame_gamepath.grid_columnconfigure(0, weight=1)
frame_gamepath.grid_columnconfigure(1, weight=1)

frame_update = customtkinter.CTkFrame(master=frame_right)
frame_update.grid(row=3, column=0, columnspan=2, rowspan=2, pady=20, padx=20, sticky='nsew')
frame_update.grid_rowconfigure(0, weight=1)
frame_update.grid_rowconfigure(1, weight=1)
frame_update.grid_columnconfigure(0, weight=1)

frame_feedback = customtkinter.CTkFrame(master=frame_right)
frame_feedback.grid(row=5, column=0, columnspan=1, rowspan=2, pady=20, padx=20, sticky='nsew')
frame_feedback.grid_rowconfigure(0, weight=1)
frame_feedback.grid_rowconfigure(1, weight=1)
frame_feedback.grid_columnconfigure(0, weight=1)

# button browse path for BFME II
browse_path_bfmeii = tkinter.Button(frame_gamepath, text='browse_path_bfmeii', width=25, height=1, )
browse_path_bfmeii.configure(command=lambda button=browse_path_bfmeii: open_directory(button))
browse_path_bfmeii.grid(row=0, column=0, pady=10, padx=20)

# label for bfmeii current path
bfmeII_path_label = tkinter.StringVar()
label_bfmeii = customtkinter.CTkLabel(frame_gamepath, textvariable=bfmeII_path_label, height=1, )
bfmeII_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII'))
label_bfmeii.grid(row=0, column=1, pady=10, padx=20, )

# button browse path for BFME II ROTWK
browse_path_bfmeiirotwk = tkinter.Button(frame_gamepath, text='browse_path_bfmeiirotwk', width=25, height=1, )
browse_path_bfmeiirotwk.configure(command=lambda button=browse_path_bfmeiirotwk: open_directory(button))
browse_path_bfmeiirotwk.grid(row=1, column=0, pady=10, padx=20)

# label for bfmeiirotwk current path
bfmeIIrotwk_path_label = tkinter.StringVar()
label_bfmeiirotwk = customtkinter.CTkLabel(frame_gamepath, textvariable=bfmeIIrotwk_path_label, height=1, )
bfmeIIrotwk_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK'))
label_bfmeiirotwk.grid(row=1, column=1, pady=10, padx=20)

# button install edain unchained submod
install_edain_unchained = tkinter.Button(frame_update, text='Repair', width=20, height=1)
install_edain_unchained.configure(command=lambda button=install_edain_unchained: start_install_thread(button))
install_edain_unchained.grid(row=0, column=0, pady=10, padx=20)

# label install
install_edain_unchained_label = customtkinter.CTkLabel(frame_update, text='Reinstall the mod')
install_edain_unchained_label.grid(row=0, column=1, pady=10, padx=20)

# button check for updates
check_for_updates = tkinter.Button(frame_update, text='Update', width=20, height=1)
check_for_updates.configure(command=lambda button=check_for_updates: start_install_thread(button))
check_for_updates.grid(row=1, column=0, pady=10, padx=20)

# label update
label_update = customtkinter.CTkLabel(frame_update, text='Update to the latest version')
label_update.grid(row=1, column=1, pady=10, padx=20)

# feedback label
label_feedback = customtkinter.CTkLabel(frame_feedback, width=50, height=2, text_font='BOLD')
label_feedback.configure(text='Do something!')
label_feedback.grid(row=0, column=0, pady=0, padx=15, sticky='ew')

# feedback progressbar
progressbar = tkinter.ttk.Progressbar(frame_feedback, orient='horizontal', mode='determinate')
progressbar.grid(row=1, column=0, sticky="ew", padx=15, pady=0)

# loop for main application window
main.mainloop()
