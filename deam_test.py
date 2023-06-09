# 官方库
import os
import time
import torch
import cv2
import torch.nn as nn
import argparse
import pandas as pd
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import numpy as np
import public
from imageio import imread
from skimage.metrics import structural_similarity as compare_ssim
from skimage.metrics import peak_signal_noise_ratio as compare_psnr
from PIL import Image
from torch.autograd import Variable
 # 私人库

from public import parse_args, log
from data_process import save_result
from model import DnCNN, Deam
import matplotlib.pyplot as plt
#

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

parser = argparse.ArgumentParser(description="AWGN Testing......")
parser.add_argument("--pretrained", type=str, default="./Deam_models/", help='path of log files')
parser.add_argument("--test_data", default=['Set68', 'Set12'], help='test dataset such as Set12, Set68 and Urban100')
parser.add_argument("--test_noiseL", type=float, default=15, help='noise level used on test set')
parser.add_argument('--statistics', default='./statistics/', help='Location to save statistics')
parser.add_argument('--data_dir', type=str, default='./data')
parser.add_argument('--module', type=str, default='noise15.pth')
parser.add_argument('--Isreal', default=False, help='If training/testing on RGB images')
parser.add_argument('--result_dir', default='deam_results/sigma15', type=str, help='directory of test dataset')#测试结果目录
opt = parser.parse_args()


def batch_PSNR(img, imclean, data_range):
    Img = img.data.cpu().numpy().astype(np.float32)
    Iclean = imclean.data.cpu().numpy().astype(np.float32)
    PSNR = 0
    for i in range(Img.shape[0]):
        PSNR += compare_psnr(Iclean[i, :, :, :], Img[i, :, :, :], data_range=data_range)
        ceshi = Iclean[i, :, :, :]
        ceshi2 = Img[i, :, :, :]
        # ceshi3 = Iclean[:, :]

        Iclean2 = ceshi[:, :, ::-1].transpose((1, 2, 0))
        Img2 = ceshi2[:, :, ::-1].transpose((1, 2, 0))
        # img2 = np.resize(img2, (img1.shape[0], img1.shape[1], img1.shape[2]))
        ce = ceshi[0]
        ce2 = ceshi2[0]
        show(np.hstack((Iclean2[:,:,0], Img2[:,:,0])))  # 去噪图片，噪声图片
    return (PSNR / Img.shape[0])
def show(x, title=None, cbar=False, figsize=None):
    plt.figure(figsize=figsize)

    plt.imshow(x, cmap="gray")  # #interpolation 插值方法  #cmap: 颜色图谱（colormap), 默认绘制为RGB(A)颜色空间
    if title:
        plt.title(title)
    if cbar:
        plt.colorbar()
    plt.show()  # 输出图片

def normalize(data):
    return data/255.


def tensor_to_np(tensor):
    img = tensor.mul(255).byte()
    img = img.numpy()
    return img


def main():
    print('Loading model ...\n')
    net = Deam(opt.Isreal)
    model = nn.DataParallel(net).cuda()
    model.load_state_dict(torch.load(os.path.join(opt.pretrained, opt.module), map_location=lambda storage, loc: storage))
    model.eval()
    for set_cur in opt.test_data:
    # print('Loading data info ...\n')
        files_path = os.path.join(opt.data_dir, 'Test', set_cur)
        files_source = os.listdir(files_path)

        psnr_test = 0
        i = 1
        psnrs = []  # 计算psnr与ssim的数组
        ssims = []

        for f in files_source:
            # if not os.path.exists(os.path.join(opt.result_dir)):  # 未找到保存文件的路径，则创造路径
            #     os.mkdir(os.path.join(opt.result_dir))
            # public.path_creat(opt.result_dir)
            SEED = 0
            torch.manual_seed(SEED)
            torch.cuda.manual_seed(SEED)
            start_time = time.time()
            image_path = os.path.join(files_path, f)
            # image
            Img = cv2.imread(image_path)
            Img = normalize(np.float32(Img[:, :, 0]))
            Img = np.expand_dims(Img, 0)
            Img = np.expand_dims(Img, 1)
            ISource = torch.Tensor(Img)

            # noise
            noise = torch.FloatTensor(ISource.size()).normal_(mean=0, std=opt.test_noiseL / 255.)
            # noisy image
            INoisy = ISource + noise
            ISource, INoisy = Variable(ISource.cuda()), Variable(INoisy.cuda())

            with torch.no_grad():  # this can save much memory
                B, C, H, W = INoisy.size()

                # padding to fit the input size of UNet
                bottom = (16 - H % 16) % 16
                right = (16 - H % 16) % 16

                padding = nn.ReflectionPad2d((0, right, 0, bottom))
                INoisy_input = padding(INoisy)

                model_out = model(INoisy_input)
                Out = model_out[:, :, 0:H, 0:W]

            psnr = batch_PSNR(torch.clamp(Out, 0., 1.), ISource, 1.)
            psnr_test += psnr
            i += 1
            name, ext = os.path.splitext(f)  # 文件名 后缀
            y = torch.squeeze(Out)  #tesnsor降维
            y1 = y.cpu().numpy()    #先加载到CPU，再转为数组
            x = torch.squeeze(INoisy_input)
            x1 = x.cpu().numpy()
            source = torch.squeeze(ISource)
            S = source.cpu().numpy()
            # show(np.hstack((y1, x1)))  # show the image
            # save_result(y1, path=os.path.join(opt.result_dir, opt.test_data,
            #                             name + 'deamnet' + ext))
            ssim_x_ = compare_ssim(y1, S)

            psnr_x_ = compare_psnr(y1, S, data_range=1.0)  # 比较 原图 与 加噪声再去噪的图 计算psnr
            # ssim_x_ = compare_ssim(x, x_)
            psnrs.append(psnr_x_)  # 向列表末尾添加元素
            ssims.append(ssim_x_)
            elapsed_time = time.time() - start_time
            print(' %10s : %2.4f second' % (f, elapsed_time))
        psnr_avg = np.mean(psnrs)  # np.mean求平均值
        ssim_avg = np.mean(ssims)
        psnrs.append(psnr_avg)
        ssims.append(ssim_avg)
        psnr_test /= len(files_source)
        public.path_creat(os.path.join(opt.result_dir, set_cur))
        save_result(np.hstack((psnrs, ssims)), path=os.path.join(opt.result_dir, set_cur, 'results.txt'))
        #         # 以文本形式 保存每一张图片的PSNR与SSIM结果
        log('Datset: {0:10s} \n  PSNR = {1:2.2f}dB, SSIM = {2:1.4f}'.format(opt.result_dir, psnr_avg, ssim_avg))
        print("PSNR on test data %f" % psnr_test)
        # data_frame = pd.DataFrame(
        #     data={'data': opt.test_data, 'sigma': opt.test_noiseL, 'PSNR': psnr_avg, 'SSIM': ssim_avg}, index=range(1,   2)
        # )
        # data_frame.to_csv(os.path.join(opt.statistics, 'testing_result.csv'), index_label='index')
        print("\n")


if __name__ == "__main__":
    main()
