import configparser
import glob
import os
import os.path
import shutil
import subprocess
import sys
import threading
import time
import tkinter
import tkinter.ttk
import webbrowser
import winreg
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
    if button.cget('text') == 'Browse BFME2 path':
        write_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII', directory_path)
        bfmeII_path_label.set(directory_path)
    elif button.cget('text') == 'Browse ROTWK path':
        write_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK', directory_path)
        bfmeIIrotwk_path_label.set(directory_path)
    is_installed()


# function for installing edain unchained with source from download repository
# asset.dat goes into bfmeii folder location
# _____________harad_sounds.big goes into bfmeiirotwk folder
# ______________Edain_Unchained.big goes into bfmeiirotwk folder
# ___________________harad_art.big goes into bfmeiirotwk folder
# englishpatch201.big goes into bfmeiirotwk/lang
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
            print('Unzipping File: ' + item)
            file_name = edain_unchained_installation_temp + '/' + item
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(edain_unchained_installation_temp)
            zip_ref.close()
            os.remove(file_name)

    # deactivate language
    check_language('edain_unchained_installation_temp')
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
        if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + item + '.bak'):
            os.remove(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + item + '.bak')
            print('Old file removed: ' + item)
    # activate submod
    write_ini('launcher_options.ini', 'SETTINGS', 'activated', 'True')
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_installation_temp):
        shutil.rmtree(edain_unchained_installation_temp)
    # update launcher_options.ini
    write_ini('launcher_options.ini', 'MODINFO', 'EDAIN_UNCHAINED_VERSION', newest_version)
    for (file, filename) in config.items('FILEVERSION'):
        print('Current Version: ' + file + ' - ' + filename)
        write_ini('launcher_options.ini', 'FILEVERSION', file, check_newest_version('FILEVERSION', file))
    # update version label in launcher
    eu_version_label.configure(
        text='Version ' + read_ini('launcher_options.ini', 'MODINFO', 'edain_unchained_version'))
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_version_temp):
        shutil.rmtree(edain_unchained_version_temp)
    check_language('BFMEIIROTWK')
    check_submod_activated()
    activate_submod()
    label_feedback.configure(text='Latest Edain Unchained Version is installed!')
    activate_all_buttons()


# function from install_all for showing the download progress
def download_all_progressbar():
    while isDownloading:
        file_size = 0
        for temp_file in os.scandir(
                read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/edain_unchained_installation_temp'):
            file_size += os.path.getsize(temp_file)
            # print('FILE: ' + str(round(file_size, 2)))
            label_feedback.configure(text='Downloading submod: ' + str(round((file_size/1000000), 2)) + 'MB')
        time.sleep(1)


# function for updating edain unchained with source from download repository
# asset.dat goes into bfmeii folder location
# englishpatch201.big goes into bfmeiirotwk/lang
# all other files go into bfmeiirotwk folder
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
        local_file_version = '0'

        file_not_exists = True
        if file == 'eu_asset':
            if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII') + '/asset.dat'):
                local_file_version = os.path.getsize(
                    read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII') + '/asset.dat')
                file_not_exists = False
            else:
                print('File does not exist: asset.dat')
        elif file == 'eu_lang':
            if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/lang/englishpatch201.big'):
                local_file_version = os.path.getsize(
                    read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/lang/englishpatch201.big')
                file_not_exists = False
            else:
                print('File does not exist: englishpatch201.big')
        else:
            if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + read_ini('launcher_options.ini', 'FILENAME', file)) or os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + read_ini('launcher_options.ini', 'FILENAME', file) + '.bak'):
                if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + read_ini(
                        'launcher_options.ini', 'FILENAME', file)):
                    local_file_version = os.path.getsize(
                        read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + read_ini(
                            'launcher_options.ini', 'FILENAME', file))
                elif os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + read_ini(
                        'launcher_options.ini', 'FILENAME', file) + '.bak'):
                    local_file_version = os.path.getsize(
                        read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + read_ini(
                            'launcher_options.ini', 'FILENAME', file) + '.bak')
                file_not_exists = False
            else:
                print('File does not exist: ' + read_ini('launcher_options.ini', 'FILENAME', file))

        # local_file_version = read_ini('launcher_options.ini', 'FILEVERSION', file)
        print('Filesize: ' + str(file) + '\n -> Installed: ' + str(local_file_version) + '\n -> Newest: ' + str(newest_file_version))

        if str(local_file_version) != str(newest_file_version) or file_not_exists:
            file_url = check_newest_version('FILEURL', file)
            edain_unchained_installation_temp = read_ini('launcher_options.ini', 'GAMEPATH',
                                                         'BFMEIIROTWK') + '/edain_unchained_installation_temp/' + file + '.zip'
            label_feedback.configure(text='Downloading ' + file)

            global isDownloading
            isDownloading = True
            global fileDownloading
            fileDownloading = file

            try:
                threading.Thread(target=download_files_progressbar).start()
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
            print('Unzipping file: ' + item)
            file_name = edain_unchained_installation_temp + '/' + item
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(edain_unchained_installation_temp)
            zip_ref.close()
            os.remove(file_name)
    # deactivate language
    check_language('edain_unchained_installation_temp')
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
        write_ini('launcher_options.ini', 'FILEVERSION', file, check_newest_version('FILEVERSION', file))
    # update version label in launcher
    eu_version_label.configure(
        text='Version ' + read_ini('launcher_options.ini', 'MODINFO', 'edain_unchained_version'))
    # cleanup temp directory afterwards
    if os.path.isdir(edain_unchained_version_temp):
        shutil.rmtree(edain_unchained_version_temp)
    check_language('BFMEIIROTWK')
    activate_submod()
    label_feedback.configure(text='Latest Edain Unchained Version is installed!')
    activate_all_buttons()


# function for starting threats for installing / updating
def start_install_thread(button):
    if check_game_paths():
        # reinstall everything
        if button.cget('text') == 'Repair':
            approve_installation_repair = tkinter.messagebox.askyesno(title='Repair Submod',
                                                                    message='Do you want to download and install all submod files again?')
            if approve_installation_repair:
                deinstall_submod()
                threading.Thread(target=install_all, daemon=True).start()
        # update only new files
        if button.cget('text') == 'Update' or button.cget('text') == 'Install':
            approve_installation_update = tkinter.messagebox.askyesno(title='Update Submod',
                                                                message='Do you want to update the submod?')
            activate_existing_files()
            if approve_installation_update:
                threading.Thread(target=install_files, daemon=True).start()


# function from install_files for showing the download progress
def download_files_progressbar():
    while isDownloading:

        for temp_file in os.listdir(
                read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/edain_unchained_installation_temp'):
            if temp_file.startswith(fileDownloading):
                file_size = os.path.getsize(read_ini('launcher_options.ini', 'GAMEPATH',
                                                     'BFMEIIROTWK') + '/edain_unchained_installation_temp/' + temp_file)
                file_size = file_size / 1000000
                # print('FILE: ' + str(round(file_size, 2)))
                label_feedback.configure(
                    text='Downloading file: ' + fileDownloading + ' ' + str(round(file_size, 2)) + 'MB')

                # d = urllib.urlopen('https://drive.google.com/drive/folders/1eRUoa2Q3IhLnRtcyobv4RZvkGWhBNB7y')
                # print(d.info()['Content-Length'])
        time.sleep(1)


# deactiave all buttons while repair/updating
def deactivate_all_buttons():
    button_start_game['state'] = 'disabled'
    button_activate_submod['state'] = 'disabled'
    button_deactivate_submod['state'] = 'disabled'
    install_edain_unchained['state'] = 'disabled'
    check_for_updates['state'] = 'disabled'
    option_switch_language['state'] = 'disabled'


# activate all buttons after repair/updating
def activate_all_buttons():
    button_start_game['state'] = 'normal'
    button_activate_submod['state'] = 'normal'
    button_deactivate_submod['state'] = 'normal'
    install_edain_unchained['state'] = 'normal'
    check_for_updates['state'] = 'normal'
    option_switch_language['state'] = 'normal'


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
def start_game_thread():
    if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '\lotrbfme2ep1.exe'):
        label_feedback.configure(text='DESTROY YOUR ENEMY!')
        threading.Thread(target=start_game, daemon=True).start()
        close_window()
    else:
        label_feedback.configure(text='No lotrbfme2ep1.exe found!')
        print('Starting Application does not exist: ' + read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '\lotrbfme2ep1.exe')


def start_game():
    os.chdir(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK'))
    os.system('lotrbfme2ep1.exe')


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
                        print('File ' + filename + ' renamed: ' + filename + '.bak')

            write_ini('launcher_options.ini', 'SETTINGS', 'activated', 'False')
            label_feedback.configure(text='Submod is deactivated!')
            check_submod_activated()
        except OSError:
            file_number = 1
            file_exists = 1
            config = configparser.ConfigParser()
            config.read('launcher_options.ini')
            for (file, filename) in config.items('FILENAME'):
                file_number += 1
                if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak'):
                    file_exists += 1
            if file_number == file_exists:
                label_feedback.configure(text='Submod is already deactivated!')
            else:
                message = ''
                for (file, filename) in config.items('FILENAME'):
                    if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename):
                        os.rename(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename,
                                  read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak')
                    elif os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename) is False and os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak') is False:
                        message = message + '\n' + filename

                write_ini('launcher_options.ini', 'SETTINGS', 'activated', 'False')
                label_feedback.configure(text='Submod is deactivated!')
                check_submod_activated()
                print('Repair submod! Files are missing: ')
                print(message)


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
                    print('File ' + filename + '.bak renamed: ' + filename)

            write_ini('launcher_options.ini', 'SETTINGS', 'activated', 'True')
            check_language('BFMEIIROTWK')
            label_feedback.configure(text='Submod is activated!')
            check_submod_activated()
        except OSError:
            activate_existing_files()
            tkinter.messagebox.showwarning(title='Warning', message='Please repair the submod! \n\n Some files are missing!')


# activate all existing files
def activate_existing_files():
    file_number = 1
    file_exists = 1
    config = configparser.ConfigParser()
    config.read('launcher_options.ini')
    for (file, filename) in config.items('FILENAME'):
        file_number += 1
        if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename):
            file_exists += 1
    if file_number == file_exists:
        label_feedback.configure(text='Submod is already activated!')
    else:
        message = 'Files are missing: '
        for (file, filename) in config.items('FILENAME'):
            # find out which files are missing
            if not (os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename)):
                if os.path.exists(
                        read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak'):
                    os.rename(
                        read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename + '.bak',
                        read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/' + filename)
                    print('File ' + filename + '.bak renamed: ' + filename)
                else:
                    message = message + '\n' + filename + '.bak'
        label_feedback.configure(message)


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


# functions for redirecting terminal output to tkinter
def run():
    threading.Thread(target=test).start()


def test():
    print("Thread: start")

    # p = subprocess.Popen("ping -c 4 stackoverflow.com".split(), stdout=subprocess.PIPE, bufsize=1, text=True)
    p = subprocess.Popen("ping stackoverflow.com".split(), stdout=subprocess.PIPE, bufsize=1, text=True)
    while p.poll() is None:
        msg = p.stdout.readline().strip() # read a line from the process output
        if msg:
            print(msg)

    print("Thread: end")

# --------#
# classes #
# --------#


# class for redirecting terminal output to tkinter
class Redirect():
    def __init__(self, widget, autoscroll=True):
        self.widget = widget
        self.autoscroll = autoscroll

    def write(self, text):
        self.widget.insert('end', text)
        if self.autoscroll:
            self.widget.see("end")  # autoscroll

    #def flush(self):
    #    pass


# function for switching the language (english or german)
def switch_language(language):
    if language == 'German':
        write_ini('launcher_options.ini', 'SETTINGS', 'language', 'German')
    else:
        write_ini('launcher_options.ini', 'SETTINGS', 'language', 'English')
    check_language('BFMEIIROTWK')


# check current language and deactivate (rename) files
def check_language(location):
    current_language = read_ini('launcher_options.ini', 'SETTINGS', 'language')
    path_german_file = ''
    path_english_file = ''
    if location == 'BFMEIIROTWK':
        path_german_file = read_ini('launcher_options.ini', 'GAMEPATH', 'bfmeiirotwk') + '/' + read_ini('launcher_options.ini', 'FILENAME', 'eu_sounds_ger')
        path_english_file = read_ini('launcher_options.ini', 'GAMEPATH', 'bfmeiirotwk') + '/' + read_ini('launcher_options.ini', 'FILENAME', 'eu_sounds_eng')

    if location == 'edain_unchained_installation_temp' and os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'bfmeiirotwk') + '/edain_unchained_installation_temp'):
        path_german_file = read_ini('launcher_options.ini', 'GAMEPATH', 'bfmeiirotwk') + '/edain_unchained_installation_temp/' + read_ini('launcher_options.ini', 'FILENAME', 'eu_sounds_ger')
        path_english_file = read_ini('launcher_options.ini', 'GAMEPATH', 'bfmeiirotwk') + '/edain_unchained_installation_temp/' + read_ini('launcher_options.ini', 'FILENAME', 'eu_sounds_eng')

    # check if files exist double (activated and deactivated)
    if os.path.exists(path_german_file) and os.path.exists(path_german_file + '.bak'):
        if current_language == 'German':
            os.remove(path_german_file + '.bak')
        else:
            os.remove(path_german_file)

    if os.path.exists(path_english_file) and os.path.exists(path_english_file + '.bak'):
        if current_language == 'English':
            os.remove(path_english_file + '.bak')
        else:
            os.remove(path_english_file)

    # check if submod is activated and deactive files
    if read_ini('launcher_options.ini', 'SETTINGS', 'activated') == 'True':
        if current_language == 'German':
            if os.path.exists(path_english_file):
                os.rename(path_english_file, path_english_file + '.bak')
                print('File ' + read_ini('launcher_options.ini', 'FILENAME', 'eu_sounds_eng') + ' renamed: ' + read_ini('launcher_options.ini', 'FILENAME', 'eu_sounds_eng') + '.bak')
            if os.path.exists(path_german_file + '.bak'):
                os.rename(path_german_file + '.bak', path_german_file)
                print('File ' + read_ini('launcher_options.ini', 'FILENAME', 'eu_sounds_ger') + '.bak renamed: ' + read_ini(
                    'launcher_options.ini', 'FILENAME', 'eu_sounds_ger'))
        elif current_language == 'English':
            if os.path.exists(path_german_file):
                os.rename(path_german_file, path_german_file + '.bak')
                print('File ' + read_ini('launcher_options.ini', 'FILENAME', 'eu_sounds_ger') + ' renamed: ' + read_ini(
                    'launcher_options.ini', 'FILENAME', 'eu_sounds_ger') + '.bak')
            if os.path.exists(path_english_file + '.bak'):
                os.rename(path_english_file + '.bak', path_english_file)
                print('File ' + read_ini('launcher_options.ini', 'FILENAME',
                                         'eu_sounds_eng') + '.bak renamed: ' + read_ini(
                    'launcher_options.ini', 'FILENAME', 'eu_sounds_eng'))


# check if submod is activated and change label
def check_submod_activated():
    if read_ini('launcher_options.ini', 'SETTINGS', 'activated') == 'True':
        eu_label.configure(text='Edain Unchained')
        eu_version_label.configure(text='Version: ' + read_ini('launcher_options.ini', 'MODINFO', 'edain_unchained_version'))
    else:
        eu_label.configure(text='Edain Mod')
        eu_version_label.configure(text='')


# functions for opening web-link
def open_link_discord():
    webbrowser.open_new_tab(read_ini('launcher_options.ini', 'LINKS', 'discord'))


def open_link_youtube():
    webbrowser.open_new_tab(read_ini('launcher_options.ini', 'LINKS', 'youtube'))


def open_link_patchnotes():
    if read_ini('launcher_options.ini', 'SETTINGS', 'language') == 'English':
        webbrowser.open_new_tab(read_ini('launcher_options.ini', 'LINKS', 'patchnotes_eng'))
    else:
        webbrowser.open_new_tab(read_ini('launcher_options.ini', 'LINKS', 'patchnotes_ger'))


def open_link_factionplan_harad():
    if read_ini('launcher_options.ini', 'SETTINGS', 'language') == 'English':
        webbrowser.open_new_tab(read_ini('launcher_options.ini', 'LINKS', 'factionplan_harad_eng'))
    else:
        webbrowser.open_new_tab(read_ini('launcher_options.ini', 'LINKS', 'factionplan_harad_ger'))


# read the gamepaths from registry
def registry_read_paths():
    if read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII') == '':
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
            with winreg.OpenKey(hkey,
                                "SOFTWARE\WOW6432Node\Electronic Arts\Electronic Arts\The Battle for Middle-earth II",
                                0, winreg.KEY_READ) as sub_key:
                if winreg.EnumValue(sub_key, 1)[0] == "InstallPath":
                    bfme2_path_value = winreg.EnumValue(sub_key, 1)[1]
                    write_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII', bfme2_path_value)

    if read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') == '':
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
            with winreg.OpenKey(hkey,
                                "SOFTWARE\WOW6432Node\Electronic Arts\Electronic Arts\The Lord of the Rings, The Rise of the Witch-king",
                                0, winreg.KEY_READ) as sub_key:
                if winreg.EnumValue(sub_key, 1)[0] == "InstallPath":
                    rotwk_path_value = winreg.EnumValue(sub_key, 1)[1]
                    write_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK', rotwk_path_value)


def bfmeii_path_reset():
    write_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII', '')
    registry_read_paths()
    bfmeII_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII'))
    is_installed()


def bfmeiirowtk_path_reset():
    write_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK', '')
    registry_read_paths()
    bfmeIIrotwk_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK'))
    is_installed()


# check if submod is already installed and change label
def is_installed():
    if os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK')
                          + '/' + read_ini('launcher_options.ini', 'FILENAME', 'EU_DATA')) \
                          or os.path.exists(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK')
                          + '/' + read_ini('launcher_options.ini', 'FILENAME', 'EU_DATA') + '.bak'):
        check_for_updates.configure(text='Update')
    else:
        check_for_updates.configure(text='Install')


# delete submod files
def deinstall_submod():
    temp = read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK') + '/*_Edain_Unchained_*'
    for files in glob.glob(temp):
        os.remove(files)
        print('File deleted: ' + files)

    is_installed()
    write_ini('launcher_options.ini', 'SETTINGS', 'ACTIVATED', 'FALSE')
    check_submod_activated()
    label_feedback.configure(text='Submod is deinstalled!')
    # tkinter.messagebox.showinfo(title='Deinstallation', message='Please check for updated with the Edain Mod Launcher!')


# open new window for the settings
def create_toplevel():
    global bfmeII_path_label
    global bfmeIIrotwk_path_label
    window_options = customtkinter.CTkToplevel()
    window_options.title('Options')
    window_options.geometry("800x260")

    # label select your BFME II path
    bfmeii_select_label = tkinter.StringVar()
    select_bfmeii_path = customtkinter.CTkLabel(window_options, textvariable=bfmeii_select_label, height=1,)
    bfmeii_select_label.set('Select your custom installation path: BFME 2')
    select_bfmeii_path.grid(row=0, column=0, pady=10, padx=20, )

    # button browse path for BFME II
    browse_path_bfmeii = tkinter.Button(window_options, text='Browse BFME2 path', width=15, height=1, )
    browse_path_bfmeii.configure(command=lambda button=browse_path_bfmeii: open_directory(button))
    browse_path_bfmeii.grid(row=1, column=0, pady=10, padx=20)

    # button reset BFME II path
    reset_bfmeii_path = tkinter.Button(window_options, text='Reset', width=10, height=1, command=bfmeii_path_reset)
    reset_bfmeii_path.grid(row=1, column=1, pady=10, padx=20)

    # label for bfmeii current path
    bfmeII_path_label = tkinter.StringVar()
    label_bfmeii = customtkinter.CTkLabel(window_options, textvariable=bfmeII_path_label, height=1, )
    bfmeII_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEII'))
    label_bfmeii.grid(row=1, column=2, pady=10, padx=20, )

    # label select your BFME II ROTWK path
    bfmeiirotwk_select_label = tkinter.StringVar()
    select_bfmeiirotwk_path = customtkinter.CTkLabel(window_options, textvariable=bfmeiirotwk_select_label, height=1, )
    bfmeiirotwk_select_label.set('Select your custom installation path: BFME 2')
    select_bfmeiirotwk_path.grid(row=2, column=0, pady=10, padx=20, )

    # button browse path for BFME II ROTWK
    browse_path_bfmeiirotwk = tkinter.Button(window_options, text='Browse ROTWK path', width=15, height=1, )
    browse_path_bfmeiirotwk.configure(command=lambda button=browse_path_bfmeiirotwk: open_directory(button))
    browse_path_bfmeiirotwk.grid(row=3, column=0, pady=10, padx=20)

    # button reset BFME II ROTWK path
    reset_bfmeiirowtk_path = tkinter.Button(window_options, text='Reset', width=10, height=1, command=bfmeiirowtk_path_reset)
    reset_bfmeiirowtk_path.grid(row=3, column=1, pady=10, padx=20)

    # label for bfmeiirotwk current path
    bfmeIIrotwk_path_label = tkinter.StringVar()
    label_bfmeiirotwk = customtkinter.CTkLabel(window_options, textvariable=bfmeIIrotwk_path_label, height=1, )
    bfmeIIrotwk_path_label.set(read_ini('launcher_options.ini', 'GAMEPATH', 'BFMEIIROTWK'))
    label_bfmeiirotwk.grid(row=3, column=2, pady=10, padx=20)

    # label select your BFME II ROTWK path
    deinstall_submod_var = tkinter.StringVar()
    deinstall_submod_label = customtkinter.CTkLabel(window_options, textvariable=deinstall_submod_var, height=1, )
    deinstall_submod_var.set('Deinstall all submod files from the current path')
    deinstall_submod_label.grid(row=4, column=0, pady=10, padx=20, )

    # button deinstall submod
    deinstall_submod_button = tkinter.Button(window_options, text='Deinstall', width=15, height=1,
                                            command=deinstall_submod)
    deinstall_submod_button.grid(row=5, column=0, pady=10, padx=20)


# show and hide the console output
def console_output():

    print("switch toggled, current value:", switch_var.get())
    switch_val = switch_var.get()

    if switch_val == "Show":
        main.geometry('1280x920')
        text.configure(height=40)
        frame.grid(row=2, column=0, sticky='ew', padx=15, pady=(0, 10))

    if switch_val == "Hide":
        main.geometry('980x520')
        frame.grid_forget()


# --------------------------#
# main window with buttons #
# --------------------------#

# main application window
main = customtkinter.CTk()
main.geometry('980x520')
main.title('Edain Unchained Launcher')
main.iconbitmap('launcherIcon.ico')
# photo = tkinter.PhotoImage(file='launcherIcon.png')
# main.iconphoto(False, photo)

# ============ create two frames ============

# configure grid layout (3x1)
main.grid_rowconfigure(0, weight=1)
main.grid_columnconfigure(1, weight=1)

frame_left = customtkinter.CTkFrame(master=main, width=180, corner_radius=0)
frame_left.grid(row=0, column=0, sticky='nswe')

frame_middle = customtkinter.CTkFrame(master=main)
frame_middle.grid(row=0, column=1, sticky='nswe', padx=20, pady=20)

frame_right = customtkinter.CTkFrame(master=main, width=180, corner_radius=0)
frame_right.grid(row=0, column=2, sticky='nswe')

# ============ frame_right ============

# configure grid layout (1x11)
frame_right.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing (top)
frame_right.grid_rowconfigure(4, minsize=20)  # empty row with minsize as spacing (middle)
frame_right.grid_rowconfigure(9, weight=1)  # empty row as spacing (Options is at bottom)
frame_right.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing (bottom)

# button discord-link
button_link_discord = customtkinter.CTkButton(frame_right, text='Discord', command=open_link_discord)
button_link_discord.grid(row=2, column=0, pady=10, padx=20)

# button youtube-link
button_link_youtube = customtkinter.CTkButton(frame_right, text='Youtube', command=open_link_youtube)
button_link_youtube.grid(row=3, column=0, pady=10, padx=20)

# button patchnotes-link
button_link_patchnotes = customtkinter.CTkButton(frame_right, text='Patchnotes', command=open_link_patchnotes)
button_link_patchnotes.grid(row=5, column=0, pady=10, padx=20)

# button factionplan_harad-link
button_link_factionplan_harad = customtkinter.CTkButton(frame_right, text='Factionplan Harad', command=open_link_factionplan_harad)
button_link_factionplan_harad.grid(row=6, column=0, pady=10, padx=20)

# button open new Options window
button_open_options = customtkinter.CTkButton(frame_right, text='Options', command=create_toplevel)
button_open_options.grid(row=10, column=0, pady=10, padx=20)

# ============ frame_left ============

# configure grid layout (1x11)
frame_left.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing (top)
frame_left.grid_rowconfigure(3, minsize=20)  # empty row with minsize as spacing (after eu_label)
frame_left.grid_rowconfigure(6, weight=1)  # empty row as spacing (Appearance Mode is at bottom)
frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing (bottom)

# edain unchained label
eu_label = customtkinter.CTkLabel(frame_left, text='Edain Unchained', text_font=("Ringbearer", 16))
eu_label.grid(row=1, column=0, pady=10, padx=10)

# edain unchained version label
eu_version_label = customtkinter.CTkLabel(frame_left, text_font=("Ringbearer", 12))
eu_version_label.configure(text='Version ' + read_ini('launcher_options.ini', 'MODINFO', 'edain_unchained_version'))
eu_version_label.grid(row=2, column=0, pady=10, padx=10)
check_submod_activated()

# button start game
button_start_game = customtkinter.CTkButton(frame_left, text='Start game', command=start_game_thread)
button_start_game.grid(row=6, column=0, pady=10, padx=20)

# button deactivate submod
button_deactivate_submod = customtkinter.CTkButton(frame_left, text='deactivate submod', command=deactivate_submod)
button_deactivate_submod.grid(row=3, column=0, pady=10, padx=20)

# button activate submod
button_activate_submod = customtkinter.CTkButton(frame_left, text='activate submod', command=activate_submod)
button_activate_submod.grid(row=4, column=0, pady=10, padx=20)


# button to test terminal output
button_terminal_test = customtkinter.CTkButton(frame_left, text='test terminal', command=run)
# button_terminal_test.grid(row=5, column=0, pady=10, padx=20)

# label for switch language
label_switch_language = customtkinter.CTkLabel(frame_left, text='Game language:')
label_switch_language.grid(row=7, column=0, pady=0, padx=20)

# switch language
option_switch_language = customtkinter.CTkOptionMenu(frame_left, values=['German', 'English'], command=switch_language)
option_switch_language.grid(row=8, column=0, pady=0, padx=20)
option_switch_language.set(read_ini('launcher_options.ini', 'SETTINGS', 'language'))

# ============ frame_middle ============

# configure grid layout (1x7)
frame_middle.rowconfigure(3, weight=1)
frame_middle.rowconfigure(5, weight=1)
frame_middle.columnconfigure(0, weight=1)

frame_update = customtkinter.CTkFrame(master=frame_middle)
frame_update.grid(row=3, column=0, columnspan=2, rowspan=2, pady=20, padx=20, sticky='nsew')
frame_update.grid_rowconfigure(0, weight=1)
frame_update.grid_rowconfigure(1, weight=1)
frame_update.grid_columnconfigure(0, weight=1)

frame_feedback = customtkinter.CTkFrame(master=frame_middle)
frame_feedback.grid(row=5, column=0, columnspan=1, rowspan=2, pady=20, padx=20, sticky='nsew')
frame_feedback.grid_rowconfigure(0, weight=1)
frame_feedback.grid_rowconfigure(1, weight=1)
frame_feedback.grid_columnconfigure(0, weight=1)

# button install edain unchained submod
install_edain_unchained = tkinter.Button(frame_update, text='Repair', width=20, height=2)
install_edain_unchained.configure(command=lambda button=install_edain_unchained: start_install_thread(button))
install_edain_unchained.grid(row=0, column=0, pady=0, padx=20)

# label install
install_edain_unchained_label = customtkinter.CTkLabel(frame_update, text='Reinstall the mod')
install_edain_unchained_label.grid(row=0, column=1, pady=10, padx=20)

# button check for updates
check_for_updates = tkinter.Button(frame_update, text='Update', width=20, height=2)
check_for_updates.configure(command=lambda button=check_for_updates: start_install_thread(button))
check_for_updates.grid(row=1, column=0, pady=0, padx=20)

# label update
label_update = customtkinter.CTkLabel(frame_update, text='Update to the latest version')
label_update.grid(row=1, column=1, pady=10, padx=20)

# feedback label
label_feedback = customtkinter.CTkLabel(frame_feedback, text_font='BOLD')
label_feedback.configure(text='Do something!')
label_feedback.grid(row=0, column=0, pady=0, padx=15, sticky='ew')

# terminal output as progressbar
global frame
frame = customtkinter.CTkFrame(frame_feedback)
# frame.pack(expand=True, fill='both')
global text
text = tkinter.Listbox(frame, height=6, selectmode='multiple')
text.pack(side='left', fill='both', expand=True)

switch_var = customtkinter.StringVar(value="Hide")
console_switch = customtkinter.CTkSwitch(frame_feedback, text="Console", command=console_output,variable=switch_var, onvalue="Show", offvalue="Hide")
console_switch.grid(row=1, column=0)

registry_read_paths()
is_installed()

scrollbar = tkinter.Scrollbar(frame)
scrollbar.pack(side='right', fill='y')
text['yscrollcommand'] = scrollbar.set
scrollbar['command'] = text.yview

old_stdout = sys.stdout
sys.stdout = Redirect(text)
sys.stderr = Redirect(text)

# loop for main application window
main.mainloop()

# after closing window
sys.stdout = old_stdout