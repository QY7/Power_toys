from power_toys.components.mosfet import MOSFET
from power_toys.data.database import component_session
from power_toys.model_params import mosfet_param_list

# 检查参数的所有属性，如果是String的字段，没有值的给赋值None，所有的Float字段，没有值的赋0
mos_list = MOSFET.list_all_model(MOSFET.vbr>10)
for mos in mos_list:
    for param in mosfet_param_list.keys():
        param_val = getattr(mos,param)
        if(param == 'id'):
            continue
        if(param == 'footprint'):
            if(param_val == None):
                setattr(mos,param,'')
        else:
            if(param_val == None or isinstance(param_val,str)):
                setattr(mos,param,0)
    mos.save_to_db()
