import pandas as pd

# 1. 加载两个原始数据集
# 请将文件名替换为你本地下载的实际文件名
dengue_df = pd.read_csv('dengue_data_malaysia.csv')
weather_df = pd.read_csv('weather_data_malaysia.csv')

# 2. 预检：打印列名以确保我们能找到 Year, State, Cases, Rainfall 等字段
print("骨痛热症列名:", dengue_df.columns)
print("天气数据列名:", weather_df.columns)

# 3. 核心步骤：标准化“州属 (State)”名称，必须与 TopoJSON 完全对齐
# 假设原始数据里有空格，或者把马六甲写成了 Malacca，把吉隆坡写成了 KL
state_mapping = {
    'Malacca': 'Melaka',
    'Kuala Lumpur Territory': 'Kuala Lumpur',
    'Penang Island': 'Penang',
    'Pinang': 'Penang'
    # 如果你在打印数据时发现其他拼写不一致，可以在这里继续添加映射
}

# 去除前后空格并替换拼写
dengue_df['State'] = dengue_df['State'].astype(str).str.strip().replace(state_mapping)
weather_df['State'] = weather_df['State'].astype(str).str.strip().replace(state_mapping)

# 4. 聚合天气数据
# 如果 Kaggle 的天气数据是“每天”或“每个气象站”的，数据量太大（会违反作业几兆字节的限制）
# 我们需要将其按 [Year, State] 分组，计算年总降雨量和年平均气温
weather_summary = weather_df.groupby(['Year', 'State']).agg({
    'Rainfall': 'sum',          # 计算一年总降雨量
    'Temperature': 'mean'       # 计算一年平均气温
}).reset_index()

# 5. 合并数据集 (Inner Join)
# 这一步将通过 Year 和 State 两个共有键，把病例数和天气指标拼到同一行
derived_data = pd.merge(dengue_df, weather_summary, on=['Year', 'State'], how='inner')

# 6. 检查最终生成的数据样本
print("\n成功合并后的派生数据预览:")
print(derived_data.head())

# 7. 导出为干净、轻量化的 CSV 文件供 Vega-Lite 读取
derived_data.to_csv('malaysia_dengue_weather_derived.csv', index=False)
print("\n文件已成功保存为：malaysia_dengue_weather_derived.csv")