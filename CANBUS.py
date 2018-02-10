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
		if "JBT"==type:
			data = [data for data in canbus_data.strip().split()]
			self.data = data[1:-1]
			self.ID = data[0]
			self.time = data[-1]
			self.framelen = self.get_framelen()
			self.keyword = self.get_keyword()
		else:
			self.data = None
			self.time = None
			self.ID = None
			self.framelen = None
			self.keyword = None
		self.NO = None  # 序列号后续再赋值

	def set_NO(self, NO):
		self.NO = NO

	def get_framelen(self):
		if 0x10==(self.data[0]&0x10):
			framelen = ((self.data[0]&0xf)<<8)|self.data[1]
		elif (0x20!=(self.data[0]&0x20)) and (0x30!=(self.data[0]&0x30)) and (self.data[0]>0) and (self.data[0]<8):
			framelen = self.data[0]
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

		self.get_relations_form_file(file_path)
		pass

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


if __name__ == "__main__":
	aa = CANBUS_RELATIONSHIP(None, r"D:\JBT\DATA_PRO\3L_CAN\canid_V3.ini")

	pass
