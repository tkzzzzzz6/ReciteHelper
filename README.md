
</p>
<p align="center">
	<img src="https://img.shields.io/github/last-commit/tkzzzzzz6/ReciteHelper?style=default&logo=git&logoColor=white&color=0080ff" alt="最后提交">
	<img src="https://img.shields.io/github/languages/top/tkzzzzzz6/ReciteHelper?style=default&color=0080ff" alt="主要语言">
	<img src="https://img.shields.io/github/languages/count/tkzzzzzz6/ReciteHelper?style=default&color=0080ff" alt="语言数量">
</p>
<p align="center">
	<!-- 默认选项，不显示依赖项徽章。 -->
</p>
<p align="center">
	<!-- 默认选项，不显示依赖项徽章。 -->
</p>

## 目录

- [概述](#-概述)
- [项目结构](#-项目结构)
  - [项目索引](#-项目索引)
- [开始使用](#-开始使用)
  - [前提条件](#-前提条件)
  - [安装](#-安装)



## 概述

今天在侄儿子要求在我这里背书的时候,有点嫌麻烦,想用程序识别和检测他的背诵,在网上查找相关软件和网站发现只有一个滑板车背诵的软件效果还不错,但是还是感觉这个产业不太成熟,于是自己用ai基于百度AI接口开发了此背诵检测程序，实现以下功能：
- 语音转文本：实时录制背诵音频并转换为文字
- 相似度对比：通过自然语言处理（NLP）比对背诵内容与原文
- 准确率评分：输出整体匹配度和逐句差异分析
支持导入自定义文言文文本文件  
>注意:<br>
>需提前申请百度语音API 和百度NPL API<br>
>目前识别效果和响应时间并不理想,需要一次性一句话一句话背诵

## 项目结构

```sh
└── ReciteHelper/
    ├── Dockerfile
    ├── README.md
    ├── config.py
    ├── main.py
    ├── requirements.txt
    └── texts
        ├── 买油翁.txt
        ├── 孙权劝学.txt
        └── 木兰诗.txt
```

## 开始使用

### 安装

使用以下方法安装 ReciteHelper：


1. 克隆 ReciteHelper 仓库：
```sh
git clone https://github.com/tkzzzzzz6/ReciteHelper
```

2. 进入项目目录：
```sh
cd ReciteHelper
```

3. 配置环境

推荐使用 conda 虚拟环境：
```sh
conda create -n beisong python=3.10 -y
conda activate beisong
pip install -r requirements.txt
```

4. 配置API密钥

-  前往百度AI控制台 创建应用
- 获取 API Key 和 Secret Key
- 修改 config.py 文件：
```sh
#语音识别配置
APP_ID = '你的APP ID'      # 应用ID
API_KEY = '你的API Key'    # API Key
SECRET_KEY = '你的API Key'    # API Key

#百度NLP配置
NLP_APP_ID = '你的APP ID' 
NLP_API_KEY = '你的API Key'    # API Key
NLP_SECRET_KEY = '你的API Key'    # API Key
```

5. 添加背诵文本

将文言文文本保存为 txt 文件，放置于 /texts 目录下  
（程序已内置《孙权劝学》《卖油翁》《木兰诗》示例文本）

6. 运行程序
```sh
python main.py
```




