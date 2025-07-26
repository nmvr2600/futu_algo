#  Futu Algo: Algorithmic High-Frequency Trading Framework
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Written by Claude Chan <claude@example.com>, 2025
#  Copyright (c)  billpwchan - All Rights Reserved

import pandas as pd
from filters.Filters import Filters
from util.chanlun import ChanlunProcessor


class ChanlunFilter(Filters):
    def __init__(self, buy_point_type: int = 1, validate_centrals: bool = False, 
                 main_level: str = "day", sub_level: str = "30min"):
        """
        缠论筛选器
        :param buy_point_type: 买点类型 (1: 第一类买点, 2: 第二类买点, 3: 第三类买点)
        :param validate_centrals: 是否验证中枢存在
        :param main_level: 主级别 (如 "day", "week")
        :param sub_level: 次级别 (如 "30min", "5min")
        """
        self.buy_point_type = buy_point_type
        self.validate_centrals = validate_centrals
        self.main_level = main_level
        self.sub_level = sub_level
        self.processor = ChanlunProcessor()
        super().__init__()
    
    def validate(self, input_data: pd.DataFrame, info_data: dict) -> bool:
        """
        验证股票是否符合缠论买点条件
        :param input_data: 股票的K线数据 DataFrame (主级别)
        :param info_data: 股票的基本面数据 dict
        :return: 是否符合筛选条件
        """
        if input_data.empty or len(input_data) < 30:  # 增加数据量要求
            print(f"  数据不足: 空数据或数据量少于30条 ({len(input_data)}条)")
            return False
        
        # 处理主级别的缠论结构
        main_structures = self.processor.process(input_data)
        
        # 验证中枢存在（如果需要）
        if self.validate_centrals and not self.processor.centrals:
            print(f"  中枢验证失败: 需要中枢但未找到中枢")
            return False
            
        # 根据配置的买点类型进行判断
        buy_point_index = None
        if self.buy_point_type == 1:
            # 打印更多关于第一类买点识别的信息
            print(f"  检查第一类买点: 中枢数量={len(self.processor.centrals)}")
            if len(self.processor.centrals) >= 2:
                last_central = self.processor.centrals[-1]
                prev_central = self.processor.centrals[-2]
                print(f"  前一中枢区间: {prev_central.low} - {prev_central.high}")
                print(f"  最后中枢区间: {last_central.low} - {last_central.high}")
                if last_central.low < prev_central.low:
                    print(f"  中枢下移条件满足")
                    if len(input_data) > 20:
                        recent_low = input_data["close"].iloc[-5:].min()
                        prev_low = input_data["close"].iloc[-20:-5].min()
                        print(f"  最近5日最低价: {recent_low}, 前15日最低价: {prev_low}")
                        if recent_low < prev_low:
                            print(f"  创新低条件满足")
                else:
                    print(f"  中枢下移条件不满足")
            buy_point_index = self.processor.identify_first_buy_point(input_data)
        elif self.buy_point_type == 2:
            # 打印更多关于第二类买点识别的信息
            print(f"  检查第二类买点: 中枢数量={len(self.processor.centrals)}, 笔数量={len(self.processor.strokes)}")
            if len(self.processor.centrals) >= 1 and len(self.processor.strokes) >= 3:
                last_central = self.processor.centrals[-1]
                last_stroke = self.processor.strokes[-1]
                print(f"  最后中枢区间: {last_central.low} - {last_central.high}")
                print(f"  最后一笔方向: {'上涨' if last_stroke.direction == 1 else '下跌'}")
                print(f"  最后一笔结束价格: {last_stroke.end_price}")
                if last_stroke.direction == -1:
                    print(f"  最后一笔向下条件满足")
                    if last_stroke.end_price > last_central.low:
                        print(f"  回调不破中枢低点条件满足")
                    else:
                        print(f"  回调不破中枢低点条件不满足: {last_stroke.end_price} <= {last_central.low}")
                else:
                    print(f"  最后一笔向下条件不满足")
            buy_point_index = self.processor.identify_second_buy_point(input_data)
        elif self.buy_point_type == 3:
            # 打印更多关于第三类买点识别的信息
            print(f"  检查第三类买点: 中枢数量={len(self.processor.centrals)}, 笔数量={len(self.processor.strokes)}")
            if len(self.processor.centrals) >= 1 and len(self.processor.strokes) >= 2:
                last_central = self.processor.centrals[-1]
                last_stroke = self.processor.strokes[-1]
                print(f"  最后中枢区间: {last_central.low} - {last_central.high}")
                print(f"  最后一笔方向: {'上涨' if last_stroke.direction == 1 else '下跌'}")
                print(f"  最后一笔结束价格: {last_stroke.end_price}")
                if last_stroke.direction == -1:
                    print(f"  最后一笔向下条件满足")
                    if last_central.low <= last_stroke.end_price <= last_central.high:
                        print(f"  回调在中枢区间内条件满足: {last_central.low} <= {last_stroke.end_price} <= {last_central.high}")
                    else:
                        print(f"  回调在中枢区间内条件不满足: {last_central.low} <= {last_stroke.end_price} <= {last_central.high}")
                else:
                    print(f"  最后一笔向下条件不满足")
            buy_point_index = self.processor.identify_third_buy_point(input_data)
        
        print(f"  买点识别结果: 类型{self.buy_point_type}, 索引={buy_point_index}")
        
        # 如果找到了对应的买点，需要进一步通过次级别确认
        if buy_point_index is not None:
            # 买点在最近的数据中
            if buy_point_index >= len(input_data) - 5:
                print(f"  买点验证通过: 在最近5条数据中找到类型{self.buy_point_type}买点")
                # 在实际应用中，这里应该获取次级别数据进行验证
                # 目前我们简化处理，直接返回True
                return True
            else:
                print(f"  买点位置不符: 买点不在最近5条数据中 (索引={buy_point_index}, 总长度={len(input_data)})")
        else:
            print(f"  未找到买点: 类型{self.buy_point_type}买点未识别到")
        
        return False