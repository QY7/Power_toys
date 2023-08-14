from power_toys.components.inductor import Inductor
import numpy as np
import os
import matplotlib.pyplot as plt
import time
import random
import threading

ind_list = Inductor.list_all()
def run_task(start):
    for idx,ind_id in enumerate(ind_list[start:start+1]):
        print(f"{idx}:\t{ind_id}")
        if(not (ind_id[:3] == 'XGL')):
            print(ind_id[:3])
            continue
        if(os.path.exists(f"./power_toys/data/coilcraft_loss_for_training_more_data/{ind_id}.txt")):
            print(f"{ind_id} existed")
            continue
        with open(f"./power_toys/data/coilcraft_loss_for_training_more_data/{ind_id}.txt",'w') as f:
            ind = Inductor(ind_id)

            isat = ind.isat
            for dc in np.arange(0,isat,isat/30):
                for ac in np.arange(0,isat,isat/30):
                    if(dc == 0 and ac == 0):
                        continue
                    if(dc+ac/2>ind.isat*1.2):
                        break
                    while(1):
                        try:
                            freq,ac_loss,dc_loss,temp = ind.get_loss_by_frequency(dc=dc,ac = ac,freq_lower=10e3,freq_upper=2e6)
                            print(f"dc:\t{dc:.1f};\tac:{ac:.1f}")
                            break
                        except Exception as e:
                            print(e)
                            print("stuck")
                            time.sleep(1)
                    for i in range(len(freq)):
                        f.write(f"{dc},{ac},{freq[i]},{dc_loss[i]},{ac_loss[i]},{temp[i]}\n")
    print("finished")
if __name__ == "__main__":
    thread_list = []

    for i in range(18):
        t = threading.Thread(target=run_task,args=(46+11+80+i,))  # 创建多线程实例，Thread中target是需要子线程执行的函数
        thread_list.append(t)

    for t in thread_list:
        t.setDaemon(True)
        t.start()
    while(1):
        pass