# Python-Final-Project
專案狀態：Phase 1 - 環境建置與基礎幾何解析

開發者：txujiz

語言： Python 3.9

1. 專案簡介 (Abstract)
本專案旨在解決建築實務中，面積計算依賴人工描繪或像素計算導致的精度誤差與效率低落問題。本專案提出一套基於 Python 的自動化框架，直接解析向量格式（AutoCAD DXF），跳過影像辨識步驟，實現「無限解析度」的精確計算。目前階段已完成開發環境建置，並驗證了從 CAD 到 Python 的數據串接流程，初步實現基礎三角剖分（Triangulation）功能。

2. 當前進度 (Current Progress)
截至 2025/12，本專案已完成 Phase 1: MVP 原型驗證：

[x] 函式庫整合：成功安裝並整合 ezdxf (CAD 解析)、shapely (幾何運算)、matplotlib (數據視覺化)。

[x] DXF 檔案讀取：建立讀取 AutoCAD 2010/2013 ASCII DXF 格式的標準流程。

[x] 基礎幾何轉換：實現將 DXF Polyline 轉換為 Shapely Polygon 物件的邏輯。

3. 系統需求 (Prerequisites)
本專案依賴以下 Python 函式庫，請確保已安裝：

ezdxf: 用於讀取與寫入 DXF 檔案。

shapely: 基於 GEOS 引擎，處理幾何拓撲與面積計算。

matplotlib: 用於繪製切割後的幾何圖形與視覺化驗證。

安裝指令：

Bash
pip install ezdxf shapely matplotlib

4. 專案結構 (File Structure)
Plaintext

Project_Root/
├── data/
│   ├── input/         # 放置處理好的 .dxf 來源檔案 (需清理雜訊)
│   └── output/        # 輸出的面積計算報告與視覺化圖表
├── src/
│   └── main.py        # 主程式 (目前開發中)
└── README.md          # 專案說明文件

5. CAD 前置處理規範 (Preprocessing)
為了確保演算法正確運行，輸入的 DWG/DXF 檔需遵守以下規範：

圖層分離：將需計算的邊界線獨立放置於特定圖層。

封閉多段線：所有空間邊界必須是閉合的 Polyline (Closed=True)。

格式轉換：需另存為 AutoCAD 2013 ASCII DXF 格式。

6. 後續開發路線 (Roadmap)
本研究預計分為三個階段執行：

Phase 1 (Done):環境建置與基礎三角剖分驗證。

Phase 2 (In Progress):實作直角多邊形的矩形最佳化切割 (Rectangular Decomposition)。

開發二分圖匹配演算法以最小化分割數量。

Phase 3 (Planned):處理圓弧與曲線邊界（混合解析模型）。

Phase 4 (Planned):自動生成包含算式的文字報告。
