"""
命令行入口
用法: python cli.py input.pdf [-o output.pdf] [--garbage 4] [--no-deflate]
"""

import argparse
from compress import compress_pdf

def main():
    parser = argparse.ArgumentParser(description="PDF 压缩工具")
    parser.add_argument("input", help="输入的 PDF 文件路径")
    parser.add_argument("-o", "--output", help="输出的 PDF 文件路径（可选）")
    parser.add_argument("--garbage", type=int, default=4, choices=[1,2,3,4],
                        help="垃圾回收级别 1-4，数值越大压缩越强（默认4）")
    parser.add_argument("--no-deflate", action="store_false", dest="deflate",
                        help="禁用 deflate 压缩流")
    args = parser.parse_args()
    
    compress_pdf(args.input, args.output, garbage=args.garbage, deflate=args.deflate)

if __name__ == "__main__":
    main()