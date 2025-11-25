import matplotlib.pyplot as plt
import numpy as np
import os

# --- 1. 参数设置 ---
data_dir = r'H:\Postgraduate\ASDspec\process'  # 请确保路径正确
start_spec_num = 921  # 输出文件的起始编号 (GP901)
end_spec_num = start_spec_num+19    # 输出文件的结束编号
print(f"输出文件名: GP{start_spec_num}_{end_spec_num}")

output_dir = os.path.join(data_dir, f"GP{start_spec_num}_{end_spec_num}")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

n_files = 100   # 文件总数
group_size = 5  # 每5个文件求一次平均

wl_full = np.arange(350, 2501)  # 波长范围 350-2500nm

# --- 2. 定义读取函数 ---
def read_asd_file(fp):
    """读取光谱数据部分"""
    with open(fp, 'r') as f:
        lines = f.readlines()
    
    # 找到数据起始行（以"Wavelength"开头）
    start = 0
    for i, L in enumerate(lines):
        if L.strip().startswith('Wavelength'):
            start = i + 1
            break
            
    refl = []
    for L in lines[start:]:
        parts = L.strip().split()
        if len(parts) < 2:
            continue
        try:
            refl.append(float(parts[1]))
        except ValueError:
            pass
    return np.array(refl)

def get_header_template(fp):
    """
    读取原始文件的头文件信息（Header），直到 'Wavelength' 这一行。
    返回 header 的所有行列表。
    """
    header_lines = []
    with open(fp, 'r') as f:
        for line in f:
            header_lines.append(line)
            if line.strip().startswith('Wavelength'):
                break
    return header_lines

# --- 3. 读取所有文件并求平均 ---
print("正在读取并计算平均光谱...")
all_spec = []
# 用于保存原始文件名，以便稍后提取Header模板
all_filenames = [] 

for i in range(0, n_files):
    fname = f"spectrum{i:05d}.asd.ref.txt"
    fp = os.path.join(data_dir, fname)
    all_filenames.append(fp) # 保存路径用于后续读取header
    refl = read_asd_file(fp)
    all_spec.append(refl)

all_spec = np.vstack(all_spec)  # shape (n_files, 2151)

# 每group_size个文件做一次平均
# avg_spec shape: (20, 2151)
avg_spec = np.array([all_spec[i:i+group_size].mean(axis=0) for i in range(0, n_files, group_size)])

print(f"计算完成，共生成 {avg_spec.shape[0]} 条平均光谱。")

# --- 4. 保存为 GP901.mn.txt 格式 ---
print("正在保存文件...")

for j in range(avg_spec.shape[0]):
    # 1. 确定新文件名
    current_num = start_spec_num + j
    new_filename_base = f"GP{current_num}.mn"
    new_filename_txt = f"{new_filename_base}.txt"
    save_path = os.path.join(output_dir, new_filename_txt)
    
    # 2. 获取Header模板
    # 逻辑：每一组平均数据，使用该组“第一个原始文件”的Header作为模板
    # 这样可以保留该组数据真实的采集时间、积分时间等元数据
    original_idx = j * group_size
    template_fp = all_filenames[original_idx]
    header_lines = get_header_template(template_fp)
    
    # 3. 写入新文件
    with open(save_path, 'w') as f:
        # --- 写入 Header ---
        for line in header_lines:
            # 关键步骤：修改 Header 中的列名，使其匹配新文件名
            # 原始可能是: Wavelength	spectrum00000.asd.ref
            # 修改为:     Wavelength	GP901.mn
            if line.strip().startswith('Wavelength'):
                # 重新构建列名行，使用制表符分隔
                new_line = f"Wavelength\t{new_filename_base}\n"
                f.write(new_line)
            # 可选：如果你想修改第一行显示的原始文件名，也可以在这里做 replace
            elif "Text conversion of header file" in line:
                # 简单替换文件名部分
                f.write(line.replace(os.path.basename(template_fp).replace('.txt',''), new_filename_base))
            else:
                f.write(line)
        
        # --- 写入 数据 (Wavelength 和 Reflectance) ---
        # 参照 GP901.mn.txt 的格式：整数波长 + Tab + 浮点数反射率
        current_data = avg_spec[j]
        for idx, val in enumerate(current_data):
            wl = wl_full[idx]
            # 使用制表符 \t 分隔，保留足够的小数位 (例如 .15f)
            f.write(f"{wl}\t {val:.15f} \n")

print(f"所有文件已保存至: {output_dir}")

# --- 5. 绘图部分 (保持不变) ---
plt.figure(figsize=(12, 6))
for j in range(avg_spec.shape[0]):
    plt.plot(wl_full, avg_spec[j], linewidth=1.5, label=f'Avg {j+1:02d}')
plt.xlim(350, 2500)
plt.ylim(0, 1)
plt.xlabel('Wavelength (nm)')
plt.ylabel('Reflectance')
plt.title('Average Spectra Saved in GP Format')
# 仅显示前20个图例避免拥挤
if avg_spec.shape[0] > 20:
    plt.legend(ncol=2, fontsize='small', frameon=False, max_num_streams=20)
else:
    plt.legend(ncol=2, fontsize='small', frameon=False)
plt.grid(False)
plt.tight_layout()
plt.show()