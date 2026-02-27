from pathlib import Path
import json



# ===================== JSON配置读取与校验函数（不变）=====================
def load_and_check_product_config(json_path: str):

    """===================== 读取产品属性特点配置(包括: 产品材质、设计样式等)与校验函数===================== """
    if not Path(json_path).exists():
        print(f"产品配置JSON不存在：{json_path}，请检查路径！")
        exit(1)
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON格式错误：{str(e)}（检查逗号/引号/括号）")
        exit(1)
    except Exception as e:
        print(f"读取JSON失败：{str(e)}")
        exit(1)
    if not isinstance(config, dict):
        print(f"JSON顶层必须是字典（如{{\"sleekS2507230194_黑色\": {...}}}）")
        exit(1)
    valid_config = {}
    for prod_folder_name, prod_info in config.items():
        if not isinstance(prod_info, dict):
            print(f"产品【{prod_folder_name}】配置非字典，跳过！")
            continue
        if "screenNum" not in prod_info or "userStr" not in prod_info:
            print(f"产品【{prod_folder_name}】缺失screenNum/userStr，跳过！")
            continue
        screen_num = prod_info["screenNum"]
        if not isinstance(screen_num, int) or screen_num <= 0:
            print(f"产品【{prod_folder_name}】screenNum必须是正整数，跳过！")
            continue
        user_str = str(prod_info["userStr"]).strip()
        if not user_str:
            print(f"产品【{prod_folder_name}】userStr为空，跳过！")
            continue
        valid_config[prod_folder_name] = {"screenNum": screen_num, "userStr": user_str}
    if not valid_config:
        print(f"JSON中无有效产品配置，程序退出！")
        exit(1)
    print(f"JSON解析成功，加载 {len(valid_config)} 个产品配置！\n")
    return valid_config
