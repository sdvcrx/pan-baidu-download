pan-baidu-download
==================

百度网盘下载脚本

** 正在准备新版 **

### 要求

- 无需会员，只需要百度网盘的分享地址即可

- python2.7

- aria2


## 特性

- 断点续传

- 最大下载速度限制

- 多线程（默认为5）：基本可以达到宽带的满速

- 无需登录

## Quick start

下载

    ./panbaidu.py pan-baidu-url

限速 `NUM kb` 下载

    ./panbaidu.py --max-download-limit=500k pan-baidu-url

下载多个文件

    ./panbaidu.py pan-baidu-url1 pan-baidu-url2 pan-baidu-url3 ...

停止 `<Ctrl> + C`

继续下载

    ./panbaidu.py pan-baidu-url


## 使用指南

    git clone git@github.com:banbanchs/pan-baidu-download.git
    cd pan-baidu-download
    ./panbaidu.py pan-baidu-url

`pan-baidu-url`格式为`http://pan.baidu.com/share/link?uk=数字&shareid=数字`

## 离线下载

百度网盘提供离线下载功能，仅能下载http/ftp/bt链接的文件，等待下载完毕后点击文件->创建公开链接，复制链接再用本工具下载

==========

### 为什么会有这个工具

chrome下载大文件时有可能会断开，而且速度不太理想

### TODO

- ~~下载速度限制~~

- 指定下载目录

- 从文件中读取链接并下载

- 下载自己分享页面的文件

- 编码完善

### 已知问题

编码不是utf-8时下载的文件名可能会乱码，window可能会乱码（未测试）

请发issue并附上你的系统，编码

### 不会支持或较难支持的功能

- 添加离线任务（离线功能比较鸡肋）

- more

## 感谢

[榨干百度网盘计划](http://daimajia.duapp.com/)

[xuanqinanhai/bleed-baidu-white](https://github.com/xuanqinanhai/bleed-baidu-white)
