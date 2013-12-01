pan-baidu-download
==================

百度网盘下载脚本

**验证码默认保存至代码目录下，暂时不支持多文件下载**

**若想改用web浏览器打开，可使用 `pan config save_code 0` 或修改 `config.ini` 中的 `save_vcode` 为0**

**到期末为止只保证其可用性，不添加新功能**

**百度对非登陆用户限速严重，将加入登陆功能**

### 要求

- 百度网盘的分享地址

- python2.7

- aria2


## 特性

- 断点续传

- 最大下载速度限制

- 多线程（默认为5）

- 无需登录

- 支持输入验证码

## 提示

linux下可使用以下命令减小敲键盘的数目

`~/bin` 需要添加到环境变量 `PATH`

```
ln -s 你的lixian_cli.py路径 ~/bin/pan
```

## Quick start

下载

```
pan download [options] [BaiduPan-url]...

Options:
    --limit=[speed]             Max download speed limit.
    --output-dir=[dir]          Download task to dir.
```

    pan download pan-baidu-url

限速 `NUM kb` 下载

    pan download --limit=500k pan-baidu-url ...

指定下载目录

    pan download --output-dir=/home/memory/Downloads pan-baidu-url ...

下载多个链接

    pan download pan-baidu-url1 pan-baidu-url2 pan-baidu-url3 ...

停止 `<Ctrl> + C`

继续下载

    pan download pan-baidu-url ...
    
显示下载链接

    pan show pan-baidu-url ...

帮助

    pan -h
    pan help [download|show|help]

配置config

    pan config
    pan config limit 500k
    pan config dir ~/Downloads/

## 使用指南

    git clone git@github.com:banbanchs/pan-baidu-download.git
    cd pan-baidu-download
    pan pan-baidu-url


## 测试环境

在此环境下测试通过

```
$ uname -a
Linux banbanchs 3.11.6-1-ARCH #1 SMP PREEMPT Fri Oct 18 23:22:36 CEST 2013 x86_64 GNU/Linux
$ aria2c --version
aria2 version 1.18.1
$ python -V
Python 2.7.5
$ date -I
2013-10-26
```


==========

### TODO

- ~~下载速度限制~~

- ~~指定下载目录~~

- 导出aria2下载链接

- ~~配置文件支持~~

- 编码完善

- Windows7支持

### 已知问题

编码不是utf-8时下载的文件名可能会乱码，window可能会乱码（未测试）

请发issue并附上你的系统，编码

### 不会支持或较难支持的功能

- 添加分享，删除分享，添加任务等等

- more

**此文档未完成**

## 感谢

[迅雷离线下载脚本 iambus/xunlei-lixian](https://github.com/iambus/xunlei-lixian)
有很多代码参(chao)考(xi)了`xunlei-lixian`，在此再次对作者表示感谢

[榨干百度网盘计划 xuanqinanhai/bleed-baidu-white](https://github.com/xuanqinanhai/bleed-baidu-white)


