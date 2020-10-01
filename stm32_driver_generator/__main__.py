import os
import sys
import json
from . import hardware_configs
from . import code_c_parser

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
path_to_drivers_dir = path_to_project_dir + '\\board_drivers'

if not os.path.exists(path_to_drivers_dir):
    os.mkdir(path_to_drivers_dir)

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
        print('load data from ' + project_json)
        with open(project_json, 'r', encoding='utf-8') as source:
            project_data = json.loads(source.read())
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
        project_data['interfaces'] = interface_list
        for target_file in target_files_list:
            if target_file.endswith('.ioc'):
                snsr = hardware_configs.getSensorsFrom_ioc(target_file)
                if snsr:
                    project_data['sensors'] = snsr
                project_data['mcu'] = hardware_configs.getMcuFlagFrom_ioc(target_file)
                project_data['clock'] = hardware_configs.getSysClkFrom_ioc(target_file)
        with open(project_json, 'w') as target:
            json.dump(project_data, target, sort_keys=True, indent=4)
    print(project_data)

    # работаем с исходным кодом
    project_drivers_dir = path_to_drivers_dir + '\\' + project_name

    if not os.path.exists(project_drivers_dir):
        os.mkdir(project_drivers_dir)
    # перебираем датчики для работы

    sensor_list = project_data['sensors']
    interface_list = project_data['interfaces']
    for sensor_type in sensor_list:
        sns_interface = sensor_list[sensor_type]['interface']
        sns_interface_type = sns_interface[:(len(sns_interface)-1)]
        if interface_list[sns_interface_type ][sns_interface] == 'enabled':
            sensor_drivers_dir = project_drivers_dir + '\\' + sensor_type.lower()
            # создаем директорию
            if not os.path.exists(sensor_drivers_dir):
                os.mkdir(sensor_drivers_dir)


            # получаем исходный код интерфейсов
            path_to_interface_src = path_to_boards_dir + '\\' + project_name + '\\Src\\'
            fun_body = code_c_parser.getFunctionC( path_to_interface_src, sns_interface )

            sensor_file_name = (project_name + '_' + sensor_type + '_' + sns_interface_type).lower()

            fun_body = code_c_parser.modifyFunHeader(sensor_file_name, fun_body)
            fun_body = code_c_parser.addStruct(sensor_file_name, sns_interface_type, fun_body)
            
            code_c_parser.saveToFileC(sensor_drivers_dir, sensor_file_name, fun_body)

            # загружаем драйвера для сенсоров

