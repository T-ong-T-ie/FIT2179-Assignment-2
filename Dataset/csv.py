import pandas as pd

# 1. 加载数据集
try:
    # 从 Excel 文件加载登革热数据
    dengue_df = pd.read_excel('Dataset Denggi Malaysia.xlsx')
    # 从 CSV 文件加载天气数据
    weather_df = pd.read_csv('full_weather.csv')
except FileNotFoundError as e:
    print(f"错误：找不到数据文件 - {e}。请确保所有数据文件都在 'Dataset' 文件夹中。")
    exit()

# 2. 预检并重命名列
print("原始登革热数据列名:", dengue_df.columns)
print("原始天气数据列名:", weather_df.columns)

# 为了稳健性，我们尝试重命名登革热数据中可能存在的不同列名
dengue_df.rename(columns={
    'YEAR': 'Year',
    'STATE': 'State',
    'CASES': 'Cases'
}, inplace=True, errors='ignore')

# 检查必要的列是否存在
required_dengue_cols = ['Year', 'State', 'Cases']
if not all(col in dengue_df.columns for col in required_dengue_cols):
    print(f"登革热数据缺少必要的列: {required_dengue_cols}。请检查 Excel 文件。")
    exit()


# 3. 处理登革热数据
# 登革热数据可能是每周的，我们需要按年份和州进行汇总
dengue_summary = dengue_df.groupby(['Year', 'State'])['Cases'].sum().reset_index()

# 4. 处理天气数据
# 将 'datetime' 列转换为日期时间对象，并提取年份
weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
weather_df.dropna(subset=['datetime'], inplace=True) # 删除无法解析的日期行
weather_df['Year'] = weather_df['datetime'].dt.year

# 按年份和州聚合天气数据
weather_summary = weather_df.groupby(['Year', 'state']).agg(
    Yearly_Precipitation_Total=('precipitation_total', 'sum'),
    Average_Temperature=('temperature', 'mean'),
    Average_UV_Index=('uv_index', 'mean')
).reset_index()
weather_summary.rename(columns={'state': 'State'}, inplace=True)

# 5. 标准化州名
# 这是确保能成功合并的关键步骤
state_mapping = {
    'W.P. Kuala Lumpur': 'Kuala Lumpur',
    'W.P. Labuan': 'Labuan',
    'W.P. Putrajaya': 'Putrajaya',
    'Pulau Pinang': 'Penang',
    'N. Sembilan': 'Negeri Sembilan'
    # 在检查数据后，可根据需要添加更多映射
}

dengue_summary['State'] = dengue_summary['State'].str.strip().replace(state_mapping)
weather_summary['State'] = weather_summary['State'].str.strip().replace(state_mapping)

# 6. 合并数据集
# 使用内部合并 (inner join) 来确保合并后的每一行在两个数据集中都有对应
derived_data = pd.merge(dengue_summary, weather_summary, on=['Year', 'State'], how='inner')

# 7. 导出为 CSV
output_filename = 'malaysia_dengue_weather_derived.csv'
# 对浮点数进行四舍五入，使文件更整洁
derived_data['Yearly_Precipitation_Total'] = derived_data['Yearly_Precipitation_Total'].round(2)
derived_data['Average_Temperature'] = derived_data['Average_Temperature'].round(2)
derived_data['Average_UV_Index'] = derived_data['Average_UV_Index'].round(2)

derived_data.to_csv(output_filename, index=False)

print(f"\n数据处理与合并完成，文件已保存为: {output_filename}")
print("\n合并后数据预览:")
print(derived_data.head())
print("\n最终列名:", derived_data.columns.tolist())
