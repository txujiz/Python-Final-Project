# Python-Final-Project
**專案狀態**：Phase 4 - 自動化報告與幾何最佳化完成  
**開發者**：txujiz  
**語言**：Python 3.9.10

## 1. 專案簡介 (Abstract)
本專案旨在解決建築實務中，面積計算依賴人工描繪或像素計算導致的精度誤差與效率低落問題。本專案提出一套基於 Python 的自動化框架，直接解析向量格式（AutoCAD DXF），實現面積精確計算。

目前階段已完成開發環境建置，驗證了從 CAD 到 Python 的數據串接流程，並實現了**梯形剖分 (Trapezoidal Decomposition)** 與**自動化計算書生成**功能。

## 2. 當前進度 (Current Progress)
截至 2025/12/10，本專案已完成以下關鍵里程碑：

* **[A] 函式庫整合**：成功安裝並整合 `ezdxf` (CAD 解析)、`shapely` (幾何運算)、`matplotlib` (數據視覺化)。
* **[B] DXF 檔案讀取**：建立讀取 AutoCAD 2010/2013 ASCII DXF 格式的標準流程。
* **[C] 幾何最佳化切割**：
    * 實作**垂直剖分法**，將任意多邊形切割為矩形、梯形與三角形。
    * 實作**智慧合併演算法**，自動修復過度切割的碎塊 (如將兩個直角三角形合併為大三角形)。
* **[D] 自動化計算書**：
    * 依據「人類視覺邏輯 (Rounding First)」判斷形狀 (Rect/Tri/Trap)。
    * 自動標註 A, B, C 編號與長寬尺寸。
    * 生成符合建築法規需求的面積計算算式。

## 3. 系統需求 (Prerequisites)
本專案依賴以下 Python 函式庫，請確保已安裝：

* **ezdxf**: 用於讀取與寫入 DXF 檔案。
* **shapely**: 基於 GEOS 引擎，處理幾何拓撲與面積計算。
* **matplotlib**: 用於繪製切割後的幾何圖形與視覺化驗證。

**安裝指令：**
pip install ezdxf shapely matplotlib

4. 專案結構 (File Structure)
Plaintext

Python-Final-Project/
├── data/
│   ├── input/         # (規劃中) 放置來源 .dxf 檔案
│   └── output/        # (規劃中) 輸出報告與圖表
├── final_app.py       # 整合版主程式 (包含演算法核心與繪圖)
├── python_plan_try.dxf # 測試用建築平面圖
└── README.md          # 專案說明文件

5. CAD 前置處理規範 (Preprocessing)
為了確保演算法正確運行，輸入的 DXF 檔需遵守以下規範：

單一圖層：將需計算的邊界獨立輸出成一個檔案。

封閉多段線：所有空間邊界必須是閉合的 Polyline (Closed=True)。

格式轉換：需另存為 AutoCAD 2013 ASCII DXF 格式。

幾何清理：避免重疊線或極微小的自交 (Self-intersection)。

6. 後續開發路線 (Roadmap)
本研究預計分為四個階段執行：

[x] Phase 1 (Done): 環境建置與基礎三角分割驗證。

[x] Phase 2 (Done): 實作直角多邊形與梯形剖分 (Decomposition)。

[ ] Phase 3 (Planned): 處理圓弧與曲線邊界（混合解析模型）。

[x] Phase 4 (Done): 自動生成包含算式的文字報告。