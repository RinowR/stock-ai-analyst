# 智诊股 · 技术面智能诊断工具

基于 [Ashare-LLM-Analyst](https://github.com/Ogannesson/ashare-llm-analyst) 改造，面向普通投资者的 AI 个股技术面诊断工具。

## 项目简介

**智诊股**是一款专为普通投资者设计的**技术面快速诊断工具**。它解决了传统 K 线图分析繁琐、专业术语难懂的问题，让用户在输入股票代码或上传 K 线图后，**一键获得清晰易懂的技术面诊断报告**。

本项目基于 [Ashare-LLM-Analyst]进行了改造，从**脚本式静态报告生成**升级为**交互式 Web 服务**，并增加了**多模态图片识别**、**交互式 K 线图**、**小白式语言生成**等新功能，大幅提升了易用性和实用性。


## 核心功能

多模式输入
支持股票代码、中文名称、模糊搜索，以及上传 K 线截图自动识别股票名称（通过多模态大模型）。

智能技术分析
自动计算 MA、MACD、KDJ、RSI、BOLL、DMI、VR、ROC 等 25 种以上技术指标。

K 线形态识别
识别红三兵、黄昏之星、早晨之星、上升三角形等常见形态。

白话诊断报告
大模型生成技术分析、走势研判、投资建议、风险提示，并用小白也能听懂的语言总结。

交互式 K 线图
基于 ECharts 绘制近 60 个交易日日线图，叠加 MA5/MA10/MA20 均线，并标注支撑位和阻力位。

轻量化教学
内置技术面速成卡片，边看诊断边学习。

## 技术架构

前端：Vue 3 + Tailwind CSS + ECharts

后端：FastAPI + Uvicorn

数据获取：akshare + Ashare（腾讯/新浪财经）

指标计算：MyTT（原项目）+ 部分 TA-Lib

AI 模型：兼容 OpenAI 接口的多模态 LLM（如 GPT-5.6-Luna、DeepSeek 等）


## 使用方法

环境要求：
Python 3.9 及以上版本，pip。

克隆项目：
git clone https://github.com/你的用户名/stock-ai-analyst.git
cd stock-ai-analyst

安装依赖（推荐使用虚拟环境）：
python -m venv venv
source venv/bin/activate（Windows 为 venv\Scripts\activate）
pip install -r requirements.txt

配置环境变量：
在项目根目录创建 .env 文件，填入 LLM API 信息：
LLM_API_KEY=你的API密钥
LLM_BASE_URL=https://api.deepseek.com（或你的服务商地址）
LLM_MODEL=deepseek-chat（或 gpt-5.6-luna 等）

启动后端服务：
python api.py
服务运行在 http://127.0.0.1:8000
Swagger 文档：http://127.0.0.1:8000/docs

打开前端页面：
直接用浏览器打开 frontend/input.html 即可使用。
前端完全静态，无需构建工具，也可部署到任何静态托管服务。

## 项目结构

项目根目录包含以下主要内容：

frontend 文件夹：存放前端静态页面，包括 input.html（输入界面）和 result.html（诊断结果界面，含 K 线图）

public 文件夹：原项目生成的旧报告，可忽略

Ashare.py：数据获取模块（腾讯/新浪财经接口）

MyTT.py：技术指标计算库（原项目）

llm.py：LLM 客户端封装（改造增强版）

main.py：核心分析引擎（改造版）

api.py：FastAPI 服务入口（新增）

models.py：Pydantic 数据模型（新增）

requirements.txt：Python 依赖列表

.env.example：环境变量模板

README.md：项目说明文档

## 注意事项

API 密钥安全：切勿将 .env 文件上传到公开仓库。

数据源：依赖 akshare 和财经网站接口，请保持网络畅通。

大模型能力：若使用图片识别，需确保 LLM 支持多模态（如 gpt-5.6-luna）。

免责声明：本工具仅作为学习研究，不构成任何投资建议，盈亏自负。

## 贡献与鸣谢

本项目基于 Ashare-LLM-Analyst 开发，感谢原作者的开源贡献。

其余部分由Rinow个人完成

欢迎提交 Issue 和 Pull Request。

## 重要免责声明

**非投资建议**：本项目及其生成的任何信息、数据或报告，**均不构成任何形式的投资建议**。所有内容仅供参考和学习，不构成对任何证券、金融产品或其他投资标的的推荐、要约或招揽。

**风险自担**：本软件按“原样”提供，**不提供任何形式的明示或暗示担保**。使用者需自行承担因使用本软件而产生的所有风险，包括但不限于数据错误、分析偏差、投资决策失误等导致的任何直接或间接损失。

**法律责任**：项目作者及贡献者**不对因使用或无法使用本软件而产生的任何索赔、损害或其他责任负责**。

**合规使用**：用户应确保其对本软件的使用符合所有适用的法律法规。

使用本软件即表示您已阅读、理解并同意本免责声明。

## 许可证

[MIT License](LICENSE)
