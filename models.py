# models.py
from pydantic import BaseModel
from typing import List, Optional

class TradeBiasItem(BaseModel):
    """买卖倾向子项"""
    direction: str          # bullish / bearish / neutral
    title: str
    dimension: str
    condition: str
    reason: str

class DiagnosisResponse(BaseModel):
    """前端结论展示页面所需的全部字段（共 30+ 个）"""
    # 基础信息
    stock: str
    code: str
    price: str
    change: str
    volume: str
    updateTime: str
    
    # 趋势判断
    trend: str              # up / down
    trendLabel: str         # 上升趋势 / 调整态势
    
    # K线形态
    pattern: str
    patternSignal: str      # bullish / bearish
    patternSignalLabel: str # 看涨 / 看跌
    patternDesc: str
    
    # 均线系统
    ma5: str
    ma10: str
    ma20: str
    maDesc: str
    
    # 成交量
    volumeStatus: str
    volumeSignal: str       # bullish / bearish / neutral
    volumeSignalLabel: str
    volumeDesc: str
    
    # 综合健康度（0-100）
    health: int
    
    # 赚钱效应
    profitability: float
    profitabilityLabel: str
    profitabilityDesc: str
    
    # 市场热度
    marketHeat: float
    heatLabel: str
    heatDesc: str
    
    # 买卖力量
    powerBalance: str
    powerSignal: str
    powerLabel: str
    buyRatio: float
    powerDesc: str
    
    # 地板价 & 天花板
    floorPrice: str
    floorDesc: str
    ceilingPrice: str
    ceilingDesc: str
    
    # 教学与建议
    patternScience: str
    tradeBias: str
    beginnerAdvice: str
    summary: str
    tags: List[str]
    
    # 买卖倾向列表（支持多条）
    tradeBiasItems: List[TradeBiasItem]