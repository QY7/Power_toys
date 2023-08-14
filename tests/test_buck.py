import pytest
import sys
sys.path.insert(0,'.')

from power_toys.components.mosfet.base_mosfet import MOSFET
from power_toys.topology.buck import BUCK
from power_toys.components.inductor.coilcraft import Coilcraft
from power_toys.common.const import *

def test_buck_main():
    Po = 110
    # 由于Buck输入是200V，如果输出也是200V，那么设计开关频率没有意义，这里以100V作为优化点
    Vo = 12

    Vin_Buck = 48
    Vo_Buck = Vo
    Io = Po/Vo

    mos1 = MOSFET.load_from_lib("BSC030N08NS5").parallel(1)
    mos2 = MOSFET.load_from_lib("BSC030N08NS5").parallel(1)

    ind = Coilcraft(id='XGL6060-103')

    buck = BUCK(vin=Vin_Buck,vo=Vo_Buck,Ncell = 2,q_active=mos1,q_passive=mos2,ind=ind,fs = 100e3,po = Po)
    assert buck.volt_sec() == 3e-05
    assert buck.duty == 0.25
    assert buck.duty_eff == 0.5
    assert buck.iripple() == pytest.approx(3)

    assert buck.loss_by_name(buck.mos2,'con_loss') == pytest.approx(0.4298233)

    assert buck.loss_by_name(buck.mos1,'con_loss') == pytest.approx(0.14327444)
    assert buck.loss_by_name(buck.mos1,'qrr_loss')+buck.loss_by_name(buck.mos2,'qrr_loss') == pytest.approx(0.4512)
    assert buck.loss_by_name(buck.mos1,'switch_on_loss')+buck.loss_by_name(mos2,'switch_on_loss') == pytest.approx(0.161467)
    assert buck.loss_by_name(buck.mos1,'switch_off_loss')+buck.loss_by_name(mos2,'switch_off_loss') == pytest.approx(0.2480915)
    assert buck.loss_by_name(buck.mos1,'cap_loss')+buck.loss_by_name(mos2,'cap_loss') == pytest.approx(0.08064)
    assert buck.loss_by_name(buck.mos1,'dri_loss')+buck.loss_by_name(mos2,'dri_loss') == pytest.approx(0.244)
    assert buck.loss_sum_on_component(buck.mos1) == pytest.approx(0.71515312219)
    assert buck.loss_by_name(buck.ind,'loss_ac')== pytest.approx(0.32416576,rel=1e-3)
    assert buck.loss_by_name(buck.ind,'loss_dc')== pytest.approx(1.3765,rel=1e-3)
    assert buck.total_loss == pytest.approx(3.45924150166)

    buck_opt_freq = buck.optimize_eff_by_fs
    assert buck_opt_freq.fs()/1000 == pytest.approx(96.698162596)

    buck_opt_rdson = buck.optimize_eff_by_rdson
    assert buck_opt_rdson.efficiency == pytest.approx(0.977773333)
