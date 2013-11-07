pan-baidu-download
==================

百度网盘下载脚本

### 要求

- 百度网盘的分享地址

- python2.7

- aria2


## 特性

- 断点续传

- 最大下载速度限制

- 多线程（默认为5）

- 单页面多文件下载（部分链接可能无效）

- 无需登录

## Quick start

下载

```
python bddown_cli.py download [options] [Baidupan-url]...

Options:
    --limit=[speed]             Max download speed limit.
    --output-dir=[dir]          Download task to dir.
```

    python bddown_cli.py download pan-baidu-url

限速 `NUM kb` 下载

    python bddown_cli.py --limit=500k download pan-baidu-url ...

指定下载目录

    python bddown_cli.py --output-dir=/home/memory/Downloads pan-baidu-url ...

下载多个链接

    python bddown_cli.py download pan-baidu-url1 pan-baidu-url2 pan-baidu-url3 ...

停止 `<Ctrl> + C`

继续下载

    python bddown_cli.py download pan-baidu-url ...
    
显示下载链接

    python bddown_cli.py show pan-baidu-url ...

帮助

    python bddown_cli.py -h
    python bddown_cli.py help [download|show|help]

**config功能暂未完成**

## 使用指南

    git clone git@github.com:banbanchs/pan-baidu-download.git
    cd pan-baidu-download
    python bddown_cli.py pan-baidu-url


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

- 配置文件支持

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


