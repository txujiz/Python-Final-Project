import networkx as nx
import numpy as np
from shapely.geometry import Polygon, LineString

class RectangularDecomposer:
    def __init__(self, polygon):
        # 確保輸入的是 Shapely Polygon
        self.poly = polygon
        # 確保頂點順序是逆時針 (CCW)，這樣我們才能統一邏輯：
        # 左轉 = 凸 (Convex), 右轉 = 凹 (Concave/Reflex)
        if not self.poly.exterior.is_ccw:
            self.poly = Polygon(self.poly.exterior.coords[::-1])
            
        self.reflex_verts = []
        self.h_chords = [] 
        self.v_chords = [] 

    def find_reflex_vertices(self):
        """
        步驟 2: 找出所有內角 > 180 (通常是 270) 的凹點
        邏輯：沿著逆時針走，如果遇到「右轉」，那就是凹點。
        """
        coords = list(self.poly.exterior.coords)
        # 移除最後一個重複的閉合點
        if coords[0] == coords[-1]:
            coords.pop()
            
        n = len(coords)
        self.reflex_verts = [] # 清空列表

        for i in range(n):
            # 取出前一點(p_prev)、當前點(p_curr)、下一點(p_next)
            p_prev = coords[i - 1]      # i=0 時，prev 就是最後一點，Python list 支援負索引，很方便
            p_curr = coords[i]
            p_next = coords[(i + 1) % n] # 用餘數確保轉一圈回到 0

            # 建立向量 v1 (前->中) 和 v2 (中->後)
            v1 = np.array(p_curr) - np.array(p_prev)
            v2 = np.array(p_next) - np.array(p_curr)

            # 計算二維外積 (Cross Product)
            # z > 0: 左轉 (凸點 90度)
            # z < 0: 右轉 (凹點 270度)
            cross_product = np.cross(v1, v2)

            if cross_product < -1e-6: # 加一點容許值避免浮點數誤差
                print(f"找到凹點: {p_curr}")
                self.reflex_verts.append(p_curr)

        return self.reflex_verts

    def generate_chords(self):
        """步驟 3: 從凹點發射射線 (目前先留空)"""
        pass

    def optimize_cuts(self):
        """步驟 4: 二分圖匹配 (目前先留空)"""
        pass
        
    def execute(self):
        """步驟 5: 執行切割"""
        # 1. 先找凹點
        self.find_reflex_vertices()
        
        # (後面步驟還沒寫，暫時先回傳空的)
        return []