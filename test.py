# test_ashare.py
import Ashare as as_api

# 测试上证指数（sh000001）
print("正在获取上证指数数据...")
try:
    df = as_api.get_price('sh000001', count=10, frequency='1d')
    if df is not None and not df.empty:
        print(f"✅ 数据获取成功！共 {len(df)} 条记录")
        print(f"最新数据:\n{df.tail(2)}")
    else:
        print("❌ 获取的数据为空")
except Exception as e:
    print(f"❌ 数据获取失败: {e}")
    # test_analyzer.py
from main import StockAnalyzer

# 创建一个分析器（不配置 LLM API）
analyzer = StockAnalyzer({'上证指数': 'sh000001'})

# 获取数据
analyzer.fetch_data()

# 生成结构化分析（新增的方法）
try:
    result = analyzer.get_structured_analysis('sh000001')
    print("✅ 结构化分析生成成功！")
    print(f"股票名称: {result['stock']}")
    print(f"当前价格: {result['price']}")
    print(f"健康度: {result['health']}")
    print(f"K线形态: {result['pattern']}")
except Exception as e:
    print(f"❌ 分析失败: {e}")