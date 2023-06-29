# 图像去噪课设说明
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
	
	由此可见在一定范围内加深网络可以提升DncNN性能，而网络过深会导致了性能下降。对于 REDNet
	，在测量的10层、20层、30层范围内，其性能则是随着深度的增加而上升，经查阅相关资料，REDNet里采用了跳跃连接，能解决网络过深导致的梯度消失，可以用更深的网络训练。而 DnCNN 中因为没有采用跳跃连接结构，因此网络过深会导致性能降低。
### 3. 讨论下采样和上采样对编码解码网络性能的影响
参数
日志
保存图片
显示图片
DnCNN网络架构
主函数

## 额外工作
### 讨论DeamNet 模型性能
DnCNN网络架构
### 讨论改进模型的性能
图片加噪声
保存图片
显示图片
旋转图片
图片大小调整
图片归一化
### 代码可视化设计
主函数


## 分工
