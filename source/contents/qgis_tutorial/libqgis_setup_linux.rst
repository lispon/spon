Linux 下搭建 QGIS 二次开发环境
================================================================================

.. include:: /other/linux_version_note/using_debian11.rst

如果软件源内有软件包, 那么 linux 下安装软件包就比较简单了:

``sudo apt install libqgis-dev -y`` 自动安装.

.. note::
    此时, 安装的是 ``3.10.14`` 版本的 QGIS, 如果需要其他版本的 QGIS, 请自行编译源码及依赖 或者 更换其他 Linux 的发行版. 这里给出 所有 Debian 系统下的 `libqgis-dev <https://packages.debian.org/search?keywords=libqgis-dev&searchon=names&suite=all&section=all>`_ 版本的查看链接. 可以看到, Debian 官网软件包内的 QGIS 版本仅包含长期支持版, 且是 `old ltr`.


使用 Debian-bakports 源安装 QGIS-3.16.14
--------------------------------------------------------------------------------

经查证, Debian 11 (bullseye) 的 backports 源中已经包含了 QGIS-3.16.14 的开发环境包.

#. 首先确定 ``/etc/apt/source.list`` 文件中是否包含 ``bullseyebackports`` 行; 如果未包含, 则添加 ``deb https://mirrors.bfsu.edu.cn/debian/ bullseye-backports main contrib non-free``

#. Debian 中查看 ``libqgis-dev`` 的所有版本. ``apt show -a libqgis-dev``, 或 ``apt-cache madison libqgis``, 前者输出详细信息, 后者仅输出版本号及源地址, 得到最新的 libqgis-dev 的版本号为 ``3.16.14+dfsg-1~bpo11+1``.

#. 安装 ``libqgis-dev`` 的 **3.16.14** 版本, ``sudo apt install libqgis-dev=3.16.14+dfsg-1~bpo11+1``; 如果之前已经安装了 **3.10** 版本的软件包, 可以先删除后安装.

#. 安装 ``qgis`` **3.16.14** 版本, 安装过程中, 可能会出现 ``以下软件包有为满足的依赖关系: 依赖python3-qgis...但是正要不安装...``; 同理, 请先安装好 ``3.16.14+dfsg-1~bpo11+1`` 的软件包, 然后再安装 ``qgis``.

.. note::
    例如, 如果提示 ``qgis-common (=3.16.14+dfsg-1~bpo11+1) 但是 3.10.14+dfsg-1 正要被安装``, 那么, 手动安装 ``sudo apt install qgis-common=3.16.14+dfsg-1~bpo11+1``. 假设, 如果在安装 ``qgis-common`` 时, 仍出现 **libx 但是 xx版本正要被安装** 的问题, 同理, 请首先安装 ``libx=3.16.14+dfsg-1~bpo11+1`` 软件包.
