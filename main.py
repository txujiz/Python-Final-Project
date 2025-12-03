import ezdxf
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import triangulate, unary_union
import os

# 1. 設定中文字型與負號顯示
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False 

def main():
    dxf_filename = "python_plan_try.dxf"
    
    if not os.path.exists(dxf_filename):
        print(f"錯誤: 找不到檔案 '{dxf_filename}'")
        return

    try:
        doc = ezdxf.readfile(dxf_filename)
        msp = doc.modelspace()
    except Exception as e:
        print(f"讀取錯誤: {e}")
        return
    
    # 自動檢查 DXF 單位
    # $INSUNITS 代碼表: 4=mm, 5=cm, 6=m, 0=無單位
    units = doc.header.get('$INSUNITS', 0) 
    
    area_divisor = 1.0 # 預設除數 (如果是公尺就不用除)
    unit_msg = "其他/公尺"

    if units == 4:
        print("偵測到圖檔單位: Millimeters (mm)")
        print("-> 自動啟用換算: 除以 1,000,000")
        area_divisor = 1000000.0
        unit_msg = "毫米 (轉為平方公尺)"
    else:
        print(f"偵測到圖檔單位代碼: {units} (非mm)")
        print("-> 保持原始數值，不進行百萬分率換算")
        area_divisor = 1.0

    # ==========================================
    polygons = []
    lines = msp.query('LWPOLYLINE') 

    for line in lines:
        if line.is_closed:
            points = [(v[0], v[1]) for v in line.get_points()]
            if len(points) >= 3:
                poly = Polygon(points)
                # 修復幾何誤差
                poly = poly.buffer(0)
                if poly.area > 0.01:
                    polygons.append(poly)

    if not polygons:
        print("沒有找到閉合的多邊形。")
        return

    # ---------------------------------------------------------
    # 2. 幾何運算與繪圖，先畫出顏色範圍再切割
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 10))
    total_area_m2 = 0 

    for poly in polygons:
        # 計算精確面積
        total_area_m2 += poly.area / area_divisor

        # 畫底色使多邊形被填滿
        if poly.geom_type == 'Polygon':
            x, y = poly.exterior.xy
            ax.fill(x, y, fc='#87CEEB', alpha=0.6, zorder=1) # 淺藍底色
            ax.plot(x, y, color='black', linewidth=2, zorder=3) # 黑色外框
        elif poly.geom_type == 'MultiPolygon':
            for part in poly.geoms:
                x, y = part.exterior.xy
                ax.fill(x, y, fc='#87CEEB', alpha=0.6, zorder=1)
                ax.plot(x, y, color='black', linewidth=2, zorder=3)

        # 畫切割線
        all_triangles = triangulate(poly)
        
        for tri in all_triangles:
            # 確保線條不凸出去
            try:
                intersect_part = tri.intersection(poly)
                if not intersect_part.is_empty and intersect_part.area > 1e-6:
                    # 這裡只畫線 
                    if intersect_part.geom_type == 'Polygon':
                        x, y = intersect_part.exterior.xy
                        ax.plot(x, y, color='white', linewidth=0.5, zorder=2) # 白線
                    elif intersect_part.geom_type == 'MultiPolygon':
                        for part in intersect_part.geoms:
                            x, y = part.exterior.xy
                            ax.plot(x, y, color='white', linewidth=0.5, zorder=2)
            except:
                pass

    # ---------------------------------------------------------
    # 3. 輸出
    # ---------------------------------------------------------
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title(f"建築面積自動計算\n總面積: {total_area_m2:.2f} 平方公尺 ($m^2$)", fontsize=16)
    print(f"計算完成！總面積: {total_area_m2:.2f} m2")
    plt.show()

if __name__ == "__main__":
    main()