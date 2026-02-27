from config import GRSAI_API_KEY, GRSAI_URL
import requests


def call_nano_banana(
    image_urls: list,  
    prompt: str,
    imageSize: str,
    aspectRatio: str,
):
    """
    调用 Nano Banana pro 模型进行图像编辑。

    参数:
        image_urls (list): 图像url的列表
        prompt (str): 提示词
        imageSize(str): 图像尺寸
        aspectRatio(str): 输出图像分辨率比例

    返回:
        dict: 响应数据或错误信息
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GRSAI_API_KEY}",  
    }
    
    # 过滤掉 None 或空字符串的 URL
    urls = [url.strip() for url in image_urls if url and isinstance(url, str)]
    
    payload = {
        "model": "nano-banana-pro",
        "prompt": prompt,
        "aspectRatio": aspectRatio,
        "imageSize": imageSize,
        "urls": urls,  
        "webHook": "-1",
        "shutProgress": False
    }
    #print("Payload:", payload)
    try:
        # 发送POST请求
        response = requests.post(
            url=GRSAI_URL, 
            json=payload,
            headers=headers,
        )
        # 检查HTTP响应状态码
        response.raise_for_status()
        print(f"响应状态码: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        # 捕获请求相关的所有异常（网络错误、状态码错误等）
        print(f"请求AI接口失败: {e}")
        return None
    except ValueError as e:
        # 捕获JSON解析失败的异常
        print(f"解析接口返回数据失败: {e}")
        return None