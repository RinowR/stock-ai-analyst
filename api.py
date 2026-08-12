# api.py
import os
import re
import json
import uvicorn
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import akshare as ak
import pandas as pd

load_dotenv()
from main import StockAnalyzer

app = FastAPI(title="智诊股 API", description="支持股票名称模糊搜索与图片识别", version="2.2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- 股票缓存（内存 + 文件） -------------------
_STOCK_LIST_CACHE = None
CACHE_FILE = "stock_cache.json"  # 缓存文件路径

def get_stock_list():
    """
    获取沪深A股列表，优先从内存读取，其次从文件读取，最后从网络加载。
    """
    global _STOCK_LIST_CACHE
    if _STOCK_LIST_CACHE is not None:
        return _STOCK_LIST_CACHE

    # 1. 尝试从文件加载
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                _STOCK_LIST_CACHE = json.load(f)
            print(f"✅ 从本地缓存加载 {len(_STOCK_LIST_CACHE)} 只股票")
            return _STOCK_LIST_CACHE
        except Exception as e:
            print(f"⚠️ 本地缓存加载失败: {e}")

    # 2. 从网络加载（东方财富）
    try:
        print("📥 正在从东方财富加载股票列表...")
        df = ak.stock_zh_a_spot_em()
        mapping = {}
        for _, row in df.iterrows():
            name = row['名称'].strip()
            code = row['代码'].strip()
            if code.startswith('6'):
                ashare_code = f"sh{code}"
            elif code.startswith(('0', '3')):
                ashare_code = f"sz{code}"
            else:
                continue
            mapping[name] = ashare_code
        _STOCK_LIST_CACHE = mapping
        # 保存到文件
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        print(f"✅ 加载并缓存 {len(mapping)} 只股票")
    except Exception as e:
        print(f"❌ 东方财富加载失败: {e}，尝试备用源...")
        try:
            df = ak.stock_info_a_code_name()
            mapping = {}
            for _, row in df.iterrows():
                name = row['name'].strip()
                code = row['code'].strip()
                if code.startswith('6'):
                    ashare_code = f"sh{code}"
                elif code.startswith(('0', '3')):
                    ashare_code = f"sz{code}"
                else:
                    continue
                mapping[name] = ashare_code
            _STOCK_LIST_CACHE = mapping
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
            print(f"✅ 备用源加载并缓存 {len(mapping)} 只股票")
        except Exception as e2:
            print(f"❌ 备用源也失败: {e2}")
            _STOCK_LIST_CACHE = {}
    return _STOCK_LIST_CACHE

# ------------------- 解析函数 -------------------
def resolve_stock_code(user_input: str) -> str:
    user_input = user_input.strip()
    if not user_input:
        raise ValueError("输入为空")
    if user_input.startswith(('sh', 'sz')):
        return user_input
    if user_input.isdigit() and len(user_input) == 6:
        if user_input.startswith('6'):
            return f"sh{user_input}"
        elif user_input.startswith(('0', '3')):
            return f"sz{user_input}"
        else:
            raise ValueError(f"无法识别代码 {user_input}")
    # 尝试提取中文名称
    chinese_match = re.search(r'[\u4e00-\u9fa5]+', user_input)
    if chinese_match:
        name_part = chinese_match.group()
        stock_map = get_stock_list()
        if not stock_map:
            raise ValueError("股票列表未加载")
        # 精确匹配
        for name, code in stock_map.items():
            if name == name_part:
                return code
        # 模糊匹配（包含关系）
        matches = []
        for name, code in stock_map.items():
            if name_part in name:
                matches.append((name, code))
        if matches:
            matches.sort(key=lambda x: len(x[0]))
            return matches[0][1]
    # 最终模糊匹配
    stock_map = get_stock_list()
    if not stock_map:
        raise ValueError("股票列表未加载")
    lower_input = user_input.lower()
    matches = []
    for name, code in stock_map.items():
        if lower_input in name.lower():
            matches.append((name, code))
    if not matches:
        raise ValueError(f"未找到包含 '{user_input}' 的股票")
    matches.sort(key=lambda x: len(x[0]))
    return matches[0][1]

# ------------------- 分析器单例 -------------------
_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = StockAnalyzer(
            {},
            llm_api_key=os.environ.get("LLM_API_KEY"),
            llm_base_url=os.environ.get("LLM_BASE_URL"),
            llm_model=os.environ.get("LLM_MODEL"),
        )
    return _analyzer

# ------------------- 启动预加载（可选） -------------------
@app.on_event("startup")
async def startup_event():
    """服务启动时异步预热股票缓存，确保首次请求快速响应"""
    import asyncio
    # 在后台线程加载，不阻塞启动
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, get_stock_list)

# ------------------- API 路由 -------------------
@app.post("/api/diagnose")
async def diagnose(stock_code: str = Form(...)):
    if not stock_code or not stock_code.strip():
        raise HTTPException(status_code=400, detail="股票代码/名称不能为空")

    try:
        code = resolve_stock_code(stock_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    analyzer = get_analyzer()
    analyzer.stock_codes = [code]
    analyzer.stock_names = {code: code}
    analyzer.fetch_data()
    if code not in analyzer.data:
        raise HTTPException(status_code=404, detail=f"数据获取失败 {code}")

    try:
        result = analyzer.get_structured_analysis(code)

        # 补全中文名称
        if result and result.get('stock') == code:
            stock_map = get_stock_list()
            for name, c in stock_map.items():
                if c == code:
                    result['stock'] = name
                    break

        # ---------- OHLC 提取 ----------
        try:
            df = analyzer.data.get(code)
            if df is not None and not df.empty:
                required = ['open', 'high', 'low', 'close']
                if all(col in df.columns for col in required):
                    ohlc_df = df[required].tail(60).copy()
                    ohlc_df['time'] = ohlc_df.index.strftime('%Y-%m-%d')
                    ohlc_df = ohlc_df[['time', 'open', 'high', 'low', 'close']]
                    result['ohlc'] = ohlc_df.to_dict(orient='records')
                else:
                    result['ohlc'] = []
            else:
                result['ohlc'] = []
        except Exception as e:
            print(f"⚠️ OHLC提取失败: {e}")
            result['ohlc'] = []

        return {"status": "success", "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/api/search")
async def search_stocks(q: str = ""):
    if not q or len(q.strip()) < 1:
        return {"status": "success", "data": []}
    keyword = q.strip().lower()
    stock_map = get_stock_list()
    if not stock_map:
        return {"status": "error", "message": "股票列表未加载"}
    candidates = []
    for name, code in stock_map.items():
        if keyword in name.lower():
            candidates.append({"name": name, "code": code})
    candidates.sort(key=lambda x: len(x["name"]))
    return {"status": "success", "data": candidates[:10]}

@app.post("/api/recognize")
async def recognize_stock(image: UploadFile = File(...)):
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    image_bytes = await image.read()
    analyzer = get_analyzer()
    llm = analyzer.llm
    if not llm:
        raise HTTPException(status_code=500, detail="LLM 未初始化，请检查 API Key 配置")
    try:
        name = llm.recognize_stock_from_image(image_bytes)
        if not name:
            return {"status": "error", "message": "未能识别出股票名称，请手动输入"}
        # 清洗名称
        chinese_match = re.search(r'[\u4e00-\u9fa5]+', name)
        if chinese_match:
            clean_name = chinese_match.group()
        else:
            clean_name = name.split()[0] if name.split() else name
        clean_name = clean_name.strip()
        # 查找代码
        stock_map = get_stock_list()
        ashare_code = None
        for stock_name, code in stock_map.items():
            if stock_name == clean_name:
                ashare_code = code
                break
        if not ashare_code:
            # 模糊匹配
            for stock_name, code in stock_map.items():
                if clean_name in stock_name or stock_name in clean_name:
                    ashare_code = code
                    break
        if ashare_code:
            return {"status": "success", "data": {"name": clean_name, "code": ashare_code}}
        else:
            return {"status": "success", "data": {"name": clean_name, "code": None, "message": "未找到对应代码，请手动输入"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")

@app.get("/")
async def root():
    return {"message": "智诊股 API v2.2", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)