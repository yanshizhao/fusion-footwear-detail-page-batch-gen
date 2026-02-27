
from pathlib import Path


# 火山引擎TOS配置 
AK = "请填写你的 TOS Access Key"   
SK = "请填写你的 TOS Secret Key"
BUCKET_NAME = "请填写你的 TOS BUCKET_NAME"               
REGION = "cn-guangzhou"

# 豆包API Key
ARK_API_KEY = "你的_ACCESS_KEY_ID_请填写" #从火山引擎获取豆包模型密钥

# API密钥和API URL
GRSAI_API_KEY = 's你的_ACCESS_KEY_ID_请填写' #GRSAI api 聚合平台获取
GRSAI_URL = "https://grsai.dakka.com.cn/v1/draw/nano-banana"
GRSAI_URL_RESULT = "https://grsai.dakka.com.cn/v1/draw/result"


# ===================== 跨平台路径配置（核心：仅修改根前缀，主体路径通用）=====================
LOCAL_IMAGE_PATH = Path("product_image") / "branan_clear_result"  # 图片源路径：./product_image/branan_clear_result
PRODUCT_CONFIG_JSON = Path("product_config.json")                  # 模板JSON配置文件：product_config.json（与脚本同目录），使用shoe-detail-page-batch-raplicate 流程填充json文件

# 支持的图片扩展名
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

#图片参数配置
RESOLUTION = "1K"
SIZE = "9:16"