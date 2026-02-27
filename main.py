from config import  LOCAL_IMAGE_PATH, PRODUCT_CONFIG_JSON, SUPPORTED_EXTENSIONS
from config import RESOLUTION, SIZE, ARK_API_KEY
from nano_banana_caller import call_nano_banana
from pathlib import Path
from tos_operations import upload_to_tos, batch_delete_tos_images
from response_parser import  extract_image_urls_from_response
from image_downloader import download_image, save_prompts_to_file
import uuid
from prompt_generator_doubao_seed import get_product_detail_prompts
import json
import argparse
from loader import load_and_check_product_config
from openai import OpenAI




def main():
    # ===================== 命令行参数解析 =====================
    parser = argparse.ArgumentParser(description="商品详情页批量生成工具（交互式）")
    parser.add_argument(
        "-i", "--input",
        type=Path,
        required=True,
        help="输入的产品图片根目录（必须是包含多个产品子文件夹的目录）"
    )
    args = parser.parse_args()
    LOCAL_IMAGE_PATH = args.input.absolute()
    print(f"📁 输入目录：{LOCAL_IMAGE_PATH}")

    # ===================== 加载模板库 =====================
    SCRIPT_DIR = Path(__file__).parent
    TEMPLATES_JSON_PATH = SCRIPT_DIR.parent / "prompt_templates.json"
    #print("TEMPLATES_JSON_PATH:", TEMPLATES_JSON_PATH)

    templates = {}
    if TEMPLATES_JSON_PATH.exists():
        try:
            with open(TEMPLATES_JSON_PATH, 'r', encoding='utf-8') as f:
                templates = json.load(f)
                print("templates:", templates)
            template_names = list(templates.keys())
            if not template_names:
                print("⚠️ templates.json 存在但为空，将仅支持【自动化模式】")
        except Exception as e:
            print(f"⚠️ 读取 templates.json 失败：{e}，将仅支持【自动化模式】")
    else:
        print(f"⚠️ 模板文件不存在：{TEMPLATES_JSON_PATH}，将仅支持【自动化模式】")


    # ===================== 交互式选择模式 =====================
    print("=" * 60)
    print("🎯 请选择生成策略：")
    print("  [1] 自动化设计（调用豆包视觉模型生成详情页提示词）")
    if templates:
        print("  [2] 使用模板库（从已配置模板中选择）")
    else:
        print("  [2] 使用模板库（⚠️ 无模板可用，此选项无效）")
    choice = input("请输入选项编号（1 或 2）：").strip()
    print("=" * 60)

    mode = None
    selected_template_name = None
    nano_prompts = []

    if choice == "1":
        mode = "auto"
        print("✅ 已选择【自动化设计】模式\n")
    elif choice == "2" and templates:
        mode = "template"
        print("✅ 已选择【模板库】模式")
        print("\n可用模板列表：")
        for i, name in enumerate(template_names, 1):
            print(f"  [{i}] {name}")
        try:
            idx = int(input("\n请选择模板编号：").strip()) - 1
            if idx < 0 or idx >= len(template_names):
                print("❌ 编号无效，程序退出。")
                return
            selected_template_name = template_names[idx]
            nano_prompts = templates[selected_template_name]
            if not isinstance(nano_prompts, list):
                print("❌ 模板内容不是列表格式！请检查 templates.json。")
                return
            print(f"✔ 已选择模板：【{selected_template_name}】（共 {len(nano_prompts)} 条提示词）")
        except ValueError:
            print("❌ 输入非数字，程序退出。")
            return
    else:
        print("❌ 无效选项或无模板可用，程序退出。")
        return

    # ===================== 初始化豆包客户端（仅 auto 模式需要）=====================
    client = None
    if mode == "auto":
        try:
            client = OpenAI(
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                api_key=ARK_API_KEY
            )
            print("✅ 豆包客户端初始化成功")
        except Exception as e:
            print(f"❌ 豆包客户端初始化失败：{e}")
            return

    # ===================== 清理云床临时文件 =====================
    try:
        batch_delete_tos_images("temp_product/")
    except Exception as e:
        print(f"[WARN] TOS 清理跳过：{e}")

    # ===================== 加载产品配置 ======================
    product_config = load_and_check_product_config(PRODUCT_CONFIG_JSON)

    # ===================== 遍历产品子文件夹 =====================
    product_folders = [f for f in LOCAL_IMAGE_PATH.iterdir() if f.is_dir()]
    if not product_folders:
        print(f"❌ 输入目录【{LOCAL_IMAGE_PATH}】下无产品子文件夹，程序退出！")
        return
    print(f"✅ 检测到 {len(product_folders)} 个产品子文件夹：{[f.name for f in product_folders]}\n")

    processed_count = 0
    for prod_folder in product_folders:
        prod_folder_name = prod_folder.name
        print("=" * 70)
        print(f"📦 开始处理产品：【{prod_folder_name}】")
        print("=" * 70)

        # 匹配配置
        if prod_folder_name not in product_config:
            print(f"⚠️ 【{prod_folder_name}】无对应JSON配置，将使用默认值（屏数=8，userStr=''）")
            screenNum = 8
            userStr = ""
        else:
            screenNum = product_config[prod_folder_name]["screenNum"]
            userStr = product_config[prod_folder_name]["userStr"]
        print(f"✅ 屏数={screenNum} | userStr='{userStr}'\n")

        # 收集图片
        prod_image_files = [f for f in prod_folder.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]
        if not prod_image_files:
            print(f"⚠️ 【{prod_folder_name}】下无支持图片，跳过！\n")
            continue
        print(f"🔍 找到 {len(prod_image_files)} 张图片，开始上传TOS...")

        # 上传TOS收集URL
        image_urls = []
        for img_file in prod_image_files:
            try:
                remote_file_key = f"temp_product/{prod_folder_name}_{uuid.uuid4()}.png"
                img_url = upload_to_tos(img_file, remote_file_key)
                if img_url:
                    image_urls.append(img_url)
                    print(f"  ✅ 【{img_file.name}】上传成功")
            except Exception as e:
                print(f"  ❌ 【{img_file.name}】上传失败：{str(e)[:30]}")
        if not image_urls:
            print(f"⚠️ 【{prod_folder_name}】无有效图片URL，跳过！\n")
            continue
        if len(image_urls) > 4:
            image_urls = image_urls[:4]
            print("⚠️ 模型限4张图，自动截取前4张！")

        # =============== 根据模式获取提示词列表 ===============
        if mode == "auto":
            try:
                print("\n🚀 豆包模型调用启动（自动设计详情页）...")
                image_descript = get_product_detail_prompts(client, image_urls, userStr, screenNum)
                print("✅ 豆包模型返回完成")
                image_list = [
                    item.lstrip('0123456789. ').strip()
                    for item in image_descript.split('\n')
                    if item.strip()
                ]
                print(f"📝 解析出 {len(image_list)} 条提示词")
                save_prompts_to_file(prod_folder, prod_folder_name, image_list)
            except Exception as e:
                print(f"❌ 豆包调用失败：{e}，跳过该产品！\n")
                continue
        else:  # mode == "template"
            image_list = nano_prompts
            print(f"📥 从模板【{selected_template_name}】加载 {len(image_list)} 条提示词")

        # =============== 逐屏调用 Nano Banana Pro 生图 ===============
        for screen_idx, prompt in enumerate(image_list, start=1):
            print(f"\n屏 {screen_idx}/{min(len(image_list), screenNum)} | 提示词：{prompt[:70]}{'...' if len(prompt)>70 else ''}")
            if screen_idx > screenNum:
                print(f"⚠️ 已达设定屏数 {screenNum}，终止生成！")
                break

            try:
                print(f"\n🎨 Nano Banana 调用启动（生图第 {screen_idx} 屏）...")
                # 传入 image_urls（list）
                response = call_nano_banana(image_urls, prompt, RESOLUTION, SIZE)
                print("✅ Nano Banana 生图结束")

                if response and response.get("code") == 0 and response["data"].get("id"):
                    task_id = response["data"]["id"]
                    img_url = extract_image_urls_from_response(task_id)
                    if img_url:
                        output_file = prod_folder / f"{prod_folder_name}_shoe_screen_{screen_idx}.png"
                        download_image(img_url, str(output_file))
                        print(f"  ✅ 第{screen_idx}屏 | 保存成功：{output_file.name}")
                    else:
                        print(f"  ❌ 第{screen_idx}屏 | 提取图片URL失败！")
                else:
                    err_msg = response.get("msg", "未知错误") if response else "无响应"
                    print(f"  ❌ 第{screen_idx}屏 | 模型调用失败：{err_msg}")
            except Exception as e:
                print(f"  ❌ 第{screen_idx}屏 | 异常：{str(e)[:60]}")

        processed_count += 1
        print(f"\n🎉 【{prod_folder_name}】处理完成！结果保存于原目录：{prod_folder}\n")

    # ===================== 结束统计 =====================
    print("=" * 80)
    print("✅ 全量处理完成！")
    print(f"📊 统计：总产品 {len(product_folders)} | 成功 {processed_count} | 跳过 {len(product_folders)-processed_count}")
    print(f"📁 所有生成图均存于各产品原始文件夹内（命名：*_shoe_screen_X.png）")
    print("=" * 80)


# ===================== 程序入口 =====================
if __name__ == "__main__":
    main()