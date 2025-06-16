import os
import glob
from pathlib import Path

def merge_txt_files_from_folders(folder_paths, output_file):
    """
    合并多个文件夹中的所有txt文件
    
    Args:
        folder_paths: 文件夹路径列表
        output_file: 输出文件路径
    """
    
    all_files = []
    
    # 收集所有文件夹中的txt文件
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            print(f"⚠️ 文件夹不存在: {folder_path}")
            continue
            
        # 查找所有txt文件
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        
        if not txt_files:
            print(f"⚠️ 文件夹中没有找到txt文件: {folder_path}")
            continue
            
        print(f"📁 在 {folder_path} 中找到 {len(txt_files)} 个txt文件")
        
        for txt_file in txt_files:
            all_files.append({
                'path': txt_file,
                'folder': os.path.basename(folder_path),
                'filename': os.path.basename(txt_file)
            })
    
    if not all_files:
        print("❌ 没有找到任何txt文件")
        return
    
    # 按文件夹和文件名排序
    all_files.sort(key=lambda x: (x['folder'], x['filename']))
    
    print(f"\n📝 准备合并 {len(all_files)} 个文件到 {output_file}")
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 合并文件
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # 写入文件头信息
            outfile.write("# 合并的TXT文件\n")
            outfile.write(f"# 总文件数: {len(all_files)}\n")
            outfile.write(f"# 来源文件夹: {', '.join([os.path.basename(fp) for fp in folder_paths])}\n\n")
            
            current_folder = None
            
            for file_info in all_files:
                file_path = file_info['path']
                folder_name = file_info['folder']
                filename = file_info['filename']
                
                # 如果是新的文件夹，添加分隔符
                if current_folder != folder_name:
                    if current_folder is not None:
                        outfile.write("\n" + "="*80 + "\n\n")
                    outfile.write(f"## 文件夹: {folder_name}\n\n")
                    current_folder = folder_name
                
                # 添加文件分隔符
                outfile.write(f"### 文件: {filename}\n\n")
                
                # 读取并写入文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        
                        # 过滤掉文件头信息和空行
                        filtered_lines = []
                        for line in lines:
                            line = line.strip()
                            # 跳过文件头信息和空行
                            if (line and 
                                not line.startswith('# 文件：') and 
                                not line.startswith('# 提取方法：') and 
                                not line.startswith('# 句子数量：')):
                                filtered_lines.append(line)
                        
                        if filtered_lines:
                            for line in filtered_lines:
                                outfile.write(line + "\n")
                    
                    print(f"✅ 已合并: {filename}")
                    
                except Exception as e:
                    print(f"❌ 读取文件失败 {filename}: {e}")
                    outfile.write(f"[错误: 无法读取文件 {filename}]\n\n")
        
        print(f"\n🎉 合并完成! 输出文件: {output_file}")
        
        # 显示统计信息
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"📊 合并后文件行数: {len(lines)}")
            
    except Exception as e:
        print(f"❌ 合并失败: {e}")

def merge_txt_files_simple(folder_paths, output_file):
    """
    简单合并模式：只合并内容，不添加分隔符和标题
    
    Args:
        folder_paths: 文件夹路径列表
        output_file: 输出文件路径
    """
    
    all_files = []
    
    # 收集所有文件夹中的txt文件
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            print(f"⚠️ 文件夹不存在: {folder_path}")
            continue
            
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        
        if txt_files:
            print(f"📁 在 {folder_path} 中找到 {len(txt_files)} 个txt文件")
            all_files.extend(txt_files)
    
    if not all_files:
        print("❌ 没有找到任何txt文件")
        return
    
    # 按文件名排序
    all_files.sort()
    
    print(f"\n📝 准备简单合并 {len(all_files)} 个文件到 {output_file}")
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 合并文件
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for file_path in all_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        
                        # 过滤掉文件头信息和空行
                        for line in lines:
                            line = line.strip()
                            # 跳过文件头信息和空行
                            if (line and 
                                not line.startswith('# 文件：') and 
                                not line.startswith('# 提取方法：') and 
                                not line.startswith('# 句子数量：')):
                                outfile.write(line + "\n")
                    
                    print(f"✅ 已合并: {os.path.basename(file_path)}")
                    
                except Exception as e:
                    print(f"❌ 读取文件失败 {os.path.basename(file_path)}: {e}")
        
        print(f"\n🎉 简单合并完成! 输出文件: {output_file}")
        
    except Exception as e:
        print(f"❌ 合并失败: {e}")

# 配置部分
if __name__ == "__main__":
    # 设置三个文件夹路径
    folder_paths = [
        "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022/The Alphine Journal 2020/manually_extracted_sentences",
        "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022/The Alphine Journal 2021/smart_extracted_sentences",
        "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022/The Alphine Journal 2022/smart_extracted_sentences"
    ]
    
    base_path = "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022"
    
    # 输出文件路径
    output_file = os.path.join(base_path, "merged_alpine_journal_2020-2022.txt")
    output_file_simple = os.path.join(base_path, "merged_alpine_journal_2020-2022_simple.txt")
    
    print("选择合并模式:")
    print("1. 详细模式 (包含文件夹和文件名分隔符)")
    print("2. 简单模式 (只合并内容)")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        merge_txt_files_from_folders(folder_paths, output_file)
    elif choice == "2":
        merge_txt_files_simple(folder_paths, output_file_simple)
    else:
        print("无效选择，使用详细模式")
        merge_txt_files_from_folders(folder_paths, output_file)