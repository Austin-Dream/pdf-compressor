"""
PDF 压缩核心模块
使用 PyMuPDF 进行无损压缩（保留所有页面、图像）
"""

import os
import fitz  # PyMuPDF

def compress_pdf(input_path: str, output_path: str = None, garbage: int = 4, deflate: bool = True) -> str:
    """
    压缩 PDF 文件
    
    Args:
        input_path: 输入 PDF 文件路径
        output_path: 输出文件路径（可选，默认在输入文件名后加 _compressed）
        garbage: 垃圾回收级别（1-4，数值越大压缩越强）
        deflate: 是否启用 deflate 压缩流
    
    Returns:
        输出文件路径
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")
    
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"
    
    # 打开原 PDF
    doc = fitz.open(input_path)
    original_size = os.path.getsize(input_path)
    
    # 保存压缩版本
    doc.save(output_path, garbage=garbage, deflate=deflate, clean=True)
    doc.close()
    
    compressed_size = os.path.getsize(output_path)
    ratio = compressed_size / original_size
    
    print(f"原始大小: {original_size / (1024*1024):.2f} MB")
    print(f"压缩后: {compressed_size / (1024*1024):.2f} MB")
    print(f"压缩比: {ratio:.1%}")
    
    return output_path


def get_page_count(input_path: str) -> int:
    """获取 PDF 总页数"""
    doc = fitz.open(input_path)
    count = len(doc)
    doc.close()
    return count


if __name__ == "__main__":
    # 测试用
    import sys
    if len(sys.argv) > 1:
        compress_pdf(sys.argv[1])
    else:
        print("用法: python compress.py <文件路径>")