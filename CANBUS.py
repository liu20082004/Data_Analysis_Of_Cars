#-*- coding: utf-8 -*-
import string
import time
from lxml import etree
import os
import os.path

class CANBUS_DATA():
	"""
	CANBUS的数据类
	canbus_data: 根据金奔腾收数小板的数据格式,传入字符串
	"""

	def __init__(self, canbus_data, type):
		self.is_canbus_data = False
		if "JBT"==type:
			data = [data for data in canbus_data.strip().split() if len(canbus_data.strip().split()) > 2]
			if data:
				if '.' not in data[-1]:  # 处理最后一帧不带时间参数的细节
					self.time = None
					self.data = data[1:]
				else:
					self.data = data[1:-1]
					self.time = data[-1]
				self.ID = data[0]
				self.framelen = self.get_framelen()
				self.keyword = self.get_keyword()
				self.is_canbus_data = True
		else:
			self.data = None
			self.time = None
			self.ID = None
			self.framelen = None
			self.keyword = None
		self.NO = None  # 序列号后续再赋值
		self.flag = None  # 收发属性,其实相对于总线来说,没有收发的关系,只有是否符合滤波规则这一条

	def set_flag(self, flag):
		self.flag = flag

	def set_NO(self, NO):
		self.NO = NO

	def get_framelen(self):
		data1 = int(self.data[0],16)
		data2 = int(self.data[1],16)
		if 0x10 == (data1 & 0x10):
			framelen = ((data1 & 0xf) << 8) | data2
		elif (0x20 != (data1 & 0x20)) and (0x30 != (data1 & 0x30)) and (data1 > 0) and (data1 < 8):
			framelen = data1
		else:
			framelen = None
		return framelen

	def get_keyword(self):
		if not self.framelen:
			keyword = None
		elif self.framelen<8:
			keyword = self.data[1]
		else:
			keyword = self.data[2]
		return keyword


class CANBUS_FILTER():
	"""CAN滤波配置"""

	def __init__(self, send, recv):
		self.send = send
		self.recv = recv


class CAR_SYSTEM():
	"""车型系统"""

	def __init__(self, system_name, filters):
		self.system_name = system_name
		self.filters = filters


class CAR():
	"""系统"""

	def __init__(self, car_name, systems):
		self.car_name = car_name
		self.systems = systems


class CANBUS_RELATIONSHIP():
	"""
	CANBUS的ID关系类
	传入关系表,初始化类属性
	类方法用来处理 CANBUS_DATA 的数据, 生成对应的数据关系  (这个表述有点模糊啊...比较难写)
	"""

	def __init__(self, canbus_data_list, file_path):
		"""
		1.先生成数据关系(从文本中读取),再处理数据
		:param canbus_data_list:
		"""

		self.filter, self.cars, self.common_id = self.get_relations_form_file(file_path)
		# self.send_id, self.recv_id, self.unknown_id = self.get_relations_of_canbus_data()
		pass

	def get_relationship_by_known(self, canbus_datas):

		canbus_frist_datas = self.get_all_frist_canbus_data(canbus_datas)
		frist_data = CANBUS_DATA()
		for canbus_frist_data in canbus_frist_datas:
			pass

		pass

	def check_id_by_car_relationship(self, ids):
		"""此函数用于统计id的命中情况"""
		send_ids = []
		recv_ids = []

		for id in ids:
			for cars in self.cars:
				for system in cars.systems:
					pass
		return send_ids, recv_ids


	def get_all_id(self, canbus_datas):
		ids = []
		for canbus_data in canbus_datas:
			if canbus_data.ID not in ids:
				ids.append(canbus_data.ID)
		return ids

	def get_all_frist_canbus_data(self, canbus_datas):
		"""获得起始数据"""
		canbus_frist_datas = [ canbus_data for canbus_data in canbus_datas if canbus_data.framelen ]
		return canbus_frist_datas

	def get_relationship_by_filter(self):
		return self.filter

	def get_relations_form_file(self, file_path):
		"""
		从file_path中获取关系表,如果没有,则在当前目录下查找
		:return: [Filter, Cars, Common_IDs]
		"""

		try:
			datas = etree.parse(file_path)
		except IOError, e:
			cur_path = os.getcwd()
			file_path = os.path.join(cur_path, "canid.ini")
			try:
				datas = etree.parse(file_path)
			except IOError, e:
				return None
		# datas = etree.HTML(file_datas)  #为什么使用HTML不行,而parse就可以?

		# 得到滤波设置
		filter_send = datas.xpath("//filter/Send/text()")
		filter_recv = datas.xpath("//filter/Recv/text()")
		Filter = [filter_send[0].split(','),filter_recv[0].split(',')]

		# 得到专车ID
		Cars = []
		Car_Types = datas.xpath("//Car_Type")
		for Car_Type in Car_Types:
			Car_Name = Car_Type.xpath(".//@car_name")
			Car_Systems = []
			Car_AllSystems = Car_Type.xpath(".//System")
			for Car_EachSystem in Car_AllSystems:
				System_Name = Car_EachSystem.xpath(".//@sys_name")
				Filter_Send = Car_EachSystem.xpath(".//Send/text()")[0].split(',')
				Filter_Recv = Car_EachSystem.xpath(".//Recv/text()")[0].split(',')
				filter = CANBUS_FILTER(Filter_Send, Filter_Recv)
				Car_System = CAR_SYSTEM(System_Name, filter)
				Car_Systems.append(Car_System)
			Car = CAR(Car_Name, Car_Systems)
			Cars.append(Car)

		# 公共ID
		Common_IDs = datas.xpath("//Common_ID//Send//text()")[0].strip('\n').strip('\t').split(',')
		return [Filter, Cars, Common_IDs]


def test_for_common_id():
	"""用于测试公共id"""
	aa = CANBUS_RELATIONSHIP(None, r"D:\JBT\DATA_PRO\3L_CAN\canid_V3.ini")

	filelines = open(r"D:\JBT\DATA_PRO\3L_CAN\untitle.txt", "r").readlines()
	canbus_datalist = [CANBUS_DATA(eachline, "JBT") for eachline in filelines if CANBUS_DATA(eachline, "JBT").is_canbus_data]
	canbus_datalist_and_flag = []
	for each_data in canbus_datalist:
		if each_data.ID in aa.common_id:
			each_data.set_flag("Send")
		else:
			each_data.set_flag("Unknow")
		canbus_datalist_and_flag.append(each_data)

	out_data = ''
	Count = 0
	for each_data in canbus_datalist_and_flag:
		if each_data.flag == "Send":
			if Count < 40:
				out_data += '\n'
			Count = 0
		elif Count < 40:
			out_data += ' ' * (40 - Count)
			Count = 40
		else:
			out_data += ' ' * 40

		out_data += each_data.ID + ' '
		Count += 1 + len(each_data.ID)
		for data in each_data.data:
			out_data += data + ' '
		Count += 3 * len(each_data.data)

		if Count > 40:
			out_data += '\n'



	outfile = open(r"D:\JBT\DATA_PRO\3L_CAN\OUT.ASM", "w")
	outfile.write(out_data)
	outfile.close()


def test_for_filter(inifile, infile, outfile):
	"""用于测试滤波设置"""

	print "正在初始化..."
	relationship = CANBUS_RELATIONSHIP(None, inifile)
	filelines = open(infile, "r").readlines()

	print "正在分析数据..."
	canbus_datalist = [CANBUS_DATA(eachline, "JBT") for eachline in filelines if CANBUS_DATA(eachline, "JBT").is_canbus_data]
	canbus_datalist_and_flag = []
	for each_data in canbus_datalist:
		if each_data.ID in relationship.filter[0]:
			each_data.set_flag("Send")
		elif each_data.ID in relationship.filter[1]:
			each_data.set_flag("Recv")
		else:
			each_data.set_flag("Unknow")
		canbus_datalist_and_flag.append(each_data)

	print "正在整理数据..."
	out_data = ''
	Count = 0
	Found_flag = False
	for each_data in canbus_datalist_and_flag:
		if each_data.flag == "Send":
			if Count < 40:
				out_data += '\n'
			Count = 0
			Found_flag = True
		elif each_data.flag == "Recv":
			if Count <= 40:
				out_data += ' ' * (40 - Count)
			else:
				out_data += ' ' * 40
			Count = 40
			Found_flag = True

		if Found_flag:
			out_data += each_data.ID + ' '
			Count += 1 + len(each_data.ID)
			for data in each_data.data:
				out_data += data + ' '
			Count += 3 * len(each_data.data)

			if Count > 40:
				out_data += '\n'
			Found_flag = False

	print "正在保存数据..."
	outfile = open(outfile, "w")
	outfile.write(out_data)
	outfile.close()
	print "处理完成!"


if __name__ == "__main__":

	ini_file_path = r"D:\JBT\DATA_PRO\3L_CAN\canid_V3.ini"
	org_file_path = r"D:\JBT\DATA_PRO\3L_CAN\untitle.txt"
	out_file_path = r"D:\JBT\DATA_PRO\3L_CAN\OUT.ASM"

	test_for_filter(ini_file_path, org_file_path, out_file_path)





	pass
