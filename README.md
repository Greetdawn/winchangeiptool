
![image-20210317163146883](https://gitee.com/greetdawn/blogImages/raw/master/img/image-20210317163146883.png)

### 场景说明

公司经常会举办相关线下的安全的竞赛，支撑竞赛过程中经常遇到测试网络环境及靶机环境是否正常，此过程需要不断修改主机的IP地址。所以开发对应小工具来简化相关操作流程。功能较为简陋，只是简单的相关实现。



### 基本架构

pyqt + python + win 模块实现

只能运行windows操作系统平台



### 功能介绍

#### 1 对应网卡选择及地址查询

![image-20210317154103056](https://gitee.com/greetdawn/blogImages/raw/master/img/image-20210317154103056.png)

![image-20210317154131522](https://gitee.com/greetdawn/blogImages/raw/master/img/image-20210317154131522.png)

#### 2 静态地址设置

支持手动ip地址输入静态配置，网关可为空

![image-20210317154431196](https://gitee.com/greetdawn/blogImages/raw/master/img/image-20210317154431196.png)



#### 3 网络地址位增 1 减 1

目前只实现了24位掩码网络位地址增1减1功能

![image-20210317154824995](https://gitee.com/greetdawn/blogImages/raw/master/img/image-20210317154824995.png)

#### 4 一键DHCP功能

静态地址配置完成后，可实现一键环境网卡的dhcp功能

![image-20210317154945471](https://gitee.com/greetdawn/blogImages/raw/master/img/image-20210317154945471.png)



#### 5 简单web请求

输入对应的ip地址可实现简单web请求功能，返回对应网页的状态码及原始页面内容。用于简单判断目标网站能否正常访问

![image-20210317155206691](https://gitee.com/greetdawn/blogImages/raw/master/img/image-20210317155206691.png)



























