import numpy as np
from pyteomics import mzml
import pandas as pd

def process_mzml(file_path):
    """
    读取mzML文件，提取保留时间、m/z值和强度数据，并进行初步处理。
    参数:
        file_path (str): mzML文件的路径
    返回:
        dict: 键为保留时间，值为(m/z数组, 强度数组)的字典
    """
    with mzml.read(file_path) as reader:
        retention_mz_intensity = {}
        for spectrum in reader:
            retention_time = spectrum['scanList']['scan'][0]['scan start time']
            mz_values = spectrum['m/z array']
            intensity = spectrum['intensity array']
            intensity = np.where(intensity < 1000, 0, intensity)  # 过滤强度小于1000的噪声
            if retention_time in retention_mz_intensity:
                existing_mz, existing_intensity = retention_mz_intensity[retention_time]
                retention_mz_intensity[retention_time] = (
                    np.concatenate([existing_mz, mz_values]), existing_intensity + intensity)
            else:
                retention_mz_intensity[retention_time] = (mz_values, intensity)
    return retention_mz_intensity

def create_dataframe(retention_mz_intensity):
    """
    将mzML提取的数据转换为pandas DataFrame，m/z值为列名，保留时间为索引。
    参数:
        retention_mz_intensity (dict): 包含保留时间、m/z和强度数据的字典
    返回:
        pd.DataFrame: 转换后的数据表格
    """
    all_mz_ranges = set()
    for mz, _ in retention_mz_intensity.values():
        all_mz_ranges.update(map(int, mz))  # 收集所有m/z范围（取整）

    retention_intensity_sum = {}
    for retention_time, (mz, intensity) in retention_mz_intensity.items():
        mz_intensity_sum = {}
        for mz_val, inten in zip(mz, intensity):
            mz_range = round(mz_val)  # 将m/z值取整
            mz_intensity_sum[mz_range] = mz_intensity_sum.get(mz_range, 0) + inten
        for mz_range in all_mz_ranges:
            mz_intensity_sum.setdefault(mz_range, 0)  # 未出现的m/z设为0
        retention_intensity_sum[retention_time] = mz_intensity_sum

    df = pd.DataFrame.from_dict(retention_intensity_sum, orient='index')
    df = df.reindex(columns=sorted(df.columns))  # 按m/z值排序列
    return df

def process_excel(df, Sampling_points_needed, integer_range_start, integer_range_end):
    """
    根据用户指定的每分钟采样点数，在保留时间整数范围内插入额外行，填充平均值。
    参数:
        df (pd.DataFrame): 原始数据表格
        Sampling_points_needed (int): 每分钟需要的采样点数
        integer_range_start (int): 保留时间范围的起始整数
        integer_range_end (int): 保留时间范围的结束整数
    返回:
        pd.DataFrame: 插入额外行后的数据表格
    """
    retention_times = df.index.values
    int_part = np.floor(retention_times).astype(int)
    all_insert_indices = []
    total_rows = 0

    for i in range(integer_range_start, integer_range_end):
        indices = np.where(int_part == i)[0]
        current_len = len(indices)
        extra_rows = Sampling_points_needed - current_len
        if extra_rows > 0:
            average_interval = current_len / (extra_rows + 1)
            insert_positions = np.linspace(0, current_len, extra_rows + 1, endpoint=False)[1:]
            insert_indices = [indices[int(pos)] for pos in insert_positions if pos < len(indices)]
            all_insert_indices.extend(insert_indices)
        total_rows += current_len + max(extra_rows, 0)

    retention_times_list = list(retention_times)
    main_numbers = [df[col].values for col in df.columns]
    inserted_retention_times = retention_times_list.copy()
    inserted_main_numbers = [list(col) for col in main_numbers]

    for pos in sorted(all_insert_indices, reverse=True):
        if pos == 0:
            new_rt = retention_times_list[0]
            new_values = [col[0] for col in main_numbers]
        elif pos >= len(retention_times_list):
            new_rt = retention_times_list[-1]
            new_values = [col[-1] for col in main_numbers]
        else:
            new_rt = (retention_times_list[pos-1] + retention_times_list[pos]) / 2
            new_values = [(main_numbers[i][pos-1] + main_numbers[i][pos]) / 2 for i in range(len(main_numbers))]
        inserted_retention_times.insert(pos, new_rt)
        for j, inserted_list in enumerate(inserted_main_numbers):
            inserted_list.insert(pos, new_values[j])

    result_df = pd.DataFrame(dict(zip(df.columns, inserted_main_numbers)), index=inserted_retention_times)
    result_df.columns = df.columns
    return result_df

def process_eroi_data(row_df, eroi_data, mz_min, mz_max, retention_start, retention_end):
    """
    根据m/z范围和保留时间范围筛选数据，并保存为Excel文件。

    参数:
        row_df (pd.DataFrame): 处理后的数据表格
        eroi_data (str): 输出Excel文件路径
        mz_min (float): m/z范围的最小值
        mz_max (float): m/z范围的最大值
        retention_start (float): 保留时间范围的起始值
        retention_end (float): 保留时间范围的结束值
    """
    columns = row_df.columns.astype(float)
    selected_columns = [col for col in columns if mz_min <= col <= mz_max]  # 筛选m/z范围内的列
    selected_df = row_df[selected_columns]
    selected_df = selected_df[(selected_df.index >= retention_start) & (selected_df.index <= retention_end)]  # 筛选保留时间范围内的行
    selected_df.to_excel(eroi_data, index=True)  # 保存为Excel文件
