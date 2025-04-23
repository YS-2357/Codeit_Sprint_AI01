import torch
import torch.nn as nn
import torch.nn.functional as F
from torchinfo import summary

####################################################################################################
# 1. Denoising Autoencoder 모델 정의
class DenoisingAutoencoder(nn.Module):
    def __init__(self):
        super(DenoisingAutoencoder, self).__init__()

        # Encoder
        # Depthwise + Pointwise
        self.enc1 = nn.Sequential(
            nn.Conv2d(1, 1, kernel_size=3, stride=1, padding=1, groups=1, bias=False),
            nn.Conv2d(1, 8, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)  # (8, 210, 270)
        )

        self.enc2 = nn.Sequential(
            nn.Conv2d(8, 8, kernel_size=3, stride=1, padding=1, groups=1, bias=False),
            nn.Conv2d(8, 16, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.MaxPool2d(kernel_size=2, stride=2)  # (16, 105, 135)
        )

        self.enc3 = nn.Sequential(
            nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=1, groups=1, bias=False),
            nn.Conv2d(16, 32, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.MaxPool2d(kernel_size=2, stride=2)  # (32, 52, 67)
        )

        #
        self.enc4 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1, groups=1, bias=False),
            nn.Conv2d(32, 64, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.MaxPool2d(kernel_size=2, stride=2)  # (64, 26, 33)
        )

        self.enc5 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1, groups=1, bias=False),
            nn.Conv2d(64, 128, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.MaxPool2d(kernel_size=2, stride=2)  # (128, 13, 16)
        )

        # Decoder
        self.dec5 = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=1, stride=1, bias=False),
            nn.ConvTranspose2d(64, 64, kernel_size=3, stride=2, padding=1, output_padding=1, groups=64, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout(p=0.3)
        )

        self.dec4 = nn.Sequential(
            nn.ConvTranspose2d(64, 32, kernel_size=1, stride=1, bias=False),
            nn.ConvTranspose2d(32, 32, kernel_size=3, stride=2, padding=1, output_padding=1, groups=32, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Dropout(p=0.3)
        )

        self.dec3 = nn.Sequential(
            nn.ConvTranspose2d(32, 16, kernel_size=1, stride=1, bias=False),
            nn.ConvTranspose2d(16, 16, kernel_size=3, stride=2, padding=1, output_padding=1, groups=16, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Dropout(p=0.2)
        )

        self.dec2 = nn.Sequential(
            nn.ConvTranspose2d(16, 8, kernel_size=1, stride=1, bias=False),
            nn.ConvTranspose2d(8, 8, kernel_size=3, stride=2, padding=1, output_padding=1, groups=8, bias=False),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.Dropout(p=0.1)
        )

        self.dec1 = nn.Sequential(
            nn.ConvTranspose2d(8, 1, kernel_size=1, stride=1, bias=False),
            nn.ConvTranspose2d(1, 1, kernel_size=3, stride=2, padding=1, output_padding=1, groups=1, bias=False),
            nn.Sigmoid()  # 픽셀 값을 0~1로 정규화
        )

        # Skip Connection 채널 맞추기
        self.conv4 = nn.Conv2d(64, 32, kernel_size=1, stride=1, bias=False)  # (64 → 32)
        self.conv5 = nn.Conv2d(128, 64, kernel_size=1, stride=1, bias=False)  # (128 → 64)

    def forward(self, x):
        # Encoding
        enc1_out = self.enc1(x)  # (8, 210, 270)
        enc2_out = self.enc2(enc1_out)  # (16, 105, 135)
        enc3_out = self.enc3(enc2_out)  # (32, 52, 67)
        enc4_out = self.enc4(enc3_out)  # (64, 26, 33)
        enc5_out = self.enc5(enc4_out)  # (128, 13, 16)

        # Decoding with Skip Connection
        dec5_out = self.dec5(enc5_out)  # (64, 26, 33)
        dec5_out = F.interpolate(dec5_out, size=(26, 33), mode='bilinear', align_corners=False)
        dec5_out = torch.cat([dec5_out, enc4_out], dim=1)
        dec5_out = self.conv5(dec5_out)  # (128 → 64)

        dec4_out = self.dec4(enc4_out)  # (32, 52, 67)
        dec4_out = F.interpolate(dec4_out, size=(52, 67), mode='bilinear', align_corners=False)
        dec4_out = torch.cat([dec4_out, enc3_out], dim=1)  # Skip Connection
        dec4_out = self.conv4(dec4_out)  # (64 → 32)

        dec3_out = self.dec3(dec4_out)  # (16, 104, 134)
        dec3_out = F.interpolate(dec3_out, size=(105, 135), mode='bilinear', align_corners=False)

        dec2_out = self.dec2(dec3_out)  # (8, 210, 270)
        dec2_out = F.interpolate(dec2_out, size=(210, 270), mode='bilinear', align_corners=False)

        dec1_out = self.dec1(dec2_out)  # (1, 420, 540)
        dec1_out = F.interpolate(dec1_out, size=(420, 540), mode='bilinear', align_corners=False)

        # Output
        outputs = torch.clamp(dec1_out, min=0.001, max=0.999)
        return outputs
    

####################################################################################################
# 2. U-Net Autoencoder 모델 정의
class UNetAutoEncoder(nn.Module):
    def __init__(self):
        super(UNetAutoEncoder, self).__init__()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.sigmoid = nn.Sigmoid()

        # Encoder
        self.enc1 = nn.Sequential(  # (1, 420, 540) -> (16, 210, 270)
            nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(),
        )
        self.enc2 = nn.Sequential(  # (16, 210, 270) -> (32, 105, 135) / Depthwise, Pointwise
            nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=1, groups=16, bias=False),
            nn.Conv2d(16, 32, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )
        self.enc3 = nn.Sequential(  # (32, 105, 135) -> (64, 52, 67) / Depthwise, Pointwise
            nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1, groups=32, bias=False),
            nn.Conv2d(32, 64, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout(p=0.3),
        )
        self.bottleneck = nn.Sequential(    # (64 -> 128) / Bottleneck
            nn.Conv2d(64, 32, kernel_size=1, stride=1, bias=False),
            nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1, groups=32, bias=False),
            nn.Conv2d(32, 128, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Dropout(p=0.3),
        )

        # Decoder
        self.upconv3 = nn.Sequential(  # (128, 52, 67) -> (64, 105, 135) / Bottleneck
            nn.ConvTranspose2d(128, 32, kernel_size=1, stride=1, bias=False),
            nn.ConvTranspose2d(32, 32, kernel_size=3, stride=2, padding=1, output_padding=1, groups=32, bias=False),
            nn.ConvTranspose2d(32, 64, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout(p=0.2),
        )
        self.dec3 = nn.Sequential(  # (128, 105, 135) -> (64, 105, 135) / Depthwise, Pointwise
            nn.Conv2d(128, 64, kernel_size=1, stride=1, bias=False),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1, groups=64, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout(p=0.2),
        )

        self.upconv2 = nn.Sequential(  # (64, 105, 135) -> (32, 210, 270) / Bottleneck
            nn.ConvTranspose2d(64, 16, kernel_size=1, stride=1, bias=False),
            nn.ConvTranspose2d(16, 16, kernel_size=3, stride=2, padding=1, output_padding=1, groups=16, bias=False),
            nn.ConvTranspose2d(16, 32, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )
        self.dec2 = nn.Sequential(  # (64, 210, 270) -> (32, 210, 270) / Depthwise, Pointwise
            nn.Conv2d(64, 32, kernel_size=1, stride=1, bias=False),
            nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1, groups=32, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )

        self.upconv1 = nn.Sequential(  # (32, 210, 270) -> (16, 420, 540) / Bottleneck
            nn.ConvTranspose2d(32, 8, kernel_size=1, stride=1, bias=False),
            nn.ConvTranspose2d(8, 8, kernel_size=3, stride=2, padding=1, output_padding=1, groups=8, bias=False),
            nn.ConvTranspose2d(8, 16, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(),
        )
        self.dec1 = nn.Sequential(  # (32, 420, 540) -> (16, 420, 540) / Depthwise, Pointwise
            nn.Conv2d(32, 16, kernel_size=1, stride=1, bias=False),
            nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=1, groups=16, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(),
        )
        self.final_conv = nn.Conv2d(16, 1, kernel_size=1, stride=1, bias=False)  # (16, 420, 540) -> (1, 420, 540)

    def forward(self, x):
        # Encoding
        enc1 = self.enc1(x)  # (16, 420, 540)
        x = self.pool(enc1)  # (16, 210, 270)

        enc2 = self.enc2(x)  # (32, 210, 270)
        x = self.pool(enc2)  # (32, 105, 135)

        enc3 = self.enc3(x)  # (64, 105, 135)
        x = self.pool(enc3)  # (64, 52, 67)

        x = self.bottleneck(x)  # (128, 52, 67)

        # Decoding with skip connections
        x = self.upconv3(x)  # (64, 105, 135)
        x = F.interpolate(x, size=(105, 135), mode='bilinear', align_corners=False) # resize
        x = torch.cat((x, enc3), dim=1)  # (128, 105, 135)
        x = self.dec3(x)  # (64, 105, 135)

        x = self.upconv2(x)  # (32, 210, 270)
        x = torch.cat((x, enc2), dim=1)  # (64, 210, 270)
        x = self.dec2(x)  # (32, 210, 270)

        x = self.upconv1(x)  # (16, 420, 540)
        x = torch.cat((x, enc1), dim=1)  # (32, 420, 540)
        x = self.dec1(x)  # (16, 420, 540)

        x = self.final_conv(x)  # (1, 420, 540)
        x = self.sigmoid(x)

        # Resize to match original input size
        # x = F.interpolate(x, size=(420, 540), mode='bilinear', align_corners=False)
        return x

####################################################################################################
# 3. 모델 요약 정보 출력
def model_summary(model, input_size):
    summary(model, input_size=input_size)

####################################################################################################
# 4. 모델 선택 함수
def get_model(model_name):
    if model_name == "dae":
        return DenoisingAutoencoder()
    elif model_name == "unet":
        return UNetAutoEncoder()
    else:
        raise ValueError(f"Unsupported model: {model_name}.\nChoose from 'dae' or 'unet'.")

####################################################################################################
# 5. __all__ 추가
__all__ = ["DenoisingAutoencoder", "UNetAutoEncoder", "model_summary", "get_model"]