"""
Author: HPC2H2
Date: 2025-07-22
Version: 1.0
Coding: UTF-8
License: MIT
Description: strategy_builder.py
"""

class StrategyBuilder:
    def __init__(self):
        self.cards = []
        self.probability = None
    
    def add_card(self, card):
        """添加一张卡片"""
        if card is not None:
            self.cards.append(str(card))
        return self  # 支持链式调用
    
    def set_probability(self, p):
        """设置概率"""
        self.probability = p
        return self
    
    def build(self):
        """构建最终策略字符串"""
        strategy = " 使用卡片:" + " ".join(self.cards)
        if self.probability is not None:
            strategy += " 成功概率：" + str(self.probability)
        return strategy