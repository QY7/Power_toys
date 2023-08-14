# Power_toys

用于电力电子计算的工具库。基于`Component`类和`Circuit`类构建电力电子的损耗计算、参数优化、磁设计等分析平台

## Component类

所有的元件都继承于`BaseComponent`类，含有基本的面积获取接口`area()`和体积获取接口`volume()`。

元件通过`register_circuit(circui)`接口绑定相应的circuit，与电路拓扑建立联系。在与circuit建立联系之后，元器件实例可以调用`circuit_param(param_name)`获取电路中对应元器件的电气参数信息，比如开通时刻的电流、电压值，或者流经元件的电流有效值等，从而使用自身对应的损耗计算函数计算对应的损耗。

目前已经实现的元件有`MOSFET`、`Coilcraft`的电感和平面变压器`Transformer`。

元器件共有属性有
-`circuit_idx`在调用`register_circuit`的时候绑定对应的电路，并使用电路中的序号给元件编号，便于后续索引
-`quantity`在调用`register_circuit`的时候赋值。这个用于表征电路中用到了多少个这个元器件。在电力电子的拓扑中，会出现多个重复元器件的情况，比如四个cell的级联BUCK中，会在四个cell中使用相同的元件，因此`quantity`会赋值为4。再比如全桥电路中，四个元器件都是相同的元器件。
-`loss_list[]`损耗名称的列表，比如MOSFET的列表为`['con_loss','dri_loss','cap_loss','switch_off_loss','switch_on_loss','qrr_loss']`，电感的列表为`['loss_ac','loss_dc']`。

### MOSFET
MOSFET类继承于BaseComponent类，具有用于功率MOSFET的一些特有的属性，比如
`id`,`rdson`,`vbr`,`vgsth`,`rg`,`qg`,`qgd`,`qg_soft`,`cosse`,`cosst`等。这些属性通过数据库的方式存放于component.db文件中，并可以通过调用`MOSFET.load_from_lib(id)`的方式从数据库中获取实例对象，除了用于损耗分析的函数之外，这里再对一些特殊的函数接口进行说明
- `parallel(N)` 获取将MOSFET并联N个之后得到的新的器件，用于损耗优化
- `mos_in_series(rdson)` 类似`parallel`，也是获取相同性能的die制作的新的器件
- `opt_rdson()` 根据电路的参数，优化迭代自身的rdson，获取到损耗最小的rdson

### 电感
基本电感是直接继承于BaseComponent的BaseInductor类，其具有基本的获取ripple和获取电感的感值的方法，是一个理想的电感

基于BaseInductor，衍生了Coilcraft类，具有esr，损耗等非理想参数，其获取损耗的接口包括
- `loss_ac()`计算电感的交流损耗，即磁芯损耗等
- `loss_dc()`计算电感的铜损，即ESR的损耗
以上的损耗计算目前是使用爬取的数据训练的多层感知机（MLP），使用时最好double check一下