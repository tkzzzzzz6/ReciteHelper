背诵检测程序开发
文言文背诵检测程序
通过语音识别和文本相似度分析，自动检测文言文背诵准确率  
技术栈：Python + 百度AI开放平台（语音识别 & NLP）
项目背景
今天在侄儿子要求在我这里背书的时候,有点嫌麻烦,想用程序识别和检测他的背诵,在网上查找相关软件和网站发现只有一个滑板车背诵的软件效果还不错,但是还是感觉这个产业不太成熟,于是自己用ai基于百度AI接口开发了此背诵检测程序，实现以下功能：
- 语音转文本：实时录制背诵音频并转换为文字
- 相似度对比：通过自然语言处理（NLP）比对背诵内容与原文
- 准确率评分：输出整体匹配度和逐句差异分析
支持导入自定义文言文文本文件  
注意:
需提前申请百度语音API 和百度NPL API
目前识别效果和响应时间并不理想,需要一次性一句话一句话背诵
快速开始
1. 克隆仓库
git clone https://github.com/tkzzzzzz6/beisong.git
cd beisong
2. 配置环境
推荐使用 conda 虚拟环境：
conda create -n beisong python=3.10 -y
conda activate beisong
pip install -r requirements.txt
3. 配置API密钥
1. 前往百度AI控制台 创建应用
2. 获取 API Key 和 Secret Key
3. 修改 config.py 文件：
#语音识别配置
APP_ID = '你的APP ID'      # 应用ID
API_KEY = '你的API Key'    # API Key
SECRET_KEY = '你的API Key'    # API Key

#百度NLP配置
NLP_APP_ID = '你的APP ID' 
NLP_API_KEY = '你的API Key'    # API Key
NLP_SECRET_KEY = '你的API Key'    # API Key
4. 添加背诵文本
将文言文文本保存为 txt 文件，放置于 /texts 目录下  
（程序已内置《孙权劝学》《卖油翁》《木兰诗》示例文本）
5. 运行程序
python main.py
项目结构
.
├── texts/                 # 文言文文本库
│   ├── 孙权劝学.txt
│   └── ...
├── config.py             # API密钥配置文件
├── main.py               # 主程序
├── requirements.txt      # 依赖库列表
└── README.md             # 说明文档
常见问题
Q1: 如何获取百度API密钥？
1. 注册百度智能云账号
2. 进入「语音技术」和「自然语言处理」服务控制台
3. 创建应用后获取密钥信息
Q2: 安装依赖时报错？
- 确保使用 Python 3.10
- 尝试升级 pip：pip install --upgrade pip
- 使用清华镜像源加速：pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
Q3: 如何扩展支持其他文本？
- 在 /texts 目录下添加新的 .txt 文件
- 文本编码需为 UTF-8
- 建议每段不超过 500 字

---
参与贡献
欢迎提交 Issue 或 Pull Request  
📧 联系邮箱：your_email@example.com  
🐛 Bug 反馈：Issues页面

---
License：本项目采用 [MIT License](LICENSE)