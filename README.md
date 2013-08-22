pan-baidu-download
==================

百度网盘下载脚本

### 要求

- 无需会员，只需要百度网盘的分享地址即可

- python2.7

- aria2

==================

## Quick start

下载

    ./panbaidu.py pan-baidu-url

停止 `<Ctrl>+C`

继续下载

    ./panbaidu.py pan-baidu-url

==================

## 使用指南

    git clone git@github.com:banbanchs/pan-baidu-download.git
    cd pan-baidu-download
    ./panbaidu.py pan-baidu-url

`pan-baidu-url`格式为`http://pan.baidu.com/share/link?uk=数字&shareid=数字`

==================

## 特性

- 断点续传

- 多线程（默认为5）

- 无需登录

==================

## 实例

      ./panbaidu.py http://pan.baidu.com/share/link?uk=3943531277&shareid=4288212096
      
==================

## 感谢

[榨干百度网盘计划](http://daimajia.duapp.com/)

[xuanqinanhai/bleed-baidu-white](https://github.com/xuanqinanhai/bleed-baidu-white)
