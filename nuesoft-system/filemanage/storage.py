#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @CopyRight    : GuangZhou Hengxin Information Technology .,Co LTD
# @Author       : shankusu(pengyanfeng@datagzhx.com)
# @Date         : 2016/12/26
# @Version      : 0.0.1
# @Link         :

"默认注释"

from django.core.files.storage import FileSystemStorage

class ImageStorage(FileSystemStorage):
    from django.conf import settings

    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        # 初始化
        super(ImageStorage, self).__init__(location, base_url)

    # 重写 _save方法,这里的name为终极path+name
    def _save(self, name, content):
        import os, time
        # # 文件扩展名
        # ext = os.path.splitext(name)[1]
        # # 文件目录
        # d = os.path.dirname(name)
        # # 定义文件名
        # fn = str(int(time.time()*1000))
        # # 重写合成文件名
        # name = os.path.join(d, fn + ext)
        # 调用父类方法
        # print ">>>>>>>>>>>>>>>>>>ImageStorage._save:%s<<<<<<<<<<<<<<<<<<<<<" %(name)
        return super(ImageStorage, self)._save(name, content)
