import  numpy as np
import pyaedt
from pyaedt.maxwell import Maxwell3d
from ..components.ansys import Ansys

class Transformer():
    rho_cu = 17.2*1e-9
    # 使用3oz的铜
    oz_unit=35*1e-6
    Kac=3
    Kfe=2
    # Pv=np.power(10,c1)*np.power((1000*Bmax),b1)*1000
    selected_mag = 'DMR_51w'
    magnetic_material = {
        'DMR_51w':{
            'c1':-3.6653,
            'b1':3.465
        }
    }

    def __init__(self,r,w,k,Noz = 2.5,h_leg = 3.5e-3,cover_winding = False):
        """变压器模型参数的创建

        Args:
            r (float): 磁芯柱子的圆弧半径
            w (flaot): 绕组的宽度
            k (float): 磁芯主子的长边/圆弧半径
            Noz (float, optional): 单层的PCB厚度. Defaults to 3.
        """
        self.m3d = None
        self.r = r
        self.w = w
        self.thick_layer = self.oz_unit*Noz
        self.k = k
        self.height_leg = h_leg
        self.core_list = []
        self.core_mat = 'ferrite'
        self.cover_winding = cover_winding
        # 默认的height_plate使用Ae来算
        self.height_plate = self.Ae/self.length_plate

    @classmethod
    def load_from_prj(cls,project_name,design_name,desktop_version = '2022.1'):
        m3d = Ansys.connect_to_proj(project_name,design_name,desktop_version=desktop_version)
        try:
            r = m3d['_r']
            w = m3d['_w']
            k = m3d['_k']
            r_val = float(r[:-2])*1e-3 if 'mm' in r else 0
            w_val = float(w[:-2])*1e-3 if 'mm' in w else 0
            k_val = float(k[:-7])/100 if 'percent' in k else 0
            trans_tmp =  cls(r_val,w_val,k_val)
            trans_tmp.m3d = m3d
            trans_tmp.core_list = ['left_leg','right_leg','Top_plate','Bottom_plate']
            return trans_tmp
        except:
            return None

    @property
    def r(self):
        return self._r
    
    @r.setter
    def r(self,value):
        self._r = value
        if(self.m3d):
            self.m3d['_r'] = f"{value*1e3}"+'mm'
        
    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self,value):
        self._w = value
        if(self.m3d):
            self.m3d['_w'] = f"{value*1e3}"+'mm'

    @property
    def k(self):
        return self._k
    
    @k.setter
    def k(self,value):
        self._k = value
        if(self.m3d):
            self.m3d['_k'] = f"{value*1e3}"+'mm'

    @property
    def l_leg_straight(self):
        """计算leg的长边的长度

        Returns:
            float: 长边的长度
        """
        return self.k*self.r
    
    @property
    def l_mag(self):
        """计算磁路的路径

        Returns:
            _type_: _description_
        """
        return 2*(2*self.w+2*self.r+2*self.height_plate/2)+2*(self.height_leg)
    
    @property
    def height_plate(self):
        """计算I片的厚度

        Returns:
            _type_: _description_
        """
        return self._height_plate
    
    @height_plate.setter
    def height_plate(self,value):
        self._height_plate = value
        if(self.m3d):
            self.m3d['_height_plate'] = f"{value*1e3}"+'mm'
    
    @property
    def air_gap(self):
        return 0.1e-3
    
    @property
    def Ae(self):
        """返回Ae面积

        Returns:
            m^2: Ae面积
        """
        return np.power(self.r,2)*np.pi+self.l_leg_straight*(2*self.r)
    
    def Bmax(self,fs,v):
        """返回Bmax

        Args:
            fs (Hz): 开关频率
            v (volt): 单匝的电压

        Returns:
            T: 返回Bmax的单边峰值
        """
        return v*(0.5*1/fs)/(self.Ae)/2
    
    @property
    def DCR(self):
        r = self.r
        w = self.w
        rho_cu = self.rho_cu
        pi = np.pi
        dcr = (((rho_cu*2*pi/self.thick_layer)*(1/np.log((pi*r+pi*w)/(pi*r))))+((rho_cu/self.thick_layer)*(2*self.l_leg_straight/w)))
        return dcr

    @property
    def footprint(self):
        """返回变压器面积

        Returns:
            float: 面积，单位mm2
        """
        return self.length_trans*self.width_trans
    
    @property
    def height_trans(self):
        """计算变压器的高度

        Returns:
            float: 高度
        """
        return self.height_plate*2+self.height_leg
    
    @property
    def height_leg(self):
        return self._height_leg
    
    @height_leg.setter
    def height_leg(self,value):
        self._height_leg = value
        if(self.m3d):
            self.m3d['_height_leg'] = value

    @property
    def length_plate(self):
        """这个假定磁芯cover了上下的绕组
                  width          
                _______                 width
               |_     _|              _________ 
        length | |   | |       length | |   | |
               | |   | |              | |   | |
               |¯     ¯|              ¯¯¯¯¯¯¯¯¯
               ¯¯¯¯¯¯¯¯¯              
        Returns:
            _type_: _description_
        """
        if(self.cover_winding):
            return 2*self.w+2*self.r+self.l_leg_straight
        else:
            return 2*self.r+self.l_leg_straight
    
    @property
    def length_trans(self):
        """变压器的长度考虑了绕组的，即便是绕组上没有磁芯
                 width          
                _______                 width
               |_     _|              _________ 
        length | |   | |       length | |   | |
               | |   | |              | |   | |
               |¯     ¯|              ¯¯¯¯¯¯¯¯¯
               ¯¯¯¯¯¯¯¯¯              
        Returns:
            _type_: _description_
        """
        return 2*self.w+2*self.r+self.l_leg_straight
    
    @property
    def width_plate(self):
        """计算plate的宽度，这里假定左右最外面的绕组上面没有磁芯
        width          
                _______                 width
               |_     _|              _________ 
        length | |   | |       length | |   | |
               | |   | |              | |   | |
               |¯     ¯|              ¯¯¯¯¯¯¯¯¯
               ¯¯¯¯¯¯¯¯¯              
        Returns:
            _type_: _description_
        """
        return 2*self.w+2*2*self.r
    
    @property
    def width_trans(self):
        """_summary_
                 width          
                _______                 width
               |_     _|              _________ 
        length | |   | |       length | |   | |
               | |   | |              | |   | |
               |¯     ¯|              ¯¯¯¯¯¯¯¯¯
               ¯¯¯¯¯¯¯¯¯              

        Returns:
            _type_: _description_
        """
        return 4*self.w+2*2*self.r

    @property
    def volume_mag_loss(self):
        """磁损耗计算用到的体积

        Returns:
            _type_: _description_
        """
        return self.l_mag*self.Ae
    
    @property
    def volume_trans(self):
        """计算整个变压器的体积

        Returns:
            _type_: _description_
        """
        return self.height_trans*self.footprint

    def winding_loss(self,Irms,turn=1):
        return self.DCR*turn**2*(Irms**2)*self.Kac

    def create_core(self):

        left_leg_name = Ansys.create_strip(
            m3d = self.m3d,
            position = [0,0,0],
            r = '_r',
            k = '_k',
            height= '_height_leg',
            name='left_leg',
            create_cross=True,
            matname=self.core_mat
        )

        Ansys.create_strip(
            m3d = self.m3d,
            position = [0,'2*_w+2*_r',0],
            r = '_r',
            k = '_k',
            height = '_height_leg',
            name='right_leg',
            create_cross=True,
            matname=self.core_mat
        )

        Ansys.create_I_plate(
            m3d = self.m3d,
            position = ['-_r','-_r','_height_leg+_air_gap'],
            r = '_r',
            k = '_k',
            w = '_w',
            height="_height_plate",
            cover_winding=self.cover_winding,
            name='Top_plate',
            matname=self.core_mat
        )

        Ansys.create_I_plate(
            m3d = self.m3d,
            position = ['-_r','-_r',f'-_air_gap-_height_plate'],
            r = '_r',
            k = '_k',
            w = '_w',
            height = "_height_plate",
            cover_winding=self.cover_winding,
            name = 'Bottom_plate',
            matname=self.core_mat
            )
        # Core的list
        self.core_list = ['left_leg','right_leg','Top_plate','Bottom_plate']
        # 打开所有Core的损耗计算
        self.m3d.set_core_losses(self.core_list,True)
    def init_ansys(self,desktop_version = "2022.1"):

        design_name = "Transformer"
        Solver = "EddyCurrent"
        non_graphical = False

        self.m3d = pyaedt.Maxwell3d(
            projectname=pyaedt.generate_unique_project_name(),
            designname=design_name,
            solution_type=Solver,
            specified_version=desktop_version,
            non_graphical=non_graphical,
            new_desktop_session=True,
        )
        self.m3d.modeler.model_units = "mm"
    
    def create_model(self,desktop_version = "2022.1",project_name = '',design_name = ''):
        if(not self.m3d):
            if(not project_name and not design_name):
                self.init_ansys(desktop_version)
            else:
                self.m3d = Ansys.connect_to_proj(project_name,design_name,desktop_version=desktop_version)
        self.m3d['_r'] = f"{self.r*1e3}"+'mm'
        self.m3d['_w'] = f"{self.w*1e3}"+'mm'
        self.m3d['_k'] = f"{self.k*1e2}"+'Percent'
        self.m3d['_height_leg'] = f"{self.height_leg*1e3}"+'mm'
        self.m3d['_air_gap'] = f"{self.air_gap*1e3}"+'mm'
        self.m3d['_height_plate'] = f"{self.height_plate*1e3}"+'mm'
        if(self.m3d.active_setup == None):
            Ansys.init_setup(self.m3d,500e3)
        self.m3d.modeler.create_air_region(x_pos=300, y_pos=300, z_pos=300, x_neg=300, y_neg=300, z_neg=300)
        self.create_core()
        self.ansys_handler = Ansys()
        Ansys.create_winding(
            m3d = self.m3d,
            position=[0,0,0],
            r = '_r',
            k = '_k',
            height='_height_leg',
            name='left_winding'
        )
        Ansys.create_winding(
            m3d = self.m3d,
            position=[0,'2*_r+2*_w',0],
            r = '_r',
            k = '_k',
            height='_height_leg',
            name = 'right_winding'
        )
        
    
    def assign_current(self,current_amp):
        """根据变量名current_name添加电流，其大小为current_amp

        Args:
            current_amp (float): 电流大小，单位A
            current_name (str): 变量名

        Returns:
            current_name: 电流变量名
        """
        m3d = self.m3d
        if(len(m3d.excitations) == 0):
            m3d.assign_current(
                ['left_winding_cross'],
                amplitude = current_amp,
                swap_direction = False,
                name = 'left_winding_current'
            )
            m3d.assign_current(
                ['right_winding_cross'],
                amplitude = current_amp,
                swap_direction = True,
                name = 'right_winding_current'
            )
            return True
        return False

    def start_sim(self):
        self.m3d.analyze_all()

    def tune_to_phi(self,phi_target,current_name,phi_express_name,start_current = 1):
        try:
            current_val = self.m3d[current_name]
        except:
            return
        start_current = 1
        phi_leg = 0
        m3d = self.m3d
        m3d[current_name] = f'{start_current}A'
        self.assign_current(current_name)
        while(np.abs(phi_leg-phi_target)>0.1e-6):
            m3d[current_name] = f"{start_current:.2f}A"
            variations = {
                "Phase": ["0deg"], 
            }
            print("start simulation")
            m3d.analyze_all()
            print("stop")
            
            phi_leg = self.phi_in_leg
            start_current = phi_target / phi_leg*start_current
            print(f"phi_keg us {phi_leg*1e6:.2f}u")
            print(f"Excitation current is {start_current:.2f}")

    @property
    def phi_in_leg(self):
        Ansys.add_phi(
            self.m3d, 
            surf_name='left_leg_cross',
            express_name='Phi_left_leg'
        )
        phi = Ansys.get_scalar_value(self.m3d,'Phi_left_leg')
        return phi

    @property
    def all_core_loss(self):
        Ansys.add_core_loss(
            self.m3d,
            self.core_list,
            express_name='All_core_loss'
        )
        Ansys.add_core_ohmic_loss(
            self.m3d,
            self.core_list,
            express_name='All_core_ohmic_loss'
        )
        loss = Ansys.get_scalar_value(self.m3d,'All_core_loss')
        ohmic_loss = Ansys.get_scalar_value(self.m3d,'All_core_ohmic_loss')
        return loss,ohmic_loss
    
if __name__ == '__main__':
    trans1 = Transformer(r=5e-3,w= 5e-3,k=1)
    print(trans1.width_plate)
    # print(trans0.core_loss(fs,vs))
