
def getFunctionC(path, interface):
    print(path)
    start_find_function = False
    bracket_counter = 0
    function_body = []
    path = path + interface[:(len(interface)-1)] + '.c'
    with open(path, 'r') as src:
        code_lines = src.read().splitlines()
        for line in code_lines:
            if line.find('void MX_' + interface.upper() + '_Init') != -1:
                start_find_function = True
                function_body.append(line)
            else:
                if start_find_function:
                    function_body.append(line)
                    for elem in line:
                        if elem == '{':
                            bracket_counter = bracket_counter + 1
                        elif elem == '}':
                            bracket_counter = bracket_counter - 1
                        if bracket_counter == 0:
                            start_find_function = False

    return (function_body)

def modifyFunHeader(name, fun_body):
    fun_body.pop(0)
    name = name.lower()
    embox_title = ['EMBOX_UNIT_INIT(' + name + '_init);']
    start = ['static int ' + name + '_init( struct ' + name + '_dev *dev )']
    fun_body = embox_title + start + fun_body
    return fun_body

def addIncludeForSrc(name, fun_body):
    headers = [('#include \"' + name + '_generated.h\"')]
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

    fun_body = ['#ifndef ' + header] + [ '#define ' + header] + fun_body

    fun_body = fun_body + ['#endif + \\\\' + header]    
    fun_body = fun_body + ['']

    with open(path + '\\' + name + '_generated.h', 'w') as trg:
        trg.write('\n'.join(fun_body))


    return

def saveToFileC(path, name, fun_body):

    fun_body = fun_body + ['']

    with open(path + '\\' + name + '_generated.c', 'w') as trg:
        trg.write('\n'.join(fun_body))
    return
    