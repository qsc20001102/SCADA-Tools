import csv
import os
import logging
from datetime import datetime
from tkinter import messagebox

logger = logging.getLogger(__name__)

class CSVManager:
    """
    负责 CSV 文件的读取、数据存储、拼接和输出
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.csv_data = []

    def load_csv(self, filepath):
        """自动识别编码读取 CSV 文件"""
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.csv_data = list(reader)
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='gbk') as f:
                reader = csv.DictReader(f)
                self.csv_data = list(reader)

        if not self.csv_data:
            logger.warning(f"CSV 文件为空或格式错误：{filepath}")
        else:
            logger.info(f"成功加载 CSV：{filepath}，共 {len(self.csv_data)} 行")
        return self.csv_data

    def generate_output(self, folder, file_name):
        """
        根据headers和rows生成新的 CSV 文件
        Args:
            folder:文件夹名称
            file_name:文件名称
        """
        if  not self.headers or not self.rows:
            logger.warning(f"数据为空，不生成文件")
            return
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S") #获取当前时间
        output_filename = f"{file_name}_{timestamp}.csv"    #输出文件名
        output_path = os.path.join(self.base_dir, folder, output_filename)    #输出文件路径
        os.makedirs(os.path.dirname(output_path), exist_ok=True)    #确保输出目录存在
        #写入输出文件
        try:
            with open(output_path, 'w', newline='', encoding='ANSI') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                writer.writerows(self.rows)
        except Exception as e:
                logger.warning(f"写入文件失败：{e}")
                messagebox.showwarning("警告", "写入文件失败")
                return
        logger.info(f"成功生成点表文件：{output_path}（共 {len(self.rows)} 行）")
        output = f"成功生成点表文件：{output_path}（共 {len(self.rows)} 行）"
        
        return output
    
    def rows_kingscdada(self, template_data, user_inputs):
        """
        根据传入数据进行处理，并将数据写入headers和rows存储
        Args:
            template_data：读取的模板数据
            user_inputs：用户设定的数据
        """
        #表头
        self.headers = ["TagID", "TagName", "Description", "TagType", "TagDataType",
                   "MaxRawValue", "MinRawValue", "MaxValue", "MinValue", "NonLinearTableName",
                   "ConvertType", "IsFilter", "DeadBand", "Unit", "ChannelName",
                   "DeviceName", "ChannelDriver", "DeviceSeries", "DeviceSeriesType", "CollectControl",
                   "CollectInterval", "CollectOffset", "TimeZoneBias", "TimeAdjustment", "Enable",
                   "ForceWrite", "ItemName", "RegName", "RegType", "ItemDataType",	
                   "ItemAccessMode", "HisRecordMode", "HisDeadBand", "HisInterval", "TagGroup",
                   "NamespaceIndex", "IdentifierType", "Identifier", "ValueRank", "QueueSize",
                   "DiscardOldest", "MonitoringMode", "TriggerMode", "DeadType", "DeadValue",	
                   "UANodePath"
        ]
        #固定数据
        fixeddata1 = ["0","否","1000","0","0","0","是","否"]
        fixeddata2 = ["不记录","0","60"]
        fixeddata3 = ["0","0","","-1","1","0","0","0","0","0",""]
        #依据数据类型变化数据
        DataType_IODisc = ["","","","","","","",""]
        DataType_IOShort = ["32767","-32767","32767","-32767","","无","否","0"]
        DataType_IOFloat = ["1000000000","-1000000000","1000000000","-1000000000","","无","否","0"]

        self.rows = []
        count = 0
        for device_row in self.csv_data:
            code = device_row['设备代号']
            desc = device_row['设备描述']
            #拼接地址处理
            try:
                if user_inputs['device'] == "SIEMENS":
                    base_offset = float(device_row['拼接地址'])
                    
                else:
                    base_offset = device_row['拼接地址']
            except Exception as e:
                logger.warning(f"加载的文件中拼接地址和设备类型不匹配：{e}")
                messagebox.showwarning("警告", "加载的文件中拼接地址和设备类型不匹配")
                return
            #每个设备遍历模板数据
            for tpl in template_data:
                TagName = f"{code}{tpl['name']}"    #点名拼接
                Description = f"{desc}{tpl['desc']}"    #描述拼接   
                #数据类型相关数据处理      
                if tpl['type'] =="IOFloat":
                    DataType = DataType_IOFloat
                    ItemDataType = "FLOAT"
                elif tpl['type'] =="IOShort":
                    DataType = DataType_IOShort
                    ItemDataType = "SHORT"
                else:
                    DataType = DataType_IODisc
                    ItemDataType = "BIT"
                #链路相关数据处理
                if user_inputs['link'] == "COM":
                    ChannelName = f"{user_inputs['link']}{user_inputs['link_com']}"
                elif user_inputs['link'] == "以太网":
                    ChannelName = f"{user_inputs['link']}<{user_inputs['link_ip']}>"
                else:
                    ChannelName = ""
                #设备类型相关数据处理，主要是采集地址拼接
                if user_inputs['device'] == "SIEMENS":
                    if tpl['type'] == "IODisc":
                        ItemName = f"DB{user_inputs['db_num']}.{base_offset + float(tpl['address']):.1f}"
                    else:
                        ItemName = f"DB{user_inputs['db_num']}.{int(base_offset) + int(tpl['address'])}"
                    RegName = "DB"
                    RegType = "3"
                elif user_inputs['device'] == "AB":
                    if tpl['address'] != "":
                        ItemName = f"TAG{base_offset}.{tpl['address']}"
                    else:
                        ItemName = ""
                    RegName = "TAG"
                    RegType = "0"
                else:
                    ItemName = ""
                    RegName = ""
                    RegType = ""
                #是否启用设备分组处理
                if user_inputs['group_name_en'] == "启用":
                    group_name = f"{user_inputs['group_name']}.{code}"
                else:
                    group_name = user_inputs['group_name']
                #每行数据的变量部分
                row = [
                    int(user_inputs['start_id']) + count,
                    TagName,
                    Description,
                    "用户变量",
                    tpl['type'],
                    "",
                    ChannelName,
                    user_inputs['device_name'],
                    user_inputs['channeldriver'],
                    user_inputs['deviceseries'],
                    ItemName, 
                    RegName,
                    RegType,
                    ItemDataType,
                    tpl['access'],
                    group_name
                ]     
                #每行数据的固定数据插入
                row[5:5]=DataType
                row[18:18]=fixeddata1
                row[31:31]=fixeddata2
                row[35:35]=fixeddata3
                self.rows.append(row)
                count += 1

    def rows_bewgsed(self, template_data, user_inputs):
        """
        根据传入数据进行处理，并将数据写入headers和rows存储
        Args:
            template_data：读取的模板数据
            user_inputs：用户设定的数据
        """
        #表头
        self.headers = [";IO#FS0序号", "所属通道", "驱动", "所属设备", "点类型",
                   "点名", "描述", "初始值", "单位编码", "引用(云)标签",
                   "提交", "标记", "值域", "权限", "采集周期",
                   "n[0]", "n[1]", "n[2]", "n[3]", "n[4]", "n[5]", "n[6]", "n[7]", "n[8]", "n[9]", "n[10]", "n[11]", 
                   "s[0]", "s[1]", "s[2]", "s[3]", "s[4]", "s[5]", "s[6]", "s[7]", "s[8]", "s[9]", "s[10]", "s[11]", 
                   "opc.vt", "opc.item", "opc.acc", "io.kind", "io.mode", "io.obj",
                   "io.path", "模拟量>>>取绝对值", "CTPT", "系数标记", "系数倍率",
                   "基数", "基础倍率", "阈值开关", "阈值", "量程变换", 
                   "裸数据上限","裸数据下限", "量程上限", "量程下限", "数字量>>>采集取反", 
                   "真值描述", "假值描述", "防抖周期"
        ]
        #固定数据
        fixeddata2 = ["","","","0","0","0","0","1000","3"]
        fixeddata3 = ["0","0","0","0","0","0","0","","","","","","","","","","","","","0","","","0","0","","","0","0","0","0","0","1","0"]
        #依据数据类型变化数据
        DataType_1 = ["0","1","1000000000","0","1000000000","0","0","合","分","0"]
        DataType_2 = ["0.001","0","100","0","1000","0","0","","","0"]

        self.rows = []
        count = 0
        for device_row in self.csv_data:
            code = device_row['设备代号']
            desc = device_row['设备描述']
            #拼接地址处理
            if user_inputs['device'] == "SIEMENS":
                base_offset = int(device_row['拼接地址'])
            else:
                base_offset = device_row['拼接地址']
            #每个设备遍历模板数据
            for tpl in template_data:
                TagName = f"{code}{tpl['name']}"    #点名拼接
                Description = f"{desc}{tpl['desc']}"    #描述拼接   
                #数据类型相关数据处理      
                if tpl['type'] =="1":
                    DataType = DataType_1
                elif tpl['type'] =="2":
                    DataType = DataType_2      
                else:
                    DataType = ["","","","","","","","","",""]
                #设备类型相关数据处理，主要是采集地址拼接
                if user_inputs['device'] == "SIEMENS":
                    n1 = int(base_offset) + int(tpl['addbyte'])
                    n2 = user_inputs['db_num']
                    if tpl['type'] == "2":
                        n3 ="0"
                        n4 = tpl['addbit']
                    else:
                        n3 = "7"
                        n4 = "0"
                elif user_inputs['device'] == "AB":
                    n1 = int(base_offset) + int(tpl['addbyte'])
                    n2 = user_inputs['db_num']
                    if tpl['type'] == "2":
                        n3 ="0"
                        n4 = tpl['addbit']
                    else:
                        n3 = "7"
                        n4 = tpl['addbit']
                else:
                    n3 = ""
                    n4 = ""

                #每行数据的变量部分
                row = [
                    "",
                    user_inputs['channel'],
                    user_inputs['drive'],
                    user_inputs['dev_name'],
                    tpl['type'],
                    TagName,
                    Description,
                    n1, 
                    n2,
                    n3,
                    n4,
                    
                ]     
                #每行数据的固定数据插入
                row[7:7]=fixeddata2
                row[21:21]=fixeddata3    
                row[55:55]=DataType             
                self.rows.append(row)
                count += 1