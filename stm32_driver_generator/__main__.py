import os
import sys
import json
from . import hardware_configs

target_folders_list = ['Inc', 'Src']
target_ext_list = ['.ioc', '.ld']


path_to_project_dir = os.getcwd()

print('target directory: ' + path_to_project_dir)

projects_list = []

path_to_boards_dir = path_to_project_dir + '\\board_projects'

print('target os type: ' + os.name)
if os.name == 'nt':
    projects_list = os.listdir(path_to_boards_dir)
    print('target project list: ' + str(projects_list))
else:
    print('unsupported os')
    sys.exit()

# проверяем наличие папки для конфигураций json
path_to_board_configs = path_to_project_dir + '\\board_configs'
if os.path.exists(path_to_board_configs):
    print('target config folder: ' + path_to_board_configs)
else:
    os.mkdir(path_to_board_configs)

for one_project in projects_list:
    #проверяем проекты плат
    project_name = one_project
    project_dir = path_to_boards_dir + '\\' + project_name
    subfolders_list = os.listdir(project_dir)
    for one_trg_fld in target_folders_list:
        src_files = one_trg_fld
        if src_files not in subfolders_list:
            print('There is no ' + src_files + ' in folder!')
            sys.exit()
    target_files_list = []
    for one_trg_ext in target_ext_list:
        one_trg_ext_is_found = False
        for one_elem in subfolders_list:
            filepath = project_dir + '\\' + one_elem
            if not os.path.isdir(filepath):
                filename, fileext = os.path.splitext(filepath)
                if fileext == one_trg_ext:
                    print('working with ' + filepath)
                    one_trg_ext_is_found = True
                    target_files_list.append(filepath)
        if not one_trg_ext_is_found:
            print('can\'t find file with ' + one_trg_ext + ' extension' )
            sys.exit()

    #проверяем конфигурационные файлы для проекта плат
    project_json = path_to_board_configs + '\\' + project_name + '.json'
    project_data = {}
    if (os.path.exists(project_json)):
        with open(path_to_board_configs, 'r') as source:
            project_data = json.loads(source)
    else:
        objects_list = os.listdir(project_dir + '\\Inc' )
        interface_list = {}
        for one_object in objects_list:
            if one_object == 'spi.h':
                spi_interface = hardware_configs.getInterfaceCount(project_dir, 'spi')
                if spi_interface:
                    interface_list['spi'] = spi_interface
            if one_object == 'i2c.h':
                i2c_interface = hardware_configs.getInterfaceCount(project_dir, 'i2c')
                if i2c_interface:
                    interface_list['i2c'] = i2c_interface
        print(hardware_configs.getDataFrom_ioc(target_files_list[0], 'Mcu.Name='))
        print(hardware_configs.getSensorsFrom_ioc(target_files_list[0]))
        print(hardware_configs.getMcuFlagFrom_ioc(target_files_list[0]))
        print(hardware_configs.getSysClkFrom_ioc(target_files_list[0]))
        print(interface_list)

