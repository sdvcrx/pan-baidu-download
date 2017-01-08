#!/usr/bin/env python2
# coding=utf-8
from __future__ import print_function

import json
import requests

from config import global_config
from bddown_core import Pan, GetFilenameError
from util import logger


def export(links):
    pan = Pan()
    for link in links:
        infos = pan.get_file_infos(link)
        for info in infos:
            if not info.filename and not info.dlink:
                raise GetFilenameError("无法获取下载地址或文件名！")
            export_single(info.filename, info.dlink)


def export_single(filename, link):
    jsonrpc_path = global_config.jsonrpc
    jsonrpc_user = global_config.jsonrpc_user
    jsonrpc_pass = global_config.jsonrpc_pass
    if not jsonrpc_path:
        print("请设置config.ini中的jsonrpc选项")
        exit(1)
    jsonreq = json.dumps(
        [{
            "jsonrpc": "2.0",
            "method": "aria2.addUri",
            "id": "qwer",
            "params": [
                [link],
                {
                    "out": filename,
                    "header": "User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0"
                              "\r\nReferer:http://pan.baidu.com/disk/home"
                }]
        }]
    )
    try:
        if jsonrpc_user and jsonrpc_pass:
            response = requests.post(url=jsonrpc_path, data=jsonreq, auth=(jsonrpc_user, jsonrpc_pass))
        else:
            response = requests.post(url=jsonrpc_path, data=jsonreq)
        logger.debug(response.text, extra={"type": "jsonreq", "method": "POST"})
    except requests.ConnectionError as urle:
        print(urle)
        raise JsonrpcError("jsonrpc无法连接，请检查jsonrpc地址是否有误！")
    if response.ok:
        print("已成功添加到jsonrpc\n")


class JsonrpcError(Exception):
    pass
