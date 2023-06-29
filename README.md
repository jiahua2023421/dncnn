# 图像去噪课设说明
## 代码架构




## 基本要求
### 1. 讨论不同噪声水平下去噪性能的表现
  本文选取3个代码开源的典型图像去噪模型作为基线模型：RED、DnCNN和DeamNe。为了公平对比，本文使用与上述文章中相同的训练设置。
  按照上述网络架构进行训练和测试，我们在BSD68数据集所得到的测试结果如下：
![image](https://github.com/jiahua2023421/dncnn/assets/70991729/5f08b9fb-c953-4e1d-b1c5-d514069bf036)
  
  可以看出，去噪性能:DeamNet>DnCNN>REDNet，说明DnCNN的残差学习和批量归一化加快了训练过程并提高去噪性能; DeamNet将ACP项引入最大后验框架来指导网络设计的做法取得了良好的效果。
  从PSNR和SSIM指标来看，我们搭建的网络和原论文的数据在DnCNN上略有差距，DeamNet要优于原论文，分析原因，DnCNN可能是由于硬件条件限制导致训练出的模型和原论文存在差距，DeamNet经过大量调参导致效果要优于原论文。

### 2. 讨论网络深度对图像去噪性能的影响
  通过查阅资料可以发现，深度学习模型之所以在各种任务中取得了成功，足够的网络深度起到了关键的作用，为什么加深网络深度可以提升性能？
	
  首先我们需要知道加深网络可以更好拟合特征。现在的深度学习网络结构的主要模块是卷积，池化，激活，这是一个标准的非线性变换模块。更深的模型，意味着更好的非线性表达能力，可以学习更加复杂的变换，从而可以拟合更加复杂的特征输入。其次网络更深，每一层要做的事情也更加简单了。每一个网络层各司其职，第一层学习到了边缘，第二层学习到了简单的形状，第三层开始学习到了目标的形状，更深的网络层能学习到更加复杂的表达。如果只有一层，那就意味着要学习的变换非常的复杂，这很难做到。
	
  网络加深在一定程度上可以提升模型性能，但是未必就是网络越深越越好，深层网络会带来梯度不稳定，网络饱和、退化等问题，这就有可能出现网络加深，性能反而开始下降。
	
  在本次课程设计中我们取噪声水平为25，讨论不同网络深度对去噪性能的影响。由表可以得出，与10层对比，DnCNN在15层下的性能表现更好；相较于15层，30层的网络在PSNR 和SSIM指标均下降。
	
  由此可见在一定范围内加深网络可以提升DncNN性能，而网络过深会导致了性能下降。对于 REDNet，在测量的10层、20层、30层范围内，其性能则是随着深度的增加而上升，经查阅相关资料，REDNet里采用了跳跃连接，能解决网络过深导致的梯度消失，可以用更深的网络训练。而 DnCNN 中因为没有采用跳跃连接结构，因此网络过深会导致性能降低。
  
### 3. 讨论下采样和上采样对编码解码网络性能的影响
  查阅相关资料，我们得到了上采样和下采样的作用如下：
	
  下采样阶段：下采样可以降低图像的分辨率，从而减少图像中的噪点和干扰。在图像去噪任务中，下采样可以减少噪点和干扰的影响，从而提高去噪效果。
	
  上采样阶段：上采样可以增加图像的分辨率，从而提高图像的质量和清晰度。在图像去噪任务中，上采样可以恢复被去除的细节和纹理，从而提高去噪效果。
	
  根据查阅的资料发现，在加入下采样之后，PSNR和SSIM性能指标有略微下降，但实际训练过程中，加入下采样并在对应反卷积层上采样，在相同的数据量和训练参数下，训练时间明显缩短，可能是下采样减小特征图大小的同时丢失了图像的部分信息，所以提高测试效率的同时去噪性能下降。

## 改进措施
  基于DnCNN的思想改进DeamNet。
  
  Deamnet在高斯噪声数据集上的训练（BSD Set12/68）：原模型输出的是预测图片，用dncnn的思想，让模型进行残差学习，输出噪声图。
   	
   损失函数优化：发现模型在训练时损失函数很小，把SSIM和PSNR的指标好坏也作为损失，加到损失函数里，让其在指标好的时候损失小，指标坏的时候损失大。


## 额外工作
### 1. 讨论DeamNet 模型性能
下面分别是在BSD数据集下高斯噪声和SIDD数据集真实噪声测试结果：
![image](https://github.com/jiahua2023421/dncnn/assets/70991729/406e25fb-1910-4aef-9a89-fffdba4e8b3b)
![image](https://github.com/jiahua2023421/dncnn/assets/70991729/5a4c527d-0cd1-4118-9459-a6be02e95d10)

### 2. 讨论改进模型的性能
Deamnet模型改进：将模型输出改为噪声，LOSS函数加上（1-SSIM）/PSNR，在不进行预训练的条件下，仅在TRAIN400上训练十次，得到在sigma25噪声级别下set12上的结果PSNR为30.2366，SSIM为0.8616。

### 3. 代码可视化设计
考虑到日常生活中可能存在对图像去噪的需求，同时使我们的工作具有可推广性和应用性，我们制作了一个简易的python图像界面。该界面可以任意选择一张图片进行去噪并获取去噪后的图片。通过按键选择目标图片后即可利用加载的去噪模型自动生成去噪效果对比图，并可对其进行缩放、保存等处理。


## 分工
![image](https://github.com/jiahua2023421/dncnn/assets/70991729/f3a940a7-7cef-48ba-b7d1-740a9c050333)

## 主要工作
  本文复现了REDNet、DnCNN和DeamNet模型，讨论了不同噪声水平下去噪性能的表现，发现了去噪性能:DeamNet>DnCNN>REDNet；讨论了网络深度对图像去噪性能的影响，发现了一定范围内加深网络可以提升DncNN性能，而网络过深会导致了性能下降，对于 REDNet，其性能则是随着深度的增加而上升；讨论了下采样和上采样对编码解码网络性能的影响，发现了下采样减小特征图大小的同时丢失了图像的部分信息，所以提高测试效率的同时去噪性能下降。
	
  根据得到的结果，我们参考对模型进行了改进，Deamnet在高斯噪声数据集上的训练（BSD Set12/68）：原模型输出的是预测图片，用dncnn的思想，让模型进行残差学习，输出噪声图。损失函数优化：发现模型在训练时损失函数很小，把SSIM和PSNR的指标好坏也作为损失，加到损失函数里，让其在指标好的时候损失小，指标坏的时候损失大。
	
  DeamNet实现对数据集进行预处理，例如打包成“.h5”文件，“.mat”文件，理解了彩色图片和灰度图片的不同，解决图片通道数不匹配的问题，对图片进行裁剪等，以及模式识别中常用的库，基础知识，对矩阵分块，数组转化成张量，解决张量，数组，维度不匹配等问题，还有显示图片，保存图片，计算SSIM，PSNR等指标。对真实噪声训练，测试文件的进行重写，函数优化，以及把它们转换成图片显示保存，让整个模型的各个部分各个功能独立，清晰。
	
  我们还进行了代码可视化设计，通过PIL设计了图片处理应用的简易图像界面，可对任意单张彩色图片进行去噪处理，操作简便。
## 主要研究结论
  通过本次课设，我们对图像去噪领域的方法有个大概的了解，经过对比，发现了去噪性能:DeamNet>DnCNN>REDNet；一定范围内加深网络可以提升DncNN性能，而网络过深会导致了性能下降，对于 REDNet，其性能则是随着深度的增加而上升；下采样减小特征图大小的同时丢失了图像的部分信息，所以提高测试效率的同时去噪性能下降。
	
  Deamnet真实噪声模型能对智能手机，相机等设备所拍摄的照片进行去噪，其所去的噪声包括高斯噪声以及盲噪声，不管是从肉眼上还是性能指标上都可看出效果很好。数据集预处理能极大的提高训练以及测试的速度，（采用.h5文件和.mat格式），通过对数组的处理使结果以图片形式显示及保存，将数组转化为张量进入模型，输出张量，再转换为数组，可以很方便的实现前端开发，可视化显示。
