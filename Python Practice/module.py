# 載入模組
import sys
print(sys.platform)

# 使用 package 結構匯入 geometry 模組（不需要 sys.path.append）
from modules.geometry import distance, slope

result = distance(1, 1, 5, 5)
print(result)

result = slope(1, 2, 5, 6)
print(result)
