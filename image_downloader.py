import requests
from datetime import datetime

def download_image(image_url, save_path='output.png'):
    try:
        response = requests.get(image_url, stream=True, timeout=300)
        response.raise_for_status()  # 如果HTTP状态码不是200，则引发异常
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"图像已成功下载到: {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"图像下载失败: {e}")


def save_prompts_to_file(prod_folder, prod_folder_name, prompt_nano):
    """
    将提示词列表保存到原图文件夹中
    
    Args:
        prod_folder: 产品文件夹的路径  
        prod_folder_name: 产品的文件夹名称
        prompt_nano: 提示词列表
    """
    try:
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_filename = f"{prod_folder_name}_prompts_{timestamp}.txt"
        prompt_file_path = prod_folder / prompt_filename  # 直接保存到原图文件夹
        
        # 保存提示词到文件
        with open(prompt_file_path, 'w', encoding='utf-8') as f:
            f.write(f"产品名称：{prod_folder_name}\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总屏数：{len(prompt_nano)}\n")
            f.write("="*60 + "\n\n")
            for i, prompt in enumerate(prompt_nano, 1):
                f.write(f"【Prompt {i}】\n")
                f.write(prompt + "\n")
                f.write("-"*50 + "\n\n")
        
        print(f"提示词已保存至：{prompt_file_path.absolute()}")
        return prompt_file_path
    except Exception as e:
        print(f"保存提示词文件失败：{str(e)}")
        return None