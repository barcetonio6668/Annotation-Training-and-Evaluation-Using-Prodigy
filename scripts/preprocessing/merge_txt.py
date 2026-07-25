import os
import glob
from pathlib import Path

def merge_txt_files_from_folders(folder_paths, output_file):
    """
    Merge all txt files from multiple folders
    
    Args:
        folder_paths: List of folder paths
        output_file: Output file path
    """
    
    all_files = []
    
    # Collect txt files from all folders
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            print(f"Folder does not exist: {folder_path}")
            continue
            
        # Find all txt files
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        
        if not txt_files:
            print(f"No txt files found in folder: {folder_path}")
            continue
            
        print(f"Found {len(txt_files)} txt files in {folder_path}")
        
        for txt_file in txt_files:
            all_files.append({
                'path': txt_file,
                'folder': os.path.basename(folder_path),
                'filename': os.path.basename(txt_file)
            })
    
    if not all_files:
        print("No txt files found")
        return
    
    # Sort by folder and filename
    all_files.sort(key=lambda x: (x['folder'], x['filename']))
    
    print(f"\nPreparing to merge {len(all_files)} files to {output_file}")
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Merge files
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Write header information
            outfile.write("# Merged TXT Files\n")
            outfile.write(f"# Total files: {len(all_files)}\n")
            outfile.write(f"# Source folders: {', '.join([os.path.basename(fp) for fp in folder_paths])}\n\n")
            
            current_folder = None
            
            for file_info in all_files:
                file_path = file_info['path']
                folder_name = file_info['folder']
                filename = file_info['filename']
                
                # Add separator for new folder
                if current_folder != folder_name:
                    if current_folder is not None:
                        outfile.write("\n" + "="*80 + "\n\n")
                    outfile.write(f"## Folder: {folder_name}\n\n")
                    current_folder = folder_name
                
                # Add file separator
                outfile.write(f"### File: {filename}\n\n")
                
                # Read and write file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        
                        # Filter out header information and empty lines
                        filtered_lines = []
                        for line in lines:
                            line = line.strip()
                            # Skip header information and empty lines
                            if (line and 
                                not line.startswith('# File:') and 
                                not line.startswith('# Extraction method:') and 
                                not line.startswith('# Sentence count:')):
                                filtered_lines.append(line)
                        
                        if filtered_lines:
                            for line in filtered_lines:
                                outfile.write(line + "\n")
                    
                    print(f"Merged: {filename}")
                    
                except Exception as e:
                    print(f"Failed to read file {filename}: {e}")
                    outfile.write(f"[Error: Unable to read file {filename}]\n\n")
        
        print(f"\nMerge complete! Output file: {output_file}")
        
        # Display statistics
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Merged file line count: {len(lines)}")
            
    except Exception as e:
        print(f"Merge failed: {e}")

def merge_txt_files_simple(folder_paths, output_file):
    """
    Simple merge mode: only merge content, no separators or headers
    
    Args:
        folder_paths: List of folder paths
        output_file: Output file path
    """
    
    all_files = []
    
    # Collect txt files from all folders
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            print(f"Folder does not exist: {folder_path}")
            continue
            
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        
        if txt_files:
            print(f"Found {len(txt_files)} txt files in {folder_path}")
            all_files.extend(txt_files)
    
    if not all_files:
        print("No txt files found")
        return
    
    # Sort by filename
    all_files.sort()
    
    print(f"\nPreparing to simply merge {len(all_files)} files to {output_file}")
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Merge files
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for file_path in all_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        
                        # Filter out header information and empty lines
                        for line in lines:
                            line = line.strip()
                            # Skip header information and empty lines
                            if (line and 
                                not line.startswith('# File:') and 
                                not line.startswith('# Extraction method:') and 
                                not line.startswith('# Sentence count:')):
                                outfile.write(line + "\n")
                    
                    print(f"Merged: {os.path.basename(file_path)}")
                    
                except Exception as e:
                    print(f"Failed to read file {os.path.basename(file_path)}: {e}")
        
        print(f"\nSimple merge complete! Output file: {output_file}")
        
    except Exception as e:
        print(f"Merge failed: {e}")

# Configuration section
if __name__ == "__main__":
    # Set three folder paths
    folder_paths = [
        "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022/The Alphine Journal 2020/manually_extracted_sentences",
        "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022/The Alphine Journal 2021/smart_extracted_sentences",
        "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022/The Alphine Journal 2022/smart_extracted_sentences"
    ]
    
    base_path = "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022"
    
    # Output file paths
    output_file = os.path.join(base_path, "merged_alpine_journal_2020-2022.txt")
    output_file_simple = os.path.join(base_path, "merged_alpine_journal_2020-2022_simple.txt")
    
    print("Choose merge mode:")
    print("1. Detailed mode (includes folder and file separators)")
    print("2. Simple mode (merge content only)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        merge_txt_files_from_folders(folder_paths, output_file)
    elif choice == "2":
        merge_txt_files_simple(folder_paths, output_file_simple)
    else:
        print("Invalid choice, using detailed mode")
        merge_txt_files_from_folders(folder_paths, output_file)