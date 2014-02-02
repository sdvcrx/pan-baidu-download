pan-baidu-download
==================

百度网盘下载脚本

**更新记录：**

[14-02-02]

添加导出到Aria2 JsonRPC

*慎用此功能，获取到的链接有可能会因时间过长而失效*

[14-01-24]

已支持登录！请在 config.ini 中填写帐号密码或使用 `pan config username [Your username]` 和 `pan config password [password]` 填入帐号密码，并用 `pan login` 进行登录

 在浏览器打开验证码功能已经移除，暂时不支持多文件下载

[13-12-24]

限速的问题好像解决了，在我这里测试能到满速

[参考链接](http://userscripts.org/topics/136081)

### 要求

- 百度网盘的分享地址

- python2.7

- aria2


## 特性

- 断点续传

- 最大下载速度限制

- 多线程（默认为5）

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

登录

    pan login [username] [password]

or

    pan config username XXXX (your username and password)
    pan config password 12345
	pan login

限速 `NUM kb` 下载

    pan download --limit=500k pan-baidu-url ...

指定下载目录

    pan download --output-dir=/home/memory/Downloads pan-baidu-url ...

下载多个链接

    pan download pan-baidu-url1 pan-baidu-url2 pan-baidu-url3 ...

停止 `<Ctrl> + C`

继续下载

    pan download pan-baidu-url ...

JsonRPC

    pan export pan-baidu-url ...

显示下载链接

    pan show pan-baidu-url ...

帮助

    pan -h
    pan help [login | download | show | help | config]

配置config

    pan config
    pan config username XXXX
    pan config passwd 123456
    pan config limit 500k
    pan config dir ~/Downloads/

## 使用指南

    git clone git@github.com:banbanchs/pan-baidu-download.git
    cd pan-baidu-download
    python bddown_cli.py download [Baidu Pan url]


## 测试环境

在此环境下测试通过

```
$ uname -a
Linux banbanchs 3.12.8-1-ARCH #1 SMP PREEMPT Thu Jan 16 09:16:34 CET 2014 x86_64 GNU/Linux
$ aria2c --version
aria2 version 1.18.3
$ python -V
Python 2.7.6
$ date -I
2014-01-24
```


==========

### TODO

- ~~下载速度限制~~

- ~~指定下载目录~~

- ~~配置文件支持~~

- 编码完善

- Windows7支持

- 列出自己网盘的文件

### 已知问题

- 登录时还不支持输入验证码，可能出现登录错误

- 编码不是utf-8时下载的文件名可能会乱码，window可能会乱码（未测试）

请发issue并附上你的系统，编码

### 不会支持或较难支持的功能

- 添加分享，删除分享，添加任务等等

- more

**此文档未完成**

## 感谢

[迅雷离线下载脚本 iambus/xunlei-lixian](https://github.com/iambus/xunlei-lixian)
有很多代码参(chao)考(xi)了`xunlei-lixian`，在此再次对作者表示感谢

[榨干百度网盘计划 xuanqinanhai/bleed-baidu-white](https://github.com/xuanqinanhai/bleed-baidu-white)


