Linux 下搭建 QGIS 二次开发环境
================================================================================

.. include:: /other/linux_version_note/using_debian11.rst

如果软件源内有软件包, 那么 linux 下安装软件包就比较简单了:

``sudo apt install libqgis-dev -y`` 自动安装.

.. note::
    此时, 安装的是 ``3.10.14`` 版本的 QGIS, 如果需要其他版本的 QGIS, 请自行编译源码及依赖 或者 更换其他 Linux 的发行版. 这里给出 所有 Debian 系统下的 `libqgis-dev <https://packages.debian.org/search?keywords=libqgis-dev&searchon=names&suite=all&section=all>`_ 版本的查看链接. 可以看到, Debian 官网软件包内的 QGIS 版本仅包含长期支持版, 且是 `old ltr`.