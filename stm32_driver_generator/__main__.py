import os
import sys
import json
from . import hardware_configs
from . import code_c_parser
from . import file_operations

target_folders_list = ['Inc', 'Src']
target_ext_list = ['.ioc', '.ld']

allowed_interfaces = ['spi','i2c']


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
    print('Project: ' + project_name)
    project_dir = path_to_boards_dir + '\\' + project_name
    
    # ищем в корневой папке подпапке заголовков и исходного кода
    is_subfolders_found = True
    project_dir_core = ''
    subfolders_list = os.listdir(project_dir)
    for one_trg_fld in target_folders_list:
        src_files = one_trg_fld
        if src_files not in subfolders_list:
            print('There is no ' + src_files + ' in root folder!')
            is_subfolders_found = False
    if not is_subfolders_found:
        is_subfolders_found = True
        project_dir_core = project_dir + '\\Core'
        subfolders_list = os.listdir(project_dir_core)
        for one_trg_fld in target_folders_list:
            src_files = one_trg_fld
            if src_files not in subfolders_list:
                print('There is no ' + src_files + ' in Core folder!')
                is_subfolders_found = False

    if project_dir_core:
        print('Target code is Core subfolder')
    if is_subfolders_found:
        print('Folders is checked: ' + str(subfolders_list))
    else:
        print('Have no data folders')
        sys.exit()
    print('Project directory: ' + project_dir)
    # проверяем файлы
    
    target_files_list = []
    for one_trg_ext in target_ext_list:
        one_trg_ext_is_found = False
        for one_elem in os.listdir(project_dir):
            filepath = project_dir + '\\' + one_elem
            if not os.path.isdir(filepath):
                filename, fileext = os.path.splitext(filepath)
                if fileext == one_trg_ext:
                    print('working with ' + filepath)
                    one_trg_ext_is_found = True
                    target_files_list.append(filepath)
        if not one_trg_ext_is_found:
            print('can\'t find file with ' + one_trg_ext + ' extension in ' +filepath )
            sys.exit()

    project_data = {}
    project_data['name'] = project_name
    for target_file in target_files_list:
        if target_file.endswith('.ioc'):
            project_data['mcu'] = hardware_configs.getMcuFlagFrom_ioc(target_file)
            project_data['clock'] = hardware_configs.getSysClkFrom_ioc(target_file)
            project_data['dma'] = hardware_configs.getDmaParams(target_file)

    
    
    #проверяем конфигурационные файлы для проекта плат
    trg_project_dir = ''
    if not project_dir_core:
        objects_list = os.listdir(project_dir + '\\Inc' )
        trg_project_dir = project_dir
    else:
        objects_list = os.listdir(project_dir_core + '\\Inc' )
        trg_project_dir = project_dir_core

    interface_list = {}
    print('Available files: ' + str(objects_list))
    for one_object in objects_list:
        target_interface_file, trg_ext = os.path.splitext(one_object)
        if target_interface_file in allowed_interfaces:
            interface_count = hardware_configs.getInterfaceCount(trg_project_dir, target_interface_file)
            # print('Have ' + str(interface_count) + ' ' + target_interface_file)
            interface_list[target_interface_file] = interface_count
    project_data['interface_list'] = interface_list

    filepath = trg_project_dir + '\\Inc\\main.h'
    main_includes = code_c_parser.getIncludesC(filepath)

    # создаем папку хранения проектов
    platform_dir = path_to_project_dir + '\\platform'
    print('target folder: ' + platform_dir)
    if not os.path.exists(platform_dir):
        os.mkdir(platform_dir)

    # создаем папку для текущего проекта
    current_project_dir = platform_dir + '\\' + project_name
    print('project dir: ' + current_project_dir)
    if not os.path.exists(current_project_dir):
        os.mkdir(current_project_dir)

    # создаем папку шаблонов
    templates_dir = current_project_dir + '\\templates'
    print('templates dir: ' + templates_dir)
    if not os.path.exists(templates_dir):
        os.mkdir(templates_dir)

    init_templates_dir = templates_dir + '\\init'
    print('init templates dir: ' + init_templates_dir)
    if not os.path.exists(init_templates_dir):
        os.mkdir(init_templates_dir)

    # создаем папку для системных файлов

    sys_dir = current_project_dir + '\\sys'
    if not os.path.exists(sys_dir):
        os.mkdir(sys_dir)
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    # 

    sys_init_path = file_operations.findFileInFolder(trg_project_dir,'system_' + (project_data['mcu'][:len('stm32fx')]).lower() + 'xx',fileext='.c')
    if not sys_init_path:
        print('Can\'t find sys file!')
        sys.exit()
    else:
        print('System init file: ' + sys_init_path[0])

    arch_src_path = file_operations.findFileInFolder(trg_project_dir, 'main', '.c')
    if not arch_src_path:
        print('Can\'t find arch file!')
        sys.exit()
    else:
        print('Arch file: ' + arch_src_path[0])

    paths = {}
    paths['path_to_driver'] = path_to_project_dir + '\\drivers\\sys.c'
    paths['path_to_cubesrc'] = arch_src_path[0]
    arch_fun = code_c_parser.getArchFunC(paths, project_data['mcu'])
    code_c_parser.saveToFileC(sys_dir, 'arch',arch_fun)

    file_operations.copySrcToDst(sys_init_path[0], current_project_dir + '\\sys\\' + sys_init_path[0].split('\\')[-1])
    mybuild = code_c_parser.genSysMybuild(sys_dir, project_data['mcu'], folder=current_project_dir.split('\\')[-1])
    code_c_parser.saveToMybuild(sys_dir,mybuild)


    for interface_type in project_data['interface_list']:
        print(interface_type)
        filepath = trg_project_dir + '\\Src\\' + interface_type +'.c'
        interface_type_list = project_data['interface_list'][interface_type]
        for interface in interface_type_list:
            interface_dir = current_project_dir + '\\' + interface_type + '_gen'
            print('interface dir: ' + interface_dir)
            if not os.path.exists(interface_dir):
                os.mkdir(interface_dir) 
            driver_path = path_to_project_dir + '\\drivers\\' + interface_type + '.c'
            if not os.path.exists(driver_path):
                with open(driver_path, 'w'):
                    pass
            if interface.upper() in project_data['dma']:
                print (project_data['dma'][interface.upper()])
                dma_body = code_c_parser.getFunctionC(filepath, 'dma')
                function_body = main_includes + code_c_parser.getInterfaceInitBlockC(driver_path, interface_type, interface, is_dma=1)

                path_to_halsrc = filepath
                path_to_interface_driver = driver_path
                path_to_hal = project_dir + '\\Drivers\\CMSIS\\Device\\ST\\' + project_data['mcu'][:len('STM32Fx')] + 'xx\\Include\\' 
                if project_data['mcu'] == 'STM32F103xB':
                    path_to_hal = path_to_hal + 'stm32f103xb.h'
                else:
                    path_to_hal = path_to_hal + project_data['mcu'][:len('stm32fxxx')].lower() + 'xx.h'
                
                print(path_to_halsrc)
                print(path_to_interface_driver)
                print('path to HAL: ' + path_to_hal)
                print(project_data['dma'])
                function_body = function_body + code_c_parser.updateInterfaceFromDMA(path_to_halsrc, path_to_interface_driver, path_to_hal, interface_type, interface, project_data['dma'][interface.upper()])

                externC, externH = code_c_parser.updateExternFunFromDMA(path_to_interface_driver, interface_type, interface, project_data['dma'][interface.upper()])
                function_body = function_body + externC
                code_c_parser.saveToFileC(interface_dir, interface, function_body)
                code_c_parser.saveToFileH(interface_dir, interface, externH)
            else:
                path_array = {}
                path_array['path_to_driver'] = driver_path
                path_array['path_to_src'] = filepath

                function_body, header_body = code_c_parser.updateInterface(path_array, interface_type, interface)
                function_body = main_includes + function_body
                code_c_parser.saveToFileC(interface_dir, interface, function_body)
                code_c_parser.saveToFileH(interface_dir, interface, header_body)
        mybuild = code_c_parser.genBaseMybuild(interface_dir, project_data, folder=current_project_dir.split('\\')[-1])
        code_c_parser.saveToMybuild(interface_dir,mybuild)
        print(mybuild)
            # print(function_body)

    template_files = []
    template_files.append('board.conf.h')
    template_files.append('build.conf')
    template_files.append('lds.conf')
    template_files.append('mods.conf')
    template_files.append('start_script.inc')
    src_template_dir = path_to_project_dir + '\\templates\\' + project_data['mcu'][:len('stm32fx')].lower() + 'x\\'
    for template in template_files:
        if os.path.exists(src_template_dir + template):
            file_operations.copySrcToDst(src_template_dir + template, init_templates_dir + '\\' + template)
            code_c_parser.openAndReplaceTemplates(init_templates_dir + '\\' + template, project_data)


    print(project_data)
    #     if one_object == 'spi.h':
    #         spi_interface = hardware_configs.getInterfaceCount(project_dir, 'spi')
    #         if spi_interface:
    #             interface_list['spi'] = spi_interface
    #         if one_object == 'i2c.h':
    #             i2c_interface = hardware_configs.getInterfaceCount(project_dir, 'i2c')
    #             if i2c_interface:
    #                 interface_list['i2c'] = i2c_interface
    #     project_data['interfaces'] = interface_list
    #     # with open(project_json, 'w') as target:
    #         # json.dump(project_data, target, sort_keys=True, indent=4)
    # print(project_data)

    # работаем с исходным кодом
    # project_drivers_dir = path_to_drivers_dir + '\\' + project_name

    # if not os.path.exists(project_drivers_dir):
    #     os.mkdir(project_drivers_dir)
    # перебираем датчики для работы

    # sensor_list = project_data['sensors']
    # interface_list = project_data['interfaces']
    # for sensor_type in sensor_list:
    #     sns_interface = sensor_list[sensor_type]['interface']
    #     sns_interface_type = sns_interface[:(len(sns_interface)-1)]
    #     if interface_list[sns_interface_type ][sns_interface] == 'enabled':
    #         sensor_drivers_dir = project_drivers_dir + '\\' + sensor_type.lower()
    #         # создаем директорию
    #         if not os.path.exists(sensor_drivers_dir):
    #             os.mkdir(sensor_drivers_dir)


    #         # получаем исходный код интерфейсов
    #         path_to_interface_src = path_to_boards_dir + '\\' + project_name + '\\Src\\'
    #         fun_body = code_c_parser.getFunctionC( path_to_interface_src, sns_interface )

    #         sensor_file_name = (project_name + '_' + sensor_type + '_' + sns_interface_type).lower()

    #         fun_body = code_c_parser.modifyFunHeader(sensor_file_name, fun_body)
    #         header_body = []

    #         header_body = code_c_parser.addIncludeForHeader(project_data['mcu'],sns_interface_type,header_body)
    #         if 'cmds_list' in sensor_list[sensor_type]:
    #             fun_body = code_c_parser.addStdCmdShell(sensor_list[sensor_type]['cmds_list'],sensor_file_name, fun_body)
    #             header_body = code_c_parser.addStdCmdHeader(sensor_list[sensor_type]['cmds_list'],sensor_file_name, header_body)
    #         fun_body = code_c_parser.addStruct(sensor_file_name, sns_interface_type, fun_body)

            
    #         fun_body = code_c_parser.addIncludeForSrc(sensor_file_name, fun_body)

    #         mybuild_body = code_c_parser.genBaseMybuild(sensor_drivers_dir,project_data['mcu'])

            # code_c_parser.saveToFileC(sensor_drivers_dir, sensor_file_name, fun_body)
            # code_c_parser.saveToFileH(sensor_drivers_dir, sensor_file_name, header_body)
            # code_c_parser.saveToMybuild(sensor_drivers_dir,mybuild_body)

            # загружаем драйвера для сенсоров

