import ezdxf
import matplotlib.pyplot as plt
import numpy as np
import string
import os
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import split, orient, unary_union


# 第一部分：演算法核心 (直接整合在這裡)

class TrapezoidalDecomposer:
    def __init__(self, polygon):
        # 基礎清理
        clean_poly = polygon.buffer(0)
        self.original_polygon = orient(clean_poly, sign=1.0)

    def decompose(self):
        """
        執行垂直分解 + 智慧合併
        """
        # --- 階段一：垂直切割 ---
        poly = self.original_polygon
        minx, miny, maxx, maxy = poly.bounds
        
        xs = set()
        for x, y in poly.exterior.coords:
            xs.add(round(x, 4))
        sorted_xs = sorted(list(xs))
        cut_xs = sorted_xs[1:-1]
        
        vertical_lines = []
        for x in cut_xs:
            line = LineString([(x, miny - 100), (x, maxy + 100)])
            vertical_lines.append(line)
            
        current_pieces = [poly]
        for line in vertical_lines:
            new_pieces = []
            for piece in current_pieces:
                if piece.intersects(line):
                    try:
                        split_result = split(piece, line)
                        new_pieces.extend(list(split_result.geoms))
                    except:
                        new_pieces.append(piece)
                else:
                    new_pieces.append(piece)
            current_pieces = new_pieces

        initial_pieces = []
        for part in current_pieces:
            if isinstance(part, Polygon) and part.area > 0.001:
                initial_pieces.append(part)

        # --- 階段二：智慧合併 ---
        merged_pieces = self.merge_recursive(initial_pieces)
        merged_pieces.sort(key=lambda p: (p.bounds[0], -p.bounds[3]))
        return merged_pieces

    def merge_recursive(self, pieces):
        while True:
            merged = False
            new_list = []
            skip_indices = set()
            n = len(pieces)
            for i in range(n):
                if i in skip_indices: continue
                poly_a = pieces[i]
                merged_this_round = False
                for j in range(i + 1, n):
                    if j in skip_indices: continue
                    poly_b = pieces[j]
                    if poly_a.touches(poly_b) or poly_a.distance(poly_b) < 0.001:
                        try:
                            union_poly = unary_union([poly_a, poly_b])
                            check_poly = union_poly.simplify(0.05, preserve_topology=False)
                            if isinstance(check_poly, Polygon):
                                coords_count = len(list(check_poly.exterior.coords)) - 1
                                is_simple = coords_count <= 4
                                is_rect_area = abs(check_poly.area - check_poly.envelope.area) < 0.01
                                if is_simple or is_rect_area:
                                    new_list.append(union_poly)
                                    skip_indices.add(j)
                                    merged_this_round = True
                                    merged = True
                                    break 
                        except:
                            pass
                if not merged_this_round:
                    new_list.append(poly_a)
            pieces = new_list
            if not merged: break
        return pieces

    def get_display_info(self, poly):
        """
        【最終修正邏輯】
        完全依照「顯示的數字」來決定形狀。
        如果顯示數字說它是矩形，它就是矩形。
        """
        poly = poly.buffer(0)
        minx, miny, maxx, maxy = poly.bounds
        width = maxx - minx
        coords = list(poly.exterior.coords)[:-1]
        
        left_ys = [p[1] for p in coords if abs(p[0] - minx) < 0.001]
        right_ys = [p[1] for p in coords if abs(p[0] - maxx) < 0.001]
        
        raw_h_left = max(left_ys) - min(left_ys) if left_ys else 0
        raw_h_right = max(right_ys) - min(right_ys) if right_ys else 0
        
        # 1. 取得顯示數值 (Display Values)
        w_disp = round(width, 2)
        hl_disp = round(raw_h_left, 2)
        hr_disp = round(raw_h_right, 2)
        area_disp = round(poly.area, 2)
        
        # 2. 判斷形狀 (Shape Definition)
        # 優先順序 1: 矩形 (顯示高度相等)
        if hl_disp == hr_disp:
            shape_type = 'Rect'
            formula = f"{w_disp} × {hl_disp} = {area_disp} $m^2$ (矩形)"
            
        # 優先順序 2: 三角形 (其中一邊顯示為0)
        elif hl_disp == 0 or hr_disp == 0:
            shape_type = 'Tri'
            base = max(hl_disp, hr_disp)
            if base == 0: base = w_disp # 橫向三角形特例
            formula = f"{w_disp} × {base} ÷ 2 = {area_disp} $m^2$ (三角形)"
            
        # 優先順序 3: 梯形
        else:
            shape_type = 'Trap'
            formula = f"({hl_disp}+{hr_disp}) × {w_disp} ÷ 2 = {area_disp} $m^2$ (梯形)"
            
        return {
            'min_x': minx, 'max_x': maxx, 'min_y': miny,
            'mid_y_left': (min(left_ys) + max(left_ys))/2 if left_ys else miny,
            'mid_y_right': (min(right_ys) + max(right_ys))/2 if right_ys else miny,
            'w_disp': w_disp, 'hl_disp': hl_disp, 'hr_disp': hr_disp,
            'formula': formula, 'label': shape_type
        }


# 第二部分：主程式與繪圖

def get_label(index):
    alphabet = string.ascii_uppercase
    if index < 26: return alphabet[index]
    else: return alphabet[index // 26 - 1] + alphabet[index % 26]

def main():
    # 設定檔名 (請確認你的 DXF 檔名正確)
    dxf_filename = "python_plan_try.dxf"
    
    if not os.path.exists(dxf_filename):
        print(f"錯誤：找不到檔案 {dxf_filename}")
        return

    # 讀取 DXF
    try:
        doc = ezdxf.readfile(dxf_filename)
        msp = doc.modelspace()
    except Exception as e:
        print(f"讀取錯誤: {e}")
        return
        
    # 單位換算
    units = doc.header.get('$INSUNITS', 0)
    scale = 1.0
    area_divisor = 1.0
    if units == 4: # mm
        scale = 0.001
        area_divisor = 1000000.0
    elif units == 5: # cm
        scale = 0.01
        area_divisor = 10000.0

    # 提取多邊形
    polygons = []
    for line in msp.query('LWPOLYLINE'):
        if line.is_closed:
            pts = line.get_points()
            if len(pts) >= 3:
                # 先把單位轉成公尺 (m)
                scaled_pts = [(p[0]*scale, p[1]*scale) for p in pts]
                poly = Polygon(scaled_pts).buffer(0)
                if poly.area > 0.01:
                    polygons.append(poly)

    if not polygons:
        print("沒有找到有效多邊形")
        return

    # 繪圖設定
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
    plt.rcParams['axes.unicode_minus'] = False 
    fig, ax = plt.subplots(figsize=(16, 10))
    plt.subplots_adjust(right=0.7)
    
    total_area = 0
    report_lines = []
    idx = 0

    print("--- 開始計算 (優先採用四捨五入邏輯) ---")

    for poly in polygons:
        decomposer = TrapezoidalDecomposer(poly)
        pieces = decomposer.decompose()
        
        for piece in pieces:
            # 取得顯示資訊
            info = decomposer.get_display_info(piece)
            
            # 準備標籤
            label_id = get_label(idx)
            idx += 1
            total_area += piece.area # 已經轉過單位了，直接加
            
            # 加入報告字串
            report_lines.append(f"{label_id}: {info['formula']}")
            print(f"處理區塊 {label_id}: {info['label']} - {info['formula']}")

            # 繪圖
            x, y = piece.exterior.xy
            ax.fill(x, y, fc='#E0F7FA', edgecolor='black', linewidth=1.5, alpha=0.9)
            
            # 標註編號
            cx, cy = piece.centroid.x, piece.centroid.y
            ax.text(cx, cy, label_id, fontsize=14, ha='center', va='center', color='red', weight='bold')
            
            # 標註尺寸
            # 寬度
            ax.text((info['min_x']+info['max_x'])/2, info['min_y'], f"{info['w_disp']:.2f}", 
                    fontsize=9, ha='center', va='top', color='blue')
            # 左高
            if info['hl_disp'] > 0:
                ax.text(info['min_x'], info['mid_y_left'], f"{info['hl_disp']:.2f}", 
                        fontsize=9, ha='right', va='center', color='green', rotation=90)
            # 右高
            if info['hr_disp'] > 0:
                ax.text(info['max_x'], info['mid_y_right'], f"{info['hr_disp']:.2f}", 
                        fontsize=9, ha='left', va='center', color='green', rotation=90)

    # 顯示總結
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f"建築面積計算圖 (人工轉正版)\n總面積: {total_area:.2f} $m^2$", fontsize=20)
    
    report_text = "【面積計算書】\n\n" + "\n\n".join(report_lines)
    fig.text(0.75, 0.85, report_text, fontsize=11, family='Microsoft JhengHei', va='top')
    
    plt.show()

if __name__ == "__main__":
    main()