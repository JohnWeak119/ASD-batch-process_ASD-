# ASD-batch-process_ASD-

使用ASD光谱仪进行测量后，需要处理大量的.asd光谱数据。在处理反射率数据时，viewspc pro软件只能对每一组数据分别做平均处理，耗时费力，操作繁琐。

在此根据CSDN怒视天下
https://blog.csdn.net/qq_49491645/article/details/148216676
的方法，写出python批量处理的代码。

实现内容如下：

1、读取文件夹下txt文档，按照设定组大小求平均光谱

2、显示、保存每组平均光谱至单独的txt中

3、保留每组平均光谱第一个光谱曲线的头信息，作为处理后的头信息

使用注意事项如下：

1、处理过程不包括掩膜坏波段

2、处理前，在 ViewSpecPro 中对所有.asd文件，进行Reflectance/Transmittance处理，全部ASCⅡ导出（导出时选中reflectance,print header information）

3、参数、路径、文件名请自行设置
