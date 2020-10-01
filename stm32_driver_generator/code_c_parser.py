


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
    start = ['int ' + name + '_init( struct ' + name + '_dev *dev )']
    fun_body = start + fun_body
    return fun_body

def addStruct(name,interface,fun_body):
    strct = []
    strct.append('struct ' + name + '_dev {')
    strct.append('\tint ' + interface + '_bus;')
    strct.append('\tstruct '+ interface +'_device *' + interface + '_dev;')
    strct.append('};')
    fun_body = strct + fun_body
    return fun_body

def saveToFileC(path, name, fun_body):
    # header = name.upper()

    # fun_body.insert(0, '#ifndef ' + header)
    # fun_body.insert(0, '#define ' + header)

    # fun_body.append('#endif')    

    with open(path + '\\' + name + '_generated.c', 'w') as trg:
        trg.write('\n'.join(fun_body))
    return
    