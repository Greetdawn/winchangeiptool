#!/usr/local/env python3
# -*- coding: utf-8 -*-
# author: greetdawn
# data: 2021-03-02

from __future__ import print_function
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from changipwin import Ui_ChangIP

import wmi
import requests
import urllib.parse
import ctypes


class MyMainForm(QMainWindow, Ui_ChangIP):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)

        # 实例化网卡配置信息对象
        self.wmiService = wmi.WMI()
        self.colNicConfigs = self.wmiService.Win32_NetworkAdapterConfiguration(IPEnabled=True)

        # 各类函数调用
        self.generate_network_adapter_list()
        self.networkcomboBox.activated.connect(self.get_network_adapter_information)

        self.hostupButton.clicked.connect(self.config_add_one)
        self.hostdownButton.clicked.connect(self.config_down_one)

        self.staticButton.clicked.connect(self.config_static_network_ip_address)
        self.dhcpButton.clicked.connect(self.config_dhcp_network_ip_address)

        self.requestButton.clicked.connect(self.get_web_status)


    # 用于下拉框选项内容的填充
    def generate_network_adapter_list(self):
        if len(self.colNicConfigs) < 1:
            self.resultBrowser.append("没有找到合适的网卡适配器选项")
        for i in range(len(self.colNicConfigs)):
            # print(self.colNicConfigs[i].Description)
            self.networkcomboBox.addItem(str(i) + ' ' + self.colNicConfigs[i].Description)

    # 获取下拉框信号传递的网卡名
    # 获取对应网卡名的网络配置信息
    def get_network_adapter_information(self):
        self.resultBrowser.clear()
        try:
            if int(self.networkcomboBox.currentIndex()) > 0:
                NetID = self.networkcomboBox.currentIndex() - 1
                self.resultBrowser.append("网卡: " + self.colNicConfigs[NetID].Description + '\n' + \
                                          "地址: " + self.colNicConfigs[NetID].IPAddress[0] + '\n' + \
                                          "掩码: " + self.colNicConfigs[NetID].IPSubnet[0] + '\n')
            else:
                self.resultBrowser.append("请选择需要修改的网卡")
        except Exception as e:
            self.resultBrowser.append("选择网卡不可用,请重新选择")

    """
        对参数设置输入框中的三个参数进行判断
            条件1： 判断每一位是否为空字符
            条件2： 判断每一位非空数值是否在[0,255]之间
    """
    def parameter_judgment(self, variable):
        for i in range(4):
            if variable[i] == '':
                return False
            else:
                if 0 <= int(variable[i]) <= 255:
                    pass
                else:
                    return False
        return True

    # 获取用户修改参数的输入
    # 进行静态ip地址修改
    def config_static_network_ip_address(self):
        self.resultBrowser.clear()
        NetID = self.networkcomboBox.currentIndex() - 1
        ip_list = self.IP.text().split('.')
        netmask_list = self.NETMASK.text().split('.')
        gateway_list = self.GATEWAY.text().split('.')
        if NetID == -1:
            self.resultBrowser.append("请先选择需要修改的网卡")
        else:
            if self.parameter_judgment(ip_list):
                if self.parameter_judgment(netmask_list):
                    if self.parameter_judgment(gateway_list):
                        returnValue1 = self.colNicConfigs[NetID].EnableStatic(IPAddress=[self.IP.text()], SubnetMask=[self.NETMASK.text()])
                        returnValue2 = self.colNicConfigs[NetID].SetGateways(DefaultIPGateway=[self.GATEWAY.text()],
                                                                             GatewayCostMetric=[1])
                        if returnValue1[0] == 0 or returnValue1[0] == 1:
                            if returnValue2[0] == 0 or returnValue2[0] == 1:
                                self.resultBrowser.append("网卡: " + self.colNicConfigs[NetID].Description + '\n' + \
                                                          "已成功修改为:" + '\n' + \
                                                          "地址: " + self.IP.text() + '\n' + \
                                                          "掩码: " + self.NETMASK.text() + '\n' + \
                                                          "网关: " + self.GATEWAY.text() + '\n')
                            else:
                                self.resultBrowser.append('网关修改失败，请重新尝试')
                    else:
                        returnValue = self.colNicConfigs[NetID].EnableStatic(IPAddress=[self.IP.text()], SubnetMask=[self.NETMASK.text()])
                        if returnValue[0] == 0 or returnValue[0] == 1:
                            self.resultBrowser.append("网卡: " + self.colNicConfigs[NetID].Description + '\n' + \
                                                      "已成功修改为:" + '\n' + \
                                                      "地址: " + self.IP.text() + '\n' + \
                                                      "掩码: " + self.NETMASK.text() + '\n')
                        else:
                            self.resultBrowser.append('地址和掩码修改失败，请重新尝试')
                else:
                    self.resultBrowser.append('输入的掩码地址格式有误，请重新输入')
            else:
                self.resultBrowser.append('输入的ip地址格式有误，请重新输入')

    # 设置动态ip地址获取
    def config_dhcp_network_ip_address(self):
        self.resultBrowser.clear()
        NetID = self.networkcomboBox.currentIndex() - 1
        if NetID == -1:
            self.resultBrowser.append("请先选择需要修改的网卡")
        else:
            retunValue1 = self.colNicConfigs[NetID].EnableDHCP()
            retunValue2 = self.colNicConfigs[NetID].SetDNSServerSearchOrder()
            if (retunValue1[0] == 0 or retunValue1[0] == 1) and \
                (retunValue2[0] == 0 or retunValue2[0] == 1):
                self.resultBrowser.append("网卡: " + self.colNicConfigs[NetID].Description + '\n' + \
                                              "设置自动获取IP地址成功" + '\n')
            else:
                self.resultBrowser.append("网卡: " + self.colNicConfigs[NetID].Description + '\n' + \
                                          "设置自动获取IP地址失败" + '\n')

    # 定义网络位地址加 1 功能
    def config_add_one(self):
        self.resultBrowser.clear()
        NetID = self.networkcomboBox.currentIndex() - 1
        ip_list = self.IP.text().split('.')
        netmask_list = self.NETMASK.text().split('.')
        gateway_list = self.GATEWAY.text().split('.')
        try:
            if NetID == -1:
                self.resultBrowser.append("请先选择需要修改的网卡")
            else:
                if self.parameter_judgment(ip_list):
                    if self.parameter_judgment(netmask_list):
                        if self.parameter_judgment(gateway_list):
                            newip = ip_list[0] + '.' + ip_list[1] + '.' + \
                                    str(int(ip_list[2]) + 1) + '.' + ip_list[3]
                            newgateway = gateway_list[0] + '.' + gateway_list[1] + '.' + \
                                         str(int(gateway_list[2]) + 1) + '.' + gateway_list[3]
                            self.IP.setText(newip)
                            self.GATEWAY.setText(newgateway)
                            returnValue1 = self.colNicConfigs[NetID].EnableStatic(IPAddress=[newip],
                                                                                  SubnetMask=[self.NETMASK.text()])
                            returnValue2 = self.colNicConfigs[NetID].SetGateways(DefaultIPGateway=[newgateway],
                                                                                 GatewayCostMetric=[1])
                            if returnValue1[0] == 0 or returnValue1[0] == 1:
                                if returnValue2[0] == 0 or returnValue2[0] == 1:
                                    self.resultBrowser.append("网卡: " + self.colNicConfigs[NetID].Description + '\n' + \
                                                              "已成功修改为:" + '\n' + \
                                                              "地址: " + newip + '\n' + \
                                                              "掩码: " + self.NETMASK.text() + '\n' + \
                                                              "网关: " + newgateway + '\n')
                                else:
                                    self.resultBrowser.append('网关修改失败，请重新尝试')
                        else:
                            newip = ip_list[0] + '.' + ip_list[1] + '.' + \
                                    str(int(ip_list[2]) + 1) + '.' + ip_list[3]
                            self.IP.setText(newip)
                            returnValue = self.colNicConfigs[NetID].EnableStatic(IPAddress=[newip],
                                                                                 SubnetMask=[self.NETMASK.text()])
                            if returnValue[0] == 0 or returnValue[0] == 1:
                                self.resultBrowser.append("网卡: " + self.colNicConfigs[NetID].Description + '\n' + \
                                                          "已成功修改为:" + '\n' + \
                                                          "地址: " + newip + '\n' + \
                                                          "掩码: " + self.NETMASK.text() + '\n')
                            else:
                                self.resultBrowser.append('地址和掩码修改失败，请重新尝试')
                    else:
                        self.resultBrowser.append('输入的掩码地址格式有误，请重新输入')
                else:
                    self.resultBrowser.append('输入的ip地址格式有误，请重新输入')
        except Exception as e:
            print(e)

    # 定义网络地址 减 1 功能
    def config_down_one(self):
        self.resultBrowser.clear()
        NetID = self.networkcomboBox.currentIndex() - 1
        ip_list = self.IP.text().split('.')
        netmask_list = self.NETMASK.text().split('.')
        gateway_list = self.GATEWAY.text().split('.')
        if NetID == -1:
            self.resultBrowser.append("请先选择需要修改的网卡")
        else:
            if self.parameter_judgment(ip_list):
                if self.parameter_judgment(netmask_list):
                    if self.parameter_judgment(gateway_list):
                        newip = ip_list[0] + '.' + ip_list[1] + '.' + \
                                str(int(ip_list[2]) - 1) + '.' + str(ip_list[3])
                        newgateway = gateway_list[0] + '.' + str(gateway_list[1]) + '.' + \
                                     str(int(gateway_list[2]) - 1) + '.' + str(gateway_list[3])
                        self.IP.setText(newip)
                        self.GATEWAY.setText(newgateway)
                        returnValue1 = self.colNicConfigs[NetID].EnableStatic(IPAddress=[newip],
                                                                              SubnetMask=[self.NETMASK.text()])
                        returnValue2 = self.colNicConfigs[NetID].SetGateways(DefaultIPGateway=[newgateway],
                                                                             GatewayCostMetric=[1])
                        if returnValue1[0] == 0 or returnValue1[0] == 1:
                            if returnValue2[0] == 0 or returnValue2[0] == 1:
                                self.resultBrowser.append("网卡: " + self.colNicConfigs[NetID].Description + '\n' + \
                                                          "已成功修改为:" + '\n' + \
                                                          "地址: " + newip + '\n' + \
                                                          "掩码: " + self.NETMASK.text() + '\n' + \
                                                          "网关: " + newgateway + '\n')
                            else:
                                self.resultBrowser.append('网关修改失败，请重新尝试')
                    else:
                        newip = ip_list[0] + '.' + ip_list[1] + '.' + \
                                str(int(ip_list[2]) - 1) + '.' + str(ip_list[3])
                        self.IP.setText(newip)
                        returnValue = self.colNicConfigs[NetID].EnableStatic(IPAddress=[newip],
                                                                             SubnetMask=[self.NETMASK.text()])
                        if returnValue[0] == 0 or returnValue[0] == 1:
                            self.resultBrowser.append("网卡: " + self.colNicConfigs[NetID].Description + '\n' + \
                                                      "已成功修改为:" + '\n' + \
                                                      "地址: " + newip + '\n' + \
                                                      "掩码: " + self.NETMASK.text() + '\n')
                        else:
                            self.resultBrowser.append('地址和掩码修改失败，请重新尝试')
                else:
                    self.resultBrowser.append('输入的掩码地址格式有误，请重新输入')
            else:
                self.resultBrowser.append('输入的ip地址格式有误，请重新输入')

    # 定义url解析函数
    def url_parse(self):
        self.requestBrowser.clear()
        req_url = self.URL.text()
        if req_url != '':
            urlparseresult = urllib.parse.urlparse(req_url)
            if urlparseresult.scheme == '':
                url = 'http://' + req_url
                return url
            else:
                return req_url
        else:
            self.requestBrowser.append('亲，你还没输地址~')
            return False

    # 定义简单的GET请求功能
    def get_web_status(self):
        self.requestBrowser.clear()
        req_type = self.reqtypecomboBox.currentText()
        if self.url_parse() != False:
            if req_type == 'GET':
                try:
                    resp = requests.get(url=self.url_parse(), timeout=1)
                    resp.encoding = 'utf-8'
                    resp_status = resp.status_code
                    resp_text = resp.text
                    self.requestBrowser.append("状态码：" + str(resp_status) + '\n' + \
                                               "-----------------------响应体-----------------------\n" + \
                                               resp_text)
                except Exception as e:
                    self.requestBrowser.append("亲，请求失败啦，请重新尝试呦~")
            else:
                self.requestBrowser.append("亲，POST功能正在开发中，敬请期待呦！")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":

    if is_admin():
        #固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
        app = QApplication(sys.argv)
        #初始化
        myWin = MyMainForm()
        #将窗口控件显示在屏幕上
        myWin.show()

        #程序运行，sys.exit方法确保程序完整退出。
        sys.exit(app.exec_())
    else:
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)