vlp16
--------------------------------------------------------------------------------

背景
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

vlp16 是 velodyne 公司推出的一款 16 线(channel)的激光雷达, 详情参数请查看 `官网 <https://ouster.com/products/hardware/vlp-16>`_.

.. note::
    在 2022 ~ 2023 年左右, Velodyne 和 Ouster 两家公司合并(`见该链接 <https://investors.ouster.com/news/news-details/2023/Ouster-and-Velodyne-Complete-Merger-of-Equals-to-Accelerate-Lidar-Adoption/default.aspx>`_), 同时 velodyne 的官网下线, 一些在线资料都已经无法找到了. 目前官网为 `https://ouster.com/ <https://ouster.com/>`_, 但是没有 velodyne 的相关资料的下载入口.

.. _`vlp16 user manual`: https://docs.clearpathrobotics.com/assets/files/clearpath_robotics_023729-TDS2-2c7454cf9f317be53ce1938dca7ddcf4.pdf

点击 `vlp16 user manual`_ 下载用户手册(来自网络搜索, 非官方下载地址, 仅供参考). 原始数据格式见 `用户手册第 9 章`

.. image:: images/vlp16-chapter9.png


首先我们需要大致了解激光雷达的基本原理.

激光发射器充电发射脉冲激光, 激光经过物体(距离记为 ``d``)反射, 经过 ``t`` 时间后被接收器接收;
那么可以得到公式: ``d = (s * t) / 2``, 其中 s 为光速. 使用下图中所示公式, 可以将 **极坐标系** 下的点坐标
转化成笛卡尔坐标系下的点坐标.

.. image:: images/vlp16-sensor_coordinate_system.png


简而言之, 我们需要获取每个点的 ``R``, ``α``, ``ω``. 其中:

- _`R` 表示为相对距离, 可以从原始数据中直接读取.
- _`α` 表示为激光发射时水平偏转角度, 可以从原始数据中读取.

    - 一般情况下, 激光雷达电机是匀速转动, 所以, ``α`` 与时间有个线性关系, 即已知原始 ``α``,
      可以通过时间偏移计算任意时刻的 ``α``.

- _`ω` 表示为激光发射时相对于安装平面的垂直偏转角度, 在正常工况下, 不会变化. 所以, 查 `vlp16 user manual`_ **Table 9-1** 即可.


数据通过 **网线(这里的网线并非 RJ45 接口, 而是 T1)** 传输. 如下图所示, 数据包长度为 1248 字节, 通过 udp 的 2368 端口发送.
其中包含 42 个 协议头; 即真正数据为 1206 字节: 12 个数据 block, 4 字节时间戳, 2 字节工厂标记.

.. image:: images/vlp16-data_packet_structure.png


这里, 引入一个名词: _`firing sequence`, 指激光雷达所有激光发射器依次充电发射接收一次的完整过程.
vlp16 执行一次 **firing sequence** 需要 **55.296 us**, 详情参考 `vlp16 user manual`_ **Chapter 8**.
每个激光点(channel)发射需要 **2.304 us**, 全部发送接收完成一次后, 需要休息 **18.432 us** (猜测留出时间来散热),
总计 ``2.304 * 16 + 18.432 = 55.296 us``
详情如下图所示:

.. image:: images/vlp16-firing_sequence_timing.png

基于此, 我们可以计算得到更多的信息(这里额外说明一下, 这里仅指单回波模式, 若双回波模式, 有些数据还需要翻倍):
- ``24 * 55.296 us= 1.327 ms``, 相邻 udp 报文中至少需要 1.327 ms 时间
- ``1 packet * 1 s / 1.327 ms = 753.5 packets/second``, 每秒可接收到 753.5 个报文, 一般使用 754
- ``753.5 * 1248 bytes = 940368 bytes/second = 918 KB/s``, 占用约 918 KB/s 带宽
- ``753.5 * (12 * 32) = 289344 laser measurements per second``

这里, 再引入一个通用名词 **RPM(rotation per minutes)**, 表示电机每分钟转动的圈数.
vlp16 RPM 范围为 **[300, 1200]**, 必须保证可以被 60 整除, 否则, 可能会出现问题.
由于激光雷达 **firing sequence** 是固定时间, 转速越高, 激光点水平间隔越大, 也就是分辨率越小.
用户手册指出, 当 RPM 为 300, 600, 900, 1200 时, 水平分辨率分别是 0.1°, 0.2°, 0.3°, 0.4°.
一般使用 RPM 600 即可.


原始数据 packet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
    这个所示的 **原始数据格式** 是指从直接 LiDAR 获取到的数据, 并非经过标准化的 **文件格式**.


下面直接给出 c++ 结构体来帮助理解数据格式, 强烈建议配合用户手册中的图表来理解.

.. code-block:: cpp

    struct Point {
        uint16_t distance;      // 距离
        uint8_t intensity;      // 回波强度
    };

    struct DataBlock {
        uint16_t flag;          // 固定为 0xFF, 0xEE 由于是小端存储, 所示应为 0xEEFF
        uint16_t azimuth;       // 方位角的角度值的 100 倍, 也就是说方位角精确到小数点后 2 位
        Point points[32];       // 每个点的方位角度都不同
    };

    struct Packet {
        // int8_t udp_header[42];   // 在实际 socket 编程中, header 头部由协议栈处理
        DataBlock block[12];
        uint64_t timestamp;         // 注意小端存储
        uint8_t mode;               // 模式
        uint8_t product;            // 产品 id. 0x22 表示 vlp16(也有可能表示 vlp16 的升级版 Puck LITE)
    }

.. _vlp16 sample data: https://data.kitware.com/#collection/5b7f46f98d777f06857cb206/folder/5b7fff608d777f06857cb539

在 **kitware data**, 我们找到一个公开的 vlp16 型号的原始数据 pcap 包的下载链接 `vlp16 sample data`_, pcap 文件可以使用 ``wireshark`` 打开, 如下图所示.

.. image:: images/vlp16_pcap_shot.png


- block[0].flag: ``ff ee``
- block[0].azimuth: ``cb 61``

  - 小端, 即 ``0x61cb = 25035``
  - ``25035 / 100 = 250.35 °`` (这里使用一个固定系数来将 ``float`` 转成 ``uint16_t`` 来减少数据量, 也常见于经纬度处理)

- block[0].points[0]: `84 06 2c`:

  - distance: ``84 06``

    - 小端, 即 ``0x0684 = 1668``
    - 分辨率 2 mm, 即 ``1668 * 2 mm = 3.336 m``

  - intensity: ``2c``:

.. note:: 计算过程也可参考用户手册 Figure 9-4 和 Figure 9-5


这样一来, 所有点的 `R`_ 值都可以获取到.


每个 ``DataBlock`` 中都包含 **32** 个点, 其分为两组, 每组 16 个点(**firing sequence**), 编号(索引)依次为 0~15.
有了索引编号(这里不需要关注发射时间), 根据上文中 `ω`_ 提到的方法, 查表获取所有点的 ``ω``.


最后, 我们计算最为复杂的 ``α``. 基本原理时, 电机匀速转动, 相邻两个 ``DataBlock`` 所有点(总共 64 个), 任意两点的 ``方位角差 / 时间差`` 是一个定值,
且这个定值可以通过 ``相邻两个 DataBlock 的方位角差 / 55.296 us`` 来计算(注意方位角差为负需要加上 360)得到.
如果已知所有点的时间和任意一点的方位角, 就可以求出所有点的方位角了. 每个 ``DataBlock`` 都有一个基准 ``azimuth``, 表示为第 ``0`` 个点的方位角(``azimuth``),

这里, 我们需要引入一个新的名词 **回波模式 (return mode)**,
详情参考 `vlp16 user manual`_ **6.2 Laser Return Modes**.

- 单回波模式: 最强(strongest), 最后(last)
- 双回波模式: 双回波(dual). 相对于单回波模式, 双回波模式下数据量翻倍.

.. image:: images/vlp16-laser_return_mode.png

单回波模式下, **firing sequence** 如下图所示.

.. image:: images/vlp16-signal_return_mode_data_structure.png

双回波模式下, **firing sequence** 如下图所示.

.. image:: images/vlp16-dual_return_mode_data_structure.png



在上文 `firing sequence`_ 可以看到, 由于存在 **18.432 us** 的 **散热** 时间, 不能简单的使用比例 ``55.296 / 16``.

- 单回波: ``DataBlock_azimuth_delta / 55.296 us = (Azimuth_i - Azimuth_0) / (k * 2.304 us); ( 0 <= i < 16)``
- 双回波: ``DataBlock_azimuth_delta / 55.296 us = (Azimuth_i - Azimuth_0) / ((k - 16) + 55.296) * 2.304 us); (16 <= i < 32)``

我们得到了每个点的 ``azimuth``, 也就是 `α`_. 我们可以计算得到所有点的坐标值(极坐标系),
并可以转换到激光雷达的笛卡尔坐标系下.
然后, 根据激光雷达的标定参数(激光雷达在车身坐标系的坐标)可将所有激光雷达点坐标转换到车身坐标系下.
至此, 可以将激光雷达点转换到其他与车身坐标系有转换关系的任何坐标系中.


.. note:: 再次想象一下激光雷达每个激光点的发射: 电机带动激光发射器水平方向匀速转动, 垂直不均匀分布的 16 个发射点依次间隔发射...


ros driver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

代码见: `https://github.com/ros-drivers/velodyne/tree/ros2 <https://github.com/ros-drivers/velodyne/tree/ros2>`_

.. note::
   #. 需要对 ros 的 msg 有一些初步的了解.
   #. 这里查看的是 ros2 的分支, 与 ros1 中的 msgs 定义有些区别.

.. note:: 当前 ros2 最新版本: jazzy, 默认支持 ubuntu-24.04, 支持到 2029年(humble 版本支持到 2027 年).

.. image:: images/ros_velodyne.png

#. **velodyne**: 使用命令行安装时(``sudo apt install ros-jazzy-velodyne``), 安装这个包就可以, 它依赖下面的四个包. 该包仅包含一些 **launch** 文件.
#. **velodyne_msgs**: 顾名思义, 定义了 velodyne 相关的 **msgs**.
#. **velodyne_driver**: 提供从 **pcap** 或 **socket** 读取激光雷达数据的节点, 发布类型为 **velodyne_msgs** 中定义的消息类型的数据. 仅做了一层数据封装.
#. **velodyne_pointcloud**: 订阅 **velodyne_msgs::msg::VelodyneScan**, 转换并发布 **sensor_msgs::msg::PointCloud2**.
#. **velodyne_laserscan**: 订阅 **sensor_msgs::msg::PointCloud2**, 转换并发布 **sensor_msgs::msg::LaserScan**.

.. mermaid::

    ---
    title: pkg velodyne driver 的大概流程图
    ---
    flowchart TD;
    pcap(pcap file) -- 1206 bytes --> velodyne_driver;
    socket(udp socket) -- 1206 bytes --> velodyne_driver;
    velodyne_driver -- velodyne_msgs::msg::VelodyneScan --> velodyne_pointcloud;
    velodyne_pointcloud -- sensor_msgs::msg::PointCloud2 --> velodyne_laserscan;
    velodyne_laserscan -- sensor_msgs::msg::LaserScan --> sub[/other Subscription/]


在开始分析 ``ros`` 中的实现之前, 我们先引入一个点云帧集(frame 或 _`scan`)的概念, 表示
激光雷达电机旋转一圈时, 所有的点云数据, 即 **包含多个 udp 报文**, 同时 **方位角差值为 360**.
这样, 使用激光雷达点云数据时, 就无需在考虑数据是否完整(是否缺少在某些方位时的数据), 从多个输入合并成单一输入.


velodyne_msgs
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

主要定义了两个 msg 类型, 使用数组将原始 udp 报文数据封装成 ``Packet``, 同时将多个 ``Packet`` 组合成 `scan`_.

.. code-block::
    :linenos:
    :emphasize-lines: 1,6

    #### VelodyneScan.msg
    # Velodyne LIDAR scan packets.
    std_msgs/Header header              # standard ROS message header
    VelodynePacket[] packets            # vector of raw packets

    #### VelodynePacket.msg
    # Raw Velodyne LIDAR packet.
    builtin_interfaces/Time stamp       # packet timestamp
    uint8[1206] data                    # packet contents


velodyne_driver
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. mermaid::

    ---
    title: velodyne driver 类图, 仅表示出主要部分.
    ---
    classDiagram
        VelodyneScan <.. Input
        Input <|.. InputSocket
        Input <|.. InputPCAP
        Input <-- VelodyneDriver
        Node <|-- VelodyneDriver
    namespace velodyne_msgs {
        %% note for VelodyneScan "msgs"
        class VelodyneScan
    }
    namespace velodyne_driver {
        class Input {
            <<Abstract>>
            +int getPacket()
        }
        class InputSocket {
            +setDeviceIP()
        }
        class InputPCAP {
            +setDeviceIP()
        }
        class VelodyneDriver {
            -pollThread()
            -poll()
        }
    }
    namespace rclcpp {
        class Node
    }


.. note:: InputPCAP 类 依赖 libpcap-dev, debian 下可以使用 sudo apt install libpcap-dev 安装依赖包.

.. _InputSocket\:\:getPacket: https://github.com/ros-drivers/velodyne/blob/ros2/velodyne_driver/src/lib/input.cpp#L159
.. _InputPCAP\:\:getPacket: https://github.com/ros-drivers/velodyne/blob/ros2/velodyne_driver/src/lib/input.cpp#L327
.. _VelodyneDriver\:\:poll: https://github.com/ros-drivers/velodyne/blob/ros2/velodyne_driver/src/driver/driver.cpp#L197


#. ``lib/input.cpp`` 中, `InputSocket::getPacket`_ 函数提供从 udp socket 中读取数据并写入到 ``VelodynePacket`` 中,
   `InputPCAP::getPacket`_ 函数提供从 ``pcap`` 文件中读取数据并将数据写入到 ``VelodynePacket`` 中.
#. ``driver/driver.cpp`` 中, 核心函数 `VelodyneDriver::poll`_, 通过调用 ``Input`` 基类指针获取数据.
   并提供两种组 `scan`_ 的方式, 可简称为 **报文数量法** 和 **方位角法** (暂不考虑名称的信达雅, 了解所表达意思即可).
   这两种方式可以通过参数 ``cut_angle`` 来设置, 单位 `deg`, 默认为 **报文数量法**.

   - **报文数量法**, 顾名思义, 接收到特定数量的报文后, 就认为激光雷达旋转了一圈, 组成了一个 ``scan``.
     默认激光雷达匀速转动, 点云数据稳定输出.
     这种方式计算量非常小, 主要用于激光雷达 RPM 较大时, 尽可能快的输出数据.
   - **方位角法**, 顾名思义, 从接收到的报文中解析方位角, 当方位角范围达到 360° 时输出.
     无论激光雷达是否匀速转动, 这种方式都可以保证输出的数据 *完整性*; 但是, 这种方式计算量较大,
     主要用于激光雷达 RPM 较小, 且对数据要求比较高时.

.. note::
    建议在阅读代码前, 了解一下 vlp16 的 `config <https://github.com/ros-drivers/velodyne/blob/ros2/velodyne_driver/config/VLP16-velodyne_driver_node-params.yaml>`_


#. 首先, 在 `vlp16 sample data`_ 下载 ``2014-11-10-10-36-54_Velodyne-VLP_10Hz-County Fair.pcap``.
#. 然后, 修改 ``config/VLP16-velodyne_driver_node-params.yaml`` 文件

    - *device ip* 修改为 ``192.168.1.200``
    - 新增 *pcap* 为 ``上一步下载的 pcap 文件存放在本地 pc 上的绝对路径``

#. 最后, 命令行 ``ros2 launch velodyne_driver velodyne_driver_node-VLP16-launch.py`` 运行
#. 可通过 ``ros2 topic list`` 看到 ``/velodyne_packets``, 也可以通过 ``ros2 bag record --topics /velodyne_packets`` 录制


velodyne pointcloud
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


首先了解一下 ros2 中 ``sensor_msgs/msg/PointCloud2`` 的内容, 使用命令 ``ros2 interface show sensor_msgs/msg/PointCloud2``, 输出如下:

.. code-block::
    :emphasize-lines: 11,19-20,23,37-40,42

    # This message holds a collection of N-dimensional points, which may
    # contain additional information such as normals, intensity, etc. The
    # point data is stored as a binary blob, its layout described by the
    # contents of the "fields" array.
    #
    # The point cloud data may be organized 2d (image-like) or 1d (unordered).
    # Point clouds organized as 2d images may be produced by camera depth sensors
    # such as stereo or time-of-flight.

    # Time of sensor data acquisition, and the coordinate frame ID (for 3d points).
    std_msgs/Header header
            builtin_interfaces/Time stamp
                    int32 sec
                    uint32 nanosec
            string frame_id

    # 2D structure of the point cloud. If the cloud is unordered, height is
    # 1 and width is the length of the point cloud.
    uint32 height
    uint32 width

    # Describes the channels and their layout in the binary data blob.
    PointField[] fields
            uint8 INT8    = 1
            uint8 UINT8   = 2
            uint8 INT16   = 3
            uint8 UINT16  = 4
            uint8 INT32   = 5
            uint8 UINT32  = 6
            uint8 FLOAT32 = 7
            uint8 FLOAT64 = 8
            string name      #
            uint32 offset    #
            uint8  datatype  #
            uint32 count     #

    bool    is_bigendian # Is this data bigendian?
    uint32  point_step   # Length of a point in bytes
    uint32  row_step     # Length of a row in bytes
    uint8[] data         # Actual point data, size is (row_step*height)

    bool is_dense        # True if there are no invalid points


.. todo:: 解释一下 msg 中各个字段的含义, 着重说明一下 fields 和 data 的关系.


.. mermaid::

    ---
    title: velodyne pointcloud
    ---
    classDiagram
        Calibration *-- RawData
        Eigen <-- DataContainerBase
        PointCloud2 <-- DataContainerBase
        tf2 <-- DataContainerBase
        VelodyneScan <.. DataContainerBase
        DataContainerBase <|.. OrganizedCloudXYZIRT
        DataContainerBase <|.. PointCloudXYZIRT
        DataContainerBase <-- Transform
        RawData <-- Transform
        note for Publisher "sensor_msgs/msg/PointCloud2"
        Publisher <-- Transform
        note for Subscription "velodyne_msgs/msg/VelodyneScan"
        Subscription <-- Transform
        note for Node "rclcpp::Node"
        Node <|-- Transform
        class RawData {
            +buildTimings()
            +setupSinCosCache()
            +setupAzimuthCache()
            +unpack()
            +scansPerPacket()
            -unpack_vlp16()
            -unpack_vls128()
        }
        class DataContainerBase {
            <<Interface>>
            +setup()
            +addPoint()
            +finishCloud()
        }



velodyne laserscan
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

首先了解一下 ros2 中 ``sensor_msgs/msg/LaserScan`` 的内容, 使用命令 ``ros2 interface show sensor_msgs/msg/LaserScan``, 输出如下:

.. code-block::
    :emphasize-lines: 7,18-20,22,25,27-28,30,32

    # Single scan from a planar laser range-finder
    #
    # If you have another ranging device with different behavior (e.g. a sonar
    # array), please find or create a different message, since applications
    # will make fairly laser-specific assumptions about this data

    std_msgs/Header header # timestamp in the header is the acquisition time of
            builtin_interfaces/Time stamp
                    int32 sec
                    uint32 nanosec
            string frame_id
                                 # the first ray in the scan.
                                 #
                                 # in frame frame_id, angles are measured around
                                 # the positive Z axis (counterclockwise, if Z is up)
                                 # with zero angle being forward along the x axis

    float32 angle_min            # start angle of the scan [rad]
    float32 angle_max            # end angle of the scan [rad]
    float32 angle_increment      # angular distance between measurements [rad]

    float32 time_increment       # time between measurements [seconds] - if your scanner
                                 # is moving, this will be used in interpolating position
                                 # of 3d points
    float32 scan_time            # time between scans [seconds]

    float32 range_min            # minimum range value [m]
    float32 range_max            # maximum range value [m]

    float32[] ranges             # range data [m]
                                 # (Note: values < range_min or > range_max should be discarded)
    float32[] intensities        # intensity data [device-specific units].  If your
                                 # device does not provide intensities, please leave
                                 # the array empty.


.. todo:: tbd


.. mermaid::

    ---
    title velodyne laserscan
    ---
    classDiagram
        note for Subscription "sensor_msgs/msg/PointCloud2"
        Subscription <-- VelodyneLaserScan
        note for Publisher "velodyne_msgs/msg/LaserScan"
        Publisher <-- VelodyneLaserScan
        note for Node "rclcpp::Node"
        Node <|-- VelodyneLaserScan
        class VelodyneLaserScan {
            +recvCallback()
        }

