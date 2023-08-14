import pyaedt
from pyaedt.maxwell import Maxwell3d
import os

class ModelFace():
    (Top,Bottom,Front,Back,Left,Right) = 'top','bottom','front','back','left','right'
    
class Ansys():
    def __init__(self):
        self.m3d = None

    @property
    def m3d(self):
        if(self._m3d == None):
            print("m3d object not assigned")
        return self._m3d
    
    @m3d.setter
    def m3d(self,value):
        self._m3d = value
    
    def create_winding(self,position = ['0mm','0mm','0mm'],r='0mm',k='0mm',w = '1mm',height = '0.3mm',name = None,matname = 'Copper'):
        """生成winding，同时生成winding的截面，命名为{name}_cross

        Args:
            position (list, optional): 原点位置，定义为strip上半部圆心位置. Defaults to ['0mm','0mm','0mm'].
            r (str, optional): 圆半径. Defaults to '0mm'.
            k (str, optional): k系数. Defaults to '0mm'.
            height (str, optional): winding的高度. Defaults to '3mm'.
            name (str, optional): 绕组的名字，如果不填入，则随机产生. Defaults to None.
            matname (str, optional): 材料名字，默认为铜. Defaults to 'Copper'.

        Returns:
            str: 返回绕组的名字
        """
        x,y,z = position[:]
        
        w_outer = self.create_strip(self.m3d,position,f"{r}+{w}-0.5mm",f"{k}*{r}/({r}+{w}-0.5mm)",height=height,matname=matname,name=name)
        w_inner = self.create_strip(self.m3d,position,f"{r}+0.5mm",f"{k}*{r}/({r}+0.5mm)",height=height,matname=matname)
        self.m3d.modeler.subtract(
            w_outer,
            w_inner,
            keep_originals=False
        )
        self.m3d.modeler.create_rectangle('YZ',[f"({x})+({k})*({r})/2",f"{y}-{r}-{w}+0.5mm",z],[f"{w}-1mm",height],name=f"{name}_cross")
        return w_outer
    
    def create_strip_face(self,position = ['0mm','0mm','0mm'],r='0mm',k='0mm',along='X',name = None):
        """产生strip的surface

        Args:
            position (list, optional): 原点位置，定义为strip上半部圆心位置. Defaults to ['0mm','0mm','0mm'].
            r (str, optional): 圆半径. Defaults to '0mm'.
            k (str, optional): k系数. Defaults to '0mm'.
            name (_type_, optional): 名字. Defaults to None.

        Returns:
            str: 返回名字
        """
        x,y,z = position[:]
        if(along=='X'):
            c1 = self.m3d.modeler.create_circle('XY',position,r,name=name)
            c2 = self.m3d.modeler.create_circle('XY',[f"{x}+{k}*{r}",y,z],r)
            rect1 = self.m3d.modeler.create_rectangle('XY',[x,f"{y}-{r}",z],dimension_list=[f"{k}*{r}",f"2*{r}"])
        else:
            c1 = self.m3d.modeler.create_circle('XY',position,r,name=name)
            c2 = self.m3d.modeler.create_circle('XY',[x,f"{y}+{k}*{r}",z],r)
            rect1 = self.m3d.modeler.create_rectangle('XY',[f"{x}-{r}",y,z],dimension_list=[f"2*{r}",f"{k}*{r}"])
        return self.m3d.modeler.unite([c1,c2,rect1],keep_originals=False)

    def create_strip(self,
                     position = ['0mm','0mm','0mm'],
                     r='0mm',
                     k='0mm',
                     height='3mm',
                     matname='ferrite',
                     name='leg',
                     csplane = 'XY',
                     along = 'X',
                     create_cross = False
                    ):
        """生成strip的实体

        Args:
            position (list, optional): 原点位置，定义为strip上半部圆心位置. Defaults to ['0mm','0mm','0mm'].
            r (str, optional): 圆半径. Defaults to '0mm'.
            k (str, optional): k系数. Defaults to '0mm'.
            height (str, optional): strip的高度. Defaults to '3mm'.
            matname (str, optional): 材料名字，默认为铁氧体. Defaults to 'ferrite'.
            name (str, optional): 名字. Defaults to 'leg'.
            csplane (str, optional): 操作的平面. Defaults to 'XY'.
            create_cross (bool, optional): 是否创建中心截面. Defaults to False.

        Returns:
            str: 生成的strip的名字
        """
        x,y,z = position[:]
        if(along == 'X'):
            cylinder1 = self.m3d.modeler.create_cylinder(csplane,position=position, radius= r,height=height,name=name,matname = matname)
            cylinder2 = self.m3d.modeler.create_cylinder(csplane,position=[f"({x}) + ({k}) * ({r})" , y , z], radius= r,height=height,matname  =matname)
            box = self.m3d.modeler.create_box([x,f"({y})-({r})",z],dimensions_list=[f"({k})*({r})",f"2*({r})",height],matname = matname)
        else:
            cylinder1 = self.m3d.modeler.create_cylinder(csplane,position=position, radius= r,height=height,name=name,matname = matname)
            cylinder2 = self.m3d.modeler.create_cylinder(csplane,position=[x , f"{y}+({k}) * ({r})" , z], radius= r,height=height,matname  =matname)
            box = self.m3d.modeler.create_box([f"({x})-({r})",y,z],dimensions_list=[f"2*({r})",f"({k})*({r})",height],matname = matname)
            
        unite_leg = self.m3d.modeler.unite([cylinder1,cylinder2,box])
        if(create_cross):
            cls.create_strip_face(self.m3d,[x,y,f"{z}+{height}/2"],r,k,f"{name}_cross")
        return unite_leg

    def create_I_plate(self,
                       position = ['0mm','0mm','0mm'],
                       r='0mm',
                       k='0mm',
                       w='0mm',
                       height = '0mm',
                       along='X',
                       cover_winding = False,
                       name = None,
                       matname = 'ferrite'
                       ):
        """根据与leg长度相同，生成I片

        Args:
            position (list, optional): 原点位置，定义为不cover winding时的立方体的顶点. Defaults to ['0mm','0mm','0mm'].
            r (str, optional): 圆半径. Defaults to '0mm'.
            k (str, optional): k系数. Defaults to '0mm'.
            w (str, optional): 绕组宽度. Defaults to '0mm'.
            height (str, optional): I片高度. Defaults to '0mm'.
            name (str, optional): 名字. Defaults to None.
            matname (str, optional): 材料名字. Defaults to 'ferrite'.
        """
        if(cover_winding):
            x,y,z = position[:]
            if(along == 'X'):
                self.m3d.modeler.create_box([f"{x}-({w})",y,z],dimensions_list=[f"2*{r}+({k})*({r})+2*({w})",f"4*{r}+2*{w}",height],name=name,matname=matname)
            else:
                self.m3d.modeler.create_box([x,f"{y}-({w})",z],dimensions_list=[f"4*{r}+2*{w}",f"2*{r}+({k})*({r})+2*({w})",height],name=name,matname=matname)
        else:
            if(along == 'X'):
                self.m3d.modeler.create_box(position,dimensions_list=[f"2*{r}+({k})*({r})",f"4*{r}+2*{w}",height],name=name,matname=matname)
            else:
                self.m3d.modeler.create_box(position,dimensions_list=[f"4*{r}+2*{w}",f"2*{r}+({k})*({r})",height],name=name,matname=matname)
                
    def init_setup(self,fs = 1e6):
        """初始化self.m3d的Setup

        Args:
            self.m3d (Maxwell3d): _description_
            fs (float or int, optional): 频率. Defaults to 1e6.
        """
        Setup = self.m3d.create_setup(setupname="Setup1")
        Setup.props["Frequency"] =f"{fs}Hz"
        Setup.props["HasSweepSetup"] = False
    
    def connect_to_proj(self,proj_name,design_name,solver = 'EddyCurrent', desktop_version = '2022.1'):
        """连接到已有的工程文件

        Args:
            proj_name (str): 项目名
            design_name (str): design名
            solver (str, optional): 求解器. Defaults to 'EddyCurrent'.
            desktop_version (str, optional): 软件版本. Defaults to '2022.1'.

        Returns:
            Maxwell3D: 返回self.m3d的操作对象
        """
        non_graphical = False
        self.m3d = pyaedt.Maxwell3d(
            projectname=proj_name,
            designname=design_name,
            solution_type=solver,
            specified_version = desktop_version,
            non_graphical=non_graphical,
            new_desktop_session=False,
        )
        self.m3d.modeler.model_units = "mm"
        return self
    
    def add_phi(self,surf_name,express_name):
        """增加phi的expression

        Args:
            surf_name (str): surf的名字
            express_name (str): expression的名字

        Returns:
            str: expression的名字
        """
        Fields = self.m3d.odesign.GetModule("FieldsReporter")
        Fields.EnterQty("B")
        Fields.CalcOp("Smooth")
        Fields.EnterScalar(0)
        Fields.CalcOp("AtPhase")
        Fields.EnterVector([0,0,1])
        Fields.CalcOp('Dot')
        Fields.EnterSurf(surf_name)
        Fields.CalcOp('Integrate')
        try:
            Fields.AddNamedExpression(express_name, "Fields")
        except:
            print("Expression might exist")
        return express_name

    def add_core_loss(self,vol_list,express_name):
        """增加core loss的expression

        Args:
            vol_list (list): 用于计算的core的list，会将list中的损耗求和
            express_name (str): expression的名字

        Returns:
            str: expression的名字
        """
        Fields = self.m3d.odesign.GetModule("FieldsReporter")
        # 计算所有CoreLoss
        Fields.EnterQty("CoreLoss")
        Fields.CalcOp("Smooth")
        Fields.EnterVol(vol_list[0])
        Fields.CalcOp('Integrate')
        for vol in vol_list[1:]:
            Fields.EnterQty("CoreLoss")
            Fields.CalcOp("Smooth")
            Fields.EnterVol(vol)
            Fields.CalcOp('Integrate')
            Fields.CalcOp('+')

        # 计算所有欧姆Loss
        Fields.EnterQty("OhmicLoss")
        Fields.CalcOp("Smooth")
        Fields.EnterVol(vol_list[0])
        Fields.CalcOp('Integrate')
        Fields.CalcOp('+')
        for vol in vol_list[1:]:
            Fields.EnterQty("OhmicLoss")
            Fields.CalcOp("Smooth")
            Fields.EnterVol(vol)
            Fields.CalcOp('Integrate')
            Fields.CalcOp('+')
        try:
            Fields.AddNamedExpression(express_name, "Fields")
        except:
            print("Expression might exist")
        return express_name
    
    def add_core_ohmic_loss(self,vol_list,express_name):
        """增加core loss的expression

        Args:
            vol_list (list): 用于计算的core的list，会将list中的损耗求和
            express_name (str): expression的名字

        Returns:
            str: expression的名字
        """
        Fields = self.m3d.odesign.GetModule("FieldsReporter")
        # 计算所有欧姆Loss
        Fields.EnterQty("OhmicLoss")
        Fields.CalcOp("Smooth")
        Fields.EnterVol(vol_list[0])
        Fields.CalcOp('Integrate')
        for vol in vol_list[1:]:
            Fields.EnterQty("OhmicLoss")
            Fields.CalcOp("Smooth")
            Fields.EnterVol(vol)
            Fields.CalcOp('Integrate')
            Fields.CalcOp('+')
        try:
            Fields.AddNamedExpression(express_name, "Fields")
        except:
            print("Expression might exist")
        return express_name
    
    def get_value_along_line(self,expression_name,obj):
        if(obj in self.all_objects_name(self.m3d)):
            variations = {"Freq": ["All"], "Phase": ["0deg"]}
            solutions = self.m3d.post.get_solution_data(
                expressions=expression_name,
                report_category="Fields",
                context=obj,
                variations=variations
            )
            return solutions
        else:
            print("No line available")
    
    def get_scalar_value(self,expression):
        """获得scalar的数据值，需要仿真结束了才能获取

        Args:
            expression (_type_): _description_

        Returns:
            _type_: _description_
        """
        variations = {
            "Phase": ["0deg"],
        }
        solutions = self.m3d.post.get_solution_data(
            expressions = expression,
            report_category="Fields",
            variations=variations,
        )
        if(solutions):
            return solutions.data_magnitude()[0]
        else:
            print("No data available")
            return 0
    
    def all_objects_name(self):
        return self.m3d.modeler._all_object_names
    
    def plot_field_3d(self,volume_name,expression):
        return self.m3d.post.create_fieldplot_volume(volume_name,expression,'Fields','test')
    
    def create_face_from_volume(self,volume_name,which_face:ModelFace,face_name):
        """从volume_name的物体上创建face

        Args:
            volume_name (_type_): _description_
            which_face (ModelFace): _description_
            face_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        if(face_name in cls.all_objects_name(self.m3d)):
            return False
        obj = self.m3d.modeler.get_object_from_name(volume_name)
        which_face = which_face.lower()

        if(which_face == ModelFace.Top):
            tmp = obj.top_face_z.create_object()
        elif(which_face == ModelFace.Bottom):
            tmp = obj.bottom_face_z.create_object()
        elif(which_face == ModelFace.Front):
            tmp = obj.front_face_x.create_object()
        elif(which_face == ModelFace.Back):
            tmp = obj.back_face_x.create_object()
        elif(which_face == ModelFace.Left):
            tmp = obj.left_face_y.create_object()
        elif(which_face == ModelFace.Right):
            tmp = obj.right_face_y.create_object()
        else:
            return False
        tmp.name = face_name
        return True
    
    def create_field_plot_volume(self,volume,quantity,plot_name):
        intrinsic = {"Freq": "1MHz", "Phase": "0deg"}
        self.m3d.post.create_fieldplot_volume(
            volume,
            quantity,
            self.m3d.existing_analysis_sweeps[0],
            intrinsic,
            plot_name=plot_name
        )
    
    def import_ferrite(self):
        self.m3d.materials.import_materials_from_file(os.path.dirname(__file__)+'/../data/ferrite_loss.json')

    def delete_all(self):
        for obj in self.m3d.modeler.object_list:
            self.m3d.modeler.delete(obj)
        for var in self.m3d.variable_manager.variable_names:
            self.m3d.variable_manager.delete_variable(var)

    def rename_winding(self,name_filters:list,volume_filter:float,rename_prefix:str,group_name:str): #测试用函数，最后还要将obj的list加入到输入变量中
        """
        定位到模型中某个长方体区域内的实体，修改名字，并编组
        Original by Felix Qi, edited by Gao Fan
        Ver 20230731.1
        位置确定流程：
        1. 规定实体命名前缀，如pri winding，sec winding 等等，同时规定相应的counter；
        2. 规定不同实体前缀对应的原始绕组实体中的名称/网络名，如pri winding一般有 Cr_Trans的网络或MID的网络，规定这些网络方便查找；
        3. 对不同实体组内，按照Z轴坐标排序；
        4. 对不同实体组内，按照已排顺序进行命名；
        Args:
            name_filters (list): 用于过滤实体的name列表
            volume_filter (float): 体积最小值，低于这个值的被过滤掉
            rename_prefix (str): 重命名的前缀   
            group_name (str): 编组的名字
        """
        counter = 1

        winding_list = []
        pos_list = []
        pos_z_list = []

        for obj in self.m3d.modeler.object_list:
            flag = False
            for net in name_filters:
                if net in obj.name:
                    flag = True
            
            if(flag and obj.volume>volume_filter and obj.material_name == 'copper'): 
                winding_list.append(obj)

        winding_list.sort(reverse=True,key=lambda obj: obj.bounding_box[2])#基于bounding_box[2]对winding_list排序

        for obj in winding_list:
            obj.name = f"{rename_prefix}{counter}"
            counter+=1
        self.m3d.modeler.create_group(winding_list,group_name=group_name)