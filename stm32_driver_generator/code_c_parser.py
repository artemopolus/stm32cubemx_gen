import sys
import os
import re

def getArchFunC(paths, mcu):
    path_to_driver = paths['path_to_driver']
    path_to_cubesrc = paths['path_to_cubesrc']
    funs_list = []
    funs_list.append('Error_Handler')
    funs_list.append('arch_init')
    funs_list.append('arch_idle')
    funs_list.append('arch_shutdown')
    funs_list.append('HAL_GetTick')
    labels = {}
    labels['stm32xx'] = mcu[:len('stm32xx')].lower()
    headers = getFunctionC(path_to_driver,'sys', is_cubemx=0, str_label='sys_init')
    del headers[0]
    del headers[0]
    del headers[-1]

    headers = replaceTextUsingLabels(headers, labels)

    fun_body = []
    for function in funs_list:
        fun_body = fun_body + getFunctionC(path_to_driver, 'sys', is_cubemx=0, str_label=function)

    clock_body = getFunctionC(path_to_cubesrc, 'main', is_cubemx=0, str_label='SystemClock_Config')

    output = headers + [clock_body[0] + ';'] + fun_body + clock_body
    return output

def getInterfaceInitBlockC(path, interface_type, interface, is_dma = 0):
    trg_label = interface + '_full_base'
    start_header = ['#include \"' + interface + '_generated.h\"']
    if is_dma:
        trg_label = interface_type.lower() + '_full_dma_init'
        fun_body = getFunctionC(path, interface_type, is_cubemx=0, str_label=trg_label)
        inserted_name = (interface.lower() + '_full_dma').upper()
        ret_body = []
        for line in fun_body:
            _trg_label = 'name'
            new = line.replace('name',inserted_name)
            ret_body.append(new)
        if ret_body:
            del ret_body[0]
            del ret_body[0]
            del ret_body[-1]
        ret_body = start_header + ret_body

        return ret_body
    else:
        return []

def openAndReplaceTemplates(path, project_data):
    labels = {}
    labels['mcuflag'] = project_data['mcu']
    labels['name'] = project_data['name']
    openAndReplaceUsingLabels(path, labels)

def openAndReplaceUsingLabels(path, labels):
    code_lines = []
    with open(path, 'r') as src:
        code_lines = src.read().splitlines()
    code_lines = replaceTextUsingLabels(code_lines, labels)
    with open(path,'w') as trg:
        trg.write('\n'.join(code_lines))
 

def replaceTextUsingLabels(text, labels):
    out = []
    for line in text:
        result = line
        for label in labels:
            result = result.replace(label, labels[label])
        out.append(result)
    return out

def updateExternFunFromDMA(path_to_driver, interface_type, interface, dma_list, add_label = '_full'):
    dmax_label = dma_list['TX'][:len('DMAx')]
    ll_dma_channel_tx = 'LL_' + dmax_label[:-1] + '_' + dma_list['TX'].split('_')[1]
    num = ll_dma_channel_tx[-1]
    ll_dma_channel_tx = ll_dma_channel_tx[:-1]
    ll_dma_channel_tx = ll_dma_channel_tx + '_' + num
    ll_dma_channel_rx = 'LL_' + dmax_label[:-1] + '_' + dma_list['RX'].split('_')[1]
    num = ll_dma_channel_rx[-1]
    ll_dma_channel_rx = ll_dma_channel_rx[:-1]
    ll_dma_channel_rx = ll_dma_channel_rx + '_' + num

    labels = {}
    labels['DMAx'] = dmax_label
    labels['LL_DMA_CHANNEL_Tx'] = ll_dma_channel_tx
    labels['LL_DMA_CHANNEL_Rx'] = ll_dma_channel_rx
    labels[interface_type.upper() + 'x'] = interface.upper()
    transmit_fun_pt = interface_type + add_label + '_dma_transmit'
    receive_fun_pt = interface_type + add_label + '_dma_receive'
    setdatalength_fun_pt = interface_type + add_label + '_dma_setdatalength'
    labels[transmit_fun_pt] = (interface + add_label + '_dma').upper() + '_transmit'
    labels[receive_fun_pt] = (interface + add_label + '_dma').upper() + '_receive'
    labels[setdatalength_fun_pt] = (interface + add_label + '_dma').upper() + '_setdatalength'
    labels['name'] = (interface_type + add_label + '_dma').upper()

    fun_body = []
    head_body = []
    add_fun = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=transmit_fun_pt)
    if add_fun:
        head_body.append('extern ' + add_fun[0] + ';')
    fun_body = replaceTextUsingLabels(add_fun, labels)
    add_fun = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=receive_fun_pt)
    if add_fun:
        head_body.append('extern ' + add_fun[0] + ';')
    fun_body = fun_body + replaceTextUsingLabels(add_fun, labels)
    add_fun = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=setdatalength_fun_pt)
    if add_fun:
        head_body.append('extern ' + add_fun[0] + ';')
    fun_body = fun_body + replaceTextUsingLabels(add_fun, labels)

    return fun_body, head_body

def updateInterface(paths, interface_type, interface, add_label = '_base'):
    start_header = ['#include \"' + interface + '_generated.h\"']

    out_fun = []
    labels = {}
    path_to_src = paths['path_to_src']
    path_to_driver = paths['path_to_driver']
    labels[interface_type.upper() + 'x'] = interface.upper()
    hal_fun_body = getFunctionC(path_to_src, interface)
    target_name = ''
    if interface_type.lower() == 'spi':
        for line in hal_fun_body:
            if line.find('SPI_InitStruct.TransferDirection') != -1:
                if line.find('LL_SPI_FULL_DUPLEX') != -1:
                    target_name = target_name + '_full'
                if line.find('LL_SPI_HALF_DUPLEX') != -1:
                    target_name = target_name + '_half'
    pointer_name = (interface_type + target_name + add_label).lower()
    target_name = (interface + target_name + add_label).upper()
    ext_fun_name = ['transmit']
    ext_fun_name.append('receive')
    ext_fun_name.append('get_option')
    ext_fun_name.append('set_option')
    labels['name'] = target_name 
    for function in ext_fun_name:
        labels[pointer_name + '_' + function] = target_name + '_' + function

    init = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=pointer_name + '_init')
    if init:
        init = replaceTextUsingLabels(init, labels)
        del init[0]
        del init[0]
        del init[-1]
    

    hal_fun_body[0] = hal_fun_body[0].replace('void MX_' + interface.upper() + '_Init', 'static int ' + target_name + '_init' )
    del hal_fun_body[-1]
    hal_fun_body = ['EMBOX_UNIT_INIT(' + target_name + '_init);'] + hal_fun_body
    add_fun = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=pointer_name)
    if add_fun:
        del add_fun[0]
        del add_fun[0]
        add_fun = replaceTextUsingLabels(add_fun, labels)

    ext_fun_bodies = []
    ext_headers = []
    for function in ext_fun_name:
        _text = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=pointer_name + '_' + function)
        _text = replaceTextUsingLabels(_text, labels)
        ext_fun_bodies = ext_fun_bodies + _text
        if _text:
            ext_headers = ext_headers + ['extern ' + _text[0]]

    out_fun = start_header + init + hal_fun_body + add_fun + ext_fun_bodies
    return out_fun, ext_headers

def updateInterfaceFromDMA(path_to_src, path_to_driver, path_to_hal, interface_type, interface, dma_list, add_label = '_full'):

    print(dma_list)
    hal_fun_body = getFunctionC(path_to_src, interface)
    dmax_label = dma_list['TX'][:len('DMAx')]
    dmax_pt = 'DMAx'
    ll_dma_channel_tx = 'LL_' + dmax_label[:-1] + '_' + dma_list['TX'].split('_')[1]
    num = ll_dma_channel_tx[-1]
    ll_dma_channel_tx = ll_dma_channel_tx[:-1]
    ll_dma_channel_tx = ll_dma_channel_tx + '_' + num
    ll_dma_channel_tx_pt = 'LL_DMA_CHANNEL_Tx'
    ll_dma_channel_rx = 'LL_' + dmax_label[:-1] + '_' + dma_list['RX'].split('_')[1]
    num = ll_dma_channel_rx[-1]
    ll_dma_channel_rx = ll_dma_channel_rx[:-1]
    ll_dma_channel_rx = ll_dma_channel_rx + '_' + num
    ll_dma_channel_rx_pt = 'LL_DMA_CHANNEL_Rx'

    dma_channel_tx_irq = dma_list['TX'] + '_IRQn'
    dma_channel_rx_irq = dma_list['RX'] + '_IRQn'
    dma_channel_tx_irq_value = 0 
    dma_channel_rx_irq_value = 0
    dma_channel_tx_irq_pt = 'TX_NUM_IRQ'
    dma_channel_rx_irq_pt = 'RX_NUM_IRQ'
    with open(path_to_hal, 'r') as src:
        code_lines = src.read().splitlines()
        for line in code_lines:
            if line.find(dma_channel_tx_irq) != -1:
                dma_channel_tx_irq_value = int(re.sub('\D','',(line.split(',')[0].split('=')[1])))
            if line.find(dma_channel_rx_irq) != -1:
                dma_channel_rx_irq_value = int(re.sub('\D','',(line.split(',')[0].split('=')[1])))
    interface_label = interface.upper()
    interface_pt = interface_type.upper() + 'x'
    target_name = (interface + add_label + '_dma').upper()
    hal_fun_body[0] = hal_fun_body[0].replace('void MX_' + interface.upper() + '_Init', 'static int ' + target_name + '_init' )
    del hal_fun_body[-1]
    hal_fun_body = ['EMBOX_UNIT_INIT(' + target_name + '_init);'] + hal_fun_body
    print('tttttttttttttttttttttttttttttttttttttttttttttttttt')
    add_fun = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=interface_type + add_label + '_dma')
    if add_fun:
        del add_fun[0]
        del add_fun[0]
    # замена переменных в данных
    # вставки в функцию
    for line in add_fun:
        result_line = line.replace(dmax_pt, dmax_label)
        result_line = result_line.replace(interface_pt, interface_label)
        result_line = result_line.replace(dma_channel_tx_irq_pt, str(dma_channel_tx_irq_value))
        result_line = result_line.replace(dma_channel_rx_irq_pt, str(dma_channel_rx_irq_value))
        result_line = result_line.replace(ll_dma_channel_rx_pt, ll_dma_channel_rx)
        result_line = result_line.replace(ll_dma_channel_tx_pt, ll_dma_channel_tx)
        result_line = result_line.replace('name', target_name)
        hal_fun_body.append(result_line)
    # дополнительные функции
    fun_tx_irq_handler_pt = interface_type + add_label + '_dma_tx_irq_handler'
    fun_tx_irq_handler_label = target_name + '_tx_irq_handler'
    num_pt1 = 'LL_DMA_IsActiveFlag_TCx'
    num_pt2 = 'LL_DMA_ClearFlag_GIx'
    tx_num = ll_dma_channel_tx.split('_')[-1]
    tx_irq_handler_fun = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=fun_tx_irq_handler_pt)
    for line in tx_irq_handler_fun:
        result_line = line.replace(dmax_pt, dmax_label)
        result_line = result_line.replace(fun_tx_irq_handler_pt, fun_tx_irq_handler_label)
        result_line = result_line.replace(num_pt1, num_pt1[:-1] + tx_num)
        result_line = result_line.replace(num_pt2, num_pt1[:-1] + tx_num)
        result_line = result_line.replace('name', target_name)
        hal_fun_body.append(result_line)
    static_line = 'STATIC_IRQ_ATTACH(' + str(dma_channel_tx_irq_value) + ', ' + fun_tx_irq_handler_label + ', NULL);'
    hal_fun_body.append(static_line)

    fun_rx_irq_handler_pt = interface_type + add_label + '_dma_rx_irq_handler'
    fun_rx_irq_handler_label = target_name + '_rx_irq_handler'
    rx_num = ll_dma_channel_rx.split('_')[-1]
    rx_irq_handler_fun = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=fun_rx_irq_handler_pt)
    for line in rx_irq_handler_fun:
        result_line = line.replace(dmax_pt, dmax_label)
        result_line = result_line.replace(fun_rx_irq_handler_pt, fun_rx_irq_handler_label)
        result_line = result_line.replace(num_pt1, num_pt1[:-1] + rx_num)
        result_line = result_line.replace(num_pt2, num_pt1[:-1] + rx_num)
        result_line = result_line.replace('name', target_name)
        hal_fun_body.append(result_line)
    static_line = 'STATIC_IRQ_ATTACH(' + str(dma_channel_rx_irq_value) + ', ' + fun_rx_irq_handler_label + ', NULL);'
    hal_fun_body.append(static_line)

    fun_tx_thread_pt = interface_type + add_label + '_dma_tx_handler'
    fun_tx_thread_label = target_name + '_tx_handler'
    tx_handler_fun = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=fun_tx_thread_pt)
    for line in tx_handler_fun:
        result_line = line
        result_line = result_line.replace(fun_tx_thread_pt, fun_tx_thread_label)
        hal_fun_body.append(result_line)

    fun_rx_thread_pt = interface_type + add_label + '_dma_rx_handler'
    fun_rx_thread_label = target_name + '_rx_handler'
    rx_handler_fun = getFunctionC(path_to_driver, interface, is_cubemx=0, str_label=fun_rx_thread_pt)
    for line in rx_handler_fun:
        result_line = line
        result_line = result_line.replace(fun_rx_thread_pt, fun_rx_thread_label)
        hal_fun_body.append(result_line)
    return hal_fun_body


def getFunctionC(path, interface, is_cubemx = 1, str_label = 'void MX_', end_label = '_Init'):
    start_find_function = False
    bracket_counter = 0
    function_body = []
    with open(path, 'r') as src:
        code_lines = src.read().splitlines()
        for line in code_lines:
            target_label = str_label
            if is_cubemx:
                target_label = str_label + interface.upper() + end_label
            if line.find( target_label ) != -1 and line[-1] != ';':
                start_find_function = True
                function_body.append(line)
            else:
                if start_find_function:
                    if line.find('NVIC_') == -1:
                        function_body.append(line)
                    for elem in line:
                        if elem == '{':
                            bracket_counter = bracket_counter + 1
                            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++ =>' + str(bracket_counter))
                        elif elem == '}':
                            bracket_counter = bracket_counter - 1
                            print('------------------------------------------------------ =>' + str(bracket_counter))
                        if bracket_counter == 0:
                            start_find_function = False
                            return function_body
    return (function_body)

def getIncludesC(path):
    function_body = []
    with open(path, 'r') as src:
        code_lines = src.read().splitlines()
        for line in code_lines:
            if line.find('#include') != -1:
                function_body.append(line)
    return function_body


def modifyFunHeader(name, fun_body):
    fun_body.pop(0)
    name = name.lower()
    embox_title = ['EMBOX_UNIT_INIT(' + name + '_init);']
    start = ['static int ' + name + '_init( struct ' + name + '_dev *dev )']
    fun_body = embox_title + start + fun_body
    return fun_body

def addIncludeForSrc(name, fun_body):
    headers = [('#include \"' + name + '_generated.h\"')]
    headers += ['#include <embox/unit.h>']
    headers += ['#include <kernel/printk.h>']
    fun_body = headers + fun_body
    return fun_body

def addIncludeForHeader(mcu, interface, fun_body, libtype = 'll'):
    mcu_base = mcu[:7].lower() + 'xx'
    headers = ['#include <stdint.h>']
    headers += ['#include \"' + mcu_base + '_' + libtype + '_' + interface + '.h\"']
    fun_body = headers + fun_body
    return fun_body

def addStdCmdShell(cdms_list, name, fun_body):
    return_value = 'uint8_t '
    for cmd in cdms_list:
        fun_name = name.lower() + '_' + cmd
        input_values = cdms_list[cmd]
        fun_body = fun_body + [(return_value + fun_name +'(' + input_values + ')'), '{','','}']
    return fun_body

def addStdCmdHeader(cdms_list, name, fun_body):
    start_line = 'extern uint8_t '
    for cmd in cdms_list:
        fun_name = name.lower() + '_' + cmd
        input_values = cdms_list[cmd]
        fun_body = fun_body + [(start_line + fun_name +'(' + input_values + ');')]

    return fun_body

def addStruct(name,interface,fun_body):
    strct = []
    strct.append('struct ' + name + '_dev {')
    strct.append('\tint ' + interface + '_bus;')
    strct.append('\tstruct '+ interface +'_device *' + interface + '_dev;')
    strct.append('};')
    fun_body = strct + fun_body
    return fun_body

def saveToFileH(path, name, fun_body):
    header = name.upper() + '_GENERATED_H'

    fun_body = ['#ifndef ' + header] + [ '#define ' + header] + ['#include <stdint.h>'] + fun_body
    

    fun_body = fun_body + ['#endif \\\\' + header]    
    fun_body = fun_body + ['']

    with open(path + '\\' + name + '_generated.h', 'w') as trg:
        trg.write('\n'.join(fun_body))


    return

def saveToFileC(path, name, fun_body):

    fun_body = fun_body + ['']

    with open(path + '\\' + name + '_generated.c', 'w') as trg:
        trg.write('\n'.join(fun_body))
    return

def genSysMybuild(path,mcu, folder):
    body = []
    prj_name = path.split('\\')[-1]
    bsp_name = 'stm' + mcu[5:7].lower()
    body += ['package ' + folder + '.' + prj_name]
    body += []
    body += []
    for elem in os.listdir(path):
        if elem.startswith('system'):
            body += ['@Build(stage=1)']
            body += [r'@BuildDepends(third_party.bsp.' + bsp_name +  'cube.cube)']
            body += ['static module system_init extends third_party.bsp.st_bsp_api {']
            body += ['\tsource \"' + elem +'\"']
            body += [r'@NoRuntime depends third_party.bsp.' + bsp_name +  'cube.cube)']
            body += ['}']
        if elem.startswith('arch'):
            body += ['@BuildDepends(system_init)']
            body += [r'@BuildDepends(third_party.bsp.' + bsp_name +  'cube.cube)']
            body += ['module arch extends embox.arch.arch {']
            body += ['\tsource \"' + elem +'\"']
            body += [r'@NoRuntime depends system_init']
            body += ['\tdepends third_party.bsp.' + bsp_name +  'cube.cube)']
            body += ['}']
    return body

def genBaseMybuild(path, mcu, folder = 'stm32f103'):
    body = []
    prj_name = path.split('\\')[-1]
    bsp_name = 'stm' + mcu[5:7].lower()
    body += ['package ' + folder + '.' + prj_name]
    body += []
    body += []
    for elem in os.listdir(path):
        if elem.endswith('_generated.c'):
            body += [r'@BuildDepends(third_party.bsp.' + bsp_name +  'cube.cube)']
            body += ['module ' + elem.replace('_generated.c','') +'{']
        # if elem.endswith('.h'):
            body += ['\tsource \"' + elem +'\"']
            elem_h = elem[:-1] + 'h'
            if elem_h in os.listdir(path):
                body += ['\t' + r'@IncludeExport(path="' + prj_name + '\")']
                body += ['\tsource \"' + elem_h +'\"']
    body += ['}']
    return body

def saveToMybuild(path, fun_body):
    fun_body = fun_body + ['']

    with open(path + '\\Mybuild','w') as trg:
        trg.write('\n'.join(fun_body))
    return

    