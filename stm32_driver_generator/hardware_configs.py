
def getInterfaceCount(path, interface_name):
    interface = {}
    name = interface_name.lower()
    NAME = interface_name.upper()
    with open(path + '\\Inc\\' + name + '.h') as source:
        code = source.read().splitlines()
        for code_line in code:
            start_word = 'void MX_' + NAME
            if code_line.startswith(start_word):
                value = name + code_line[len(start_word)]
                interface[value] = 'disabled'
    return interface

def getDataFrom_ioc(path, label):
    with open(path, 'r') as source:
        options = source.read().splitlines()
        for data in options:
            if (data.startswith(label)):
                return data[len(label):]
    return ''

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
    nb_count = len('stm32f100x0')
    mcu_flag = str_with_mcu[:nb_count]
    mcu_flag = mcu_flag[:(nb_count-2)] + 'x' + mcu_flag[nb_count-1]
    return mcu_flag

def getSysClkFrom_ioc(path):
    str_clc = getDataFrom_ioc(path,'RCC.SYSCLKFreq_VALUE=')
    return int(str_clc)