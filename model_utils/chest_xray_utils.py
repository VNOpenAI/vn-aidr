import numpy as np
import cv2


def border_pad(image, cfg):
    h, w, c = image.shape

    if cfg.border_pad == 'zero':
        image = np.pad(image, ((0, cfg.long_side - h),
                               (0, cfg.long_side - w), (0, 0)),
                       mode='constant',
                       constant_values=0.0)
    elif cfg.border_pad == 'pixel_mean':
        image = np.pad(image, ((0, cfg.long_side - h),
                               (0, cfg.long_side - w), (0, 0)),
                       mode='constant',
                       constant_values=cfg.pixel_mean)
    else:
        image = np.pad(image, ((0, cfg.long_side - h),
                               (0, cfg.long_side - w), (0, 0)),
                       mode=cfg.border_pad)

    height_pad_percent = (cfg.long_side - h) / cfg.long_side
    width_pad_percent = (cfg.long_side - w) / cfg.long_side
    return image, (width_pad_percent, height_pad_percent)



def fix_ratio(image, cfg):
    h, w, c = image.shape

    if h >= w:
        ratio = h * 1.0 / w
        h_ = cfg.long_side
        w_ = round(h_ / ratio)
    else:
        ratio = w * 1.0 / h
        w_ = cfg.long_side
        h_ = round(w_ / ratio)

    image = cv2.resize(image, dsize=(w_, h_), interpolation=cv2.INTER_LINEAR)
    image, padding_percent = border_pad(image, cfg)

    return image, padding_percent


def preprocess(cfg, image):

    # Convert to gray
    if image.ndim != 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image = image

    if cfg.use_equalizeHist:
        image = cv2.equalizeHist(image)

    if cfg.gaussian_blur > 0:
        image = cv2.GaussianBlur(
            image,
            (cfg.gaussian_blur, cfg.gaussian_blur), 0)

    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    image, padding_percent = fix_ratio(image, cfg)

    # normalization
    image = image.astype(np.float32) - cfg.pixel_mean
    # vgg and resnet do not use pixel_std, densenet and inception use.
    if cfg.pixel_std:
        image /= cfg.pixel_std
    # normal image tensor :  H x W x C
    # torch image tensor :   C X H X W
    image = image.transpose((2, 0, 1))

    return image, padding_percent


def remove_padding(image, width_pad_percent, height_pad_percent):
    h, w = image.shape[:2]
    w_pad = int(width_pad_percent * w)
    h_pad = int(height_pad_percent * h)
    image = image[:h-h_pad, :w-w_pad]
    return image
