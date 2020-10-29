
def getInterfaceCount(path, interface_name):
    interface = []
    name = interface_name.lower()
    NAME = interface_name.upper()
    with open(path + '\\Inc\\' + name + '.h') as source:
        code = source.read().splitlines()
        for code_line in code:
            start_word = 'void MX_' + NAME
            if code_line.startswith(start_word):
                value = code_line.split('_')[1].lower()
                interface.append(value)
    return interface

def getDataFrom_ioc(path, label):
    with open(path, 'r') as source:
        options = source.read().splitlines()
        for data in options:
            if (data.startswith(label)):
                return data[len(label):]
    return ''

def getDataArrayFrom_ioc(path, label):
    array = []
    with open(path, 'r') as source:
        options = source.read().splitlines()
        for data in options:
            if (data.startswith(label)):
                array.append(data)
    return array


def getSensorsFrom_ioc(path):
    str_with_sns = getDataFrom_ioc(path,'Mcu.UserConstants=')
    data_list = str_with_sns.split(';')
    sensor_list = {}
    for data in data_list:
        if data.startswith('sensor_'):
            info, enabled = data.split(',')
            type, sensor, interface = info.split('_')
            sensor_struct = {}
            sensor_struct['interface'] = interface.lower()
            if enabled:
                sensor_list[sensor.upper()] = sensor_struct
    return sensor_list

def getMcuFlagFrom_ioc(path):
    str_with_mcu = getDataFrom_ioc(path,'Mcu.Name=')
    mcu_flag = ''
    if not str_with_mcu:
        return mcu_flag
    nb_count = len('stm32f100')
    mcu_flag = str_with_mcu[:nb_count] + 'x' +str_with_mcu[nb_count + 1]
    return mcu_flag

def getSysClkFrom_ioc(path):
    str_clc = getDataFrom_ioc(path,'RCC.SYSCLKFreq_VALUE=')
    if not str_clc:
        return -1
    return int(str_clc)

def getDmaParams(path):
    dma_str = getDataArrayFrom_ioc(path, 'Dma')
    dma_res = {}
    for param in dma_str:
        param_comp = param.split('.')
        for comp in param_comp:
            target_stream = 'Instance='
            if comp.startswith(target_stream):
                _labels = (param_comp[1].split('_'))
                if _labels[0] in dma_res:
                    dma_res[_labels[0]][_labels[1]] = comp.split('=')[1]
                else:
                    _newset = {}
                    _newset[_labels[1]] = comp.split('=')[1]
                    dma_res[_labels[0]] = _newset
    return dma_res
