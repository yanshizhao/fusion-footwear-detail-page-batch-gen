# Automatic generation process of detailed page of footwear e-commerce 

交互式多源融合的电商鞋靴详情页生成流程。
支持两种模式自动生成详情页：
[1] 自动生成详情页流程
[2] 参考本地详情页模板库生成详情页
支持保存详情页生成提示词（Prompt）。

## ✨ 功能特点

- 📥 **自动下载**：自动下载保存详情页生成结果。
- 🧠 **智能提示词生成**：
  - 集成 **Doubao Seed** 模型生成高质量描述。
  - 支持 **Nano Banana pro** 模型调用。
- ☁️ **云存储集成**：使用火山引擎 TOS 对象存储，自动上传本地图片，生成公网可以访问的url链接。
- 依据模型识别 和 用户输入 自动生成成套详情图


## 🛠️ 环境要求

- Python 3.12+
- 火山引擎账号 (需开通 TOS 对象存储 & 方舟 Ark/豆包大模型服务)
- api聚合平台接口调用权限

## 📦 安装使用步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/yanshizhao/fusion-footwear-detail-page-batch-gen.git

2. **建立本地模板库**   
   使用模式[2] 前，使用shoe-detail-page-batch-raplicateshoe-detail-page-batch-raplicate 流程建立本地模板库
3、执行
   cd <项目文件夹>
   python -i <产品图片根目录（必须是包含多个产品子文件夹的目录>