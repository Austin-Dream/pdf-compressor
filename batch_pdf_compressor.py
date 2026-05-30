import streamlit as st
import fitz  # PyMuPDF
import tempfile
import os
import io
import zipfile
from PIL import Image
from pathlib import Path

st.set_page_config(page_title="批量 PDF 强压缩工具", page_icon="🗜️")
st.title("🗜️ 批量 PDF 强压缩工具")
st.markdown("选择多个 PDF 文件，批量压缩后打包下载。")

# 压缩强度配置
compression_levels = {
    "低 (轻度压缩，保留较好质量)": {"dpi": 150, "quality": 85, "colorspace": "rgb"},
    "中 (推荐，体积缩小 60-80%)": {"dpi": 100, "quality": 70, "colorspace": "rgb"},
    "高 (最大压缩，适合文字/扫描件)": {"dpi": 72, "quality": 50, "colorspace": "gray"},
}

uploaded_files = st.file_uploader(
    "选择 PDF 文件（可多选）", 
    type=["pdf"], 
    accept_multiple_files=True,
    label_visibility="visible"
)

if uploaded_files:
    level_name = st.selectbox("压缩强度", list(compression_levels.keys()))
    level = compression_levels[level_name]
    
    if st.button("🚀 开始批量压缩", type="primary"):
        results = []  # 存储 (原文件名, 压缩后字节, 原大小, 新大小)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"正在压缩: {uploaded_file.name} ({idx+1}/{len(uploaded_files)})")
            file_bytes = uploaded_file.getvalue()
            orig_size = len(file_bytes) / (1024 * 1024)
            
            # 保存临时输入文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
                tmp_in.write(file_bytes)
                input_pdf = tmp_in.name
            
            output_pdf = input_pdf.replace(".pdf", "_compressed.pdf")
            
            try:
                # 打开原 PDF
                doc = fitz.open(input_pdf)
                new_doc = fitz.open()
                
                total_pages = len(doc)
                for page_num in range(total_pages):
                    page = doc[page_num]
                    zoom = level["dpi"] / 72
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, colorspace=level["colorspace"])
                    
                    # 转为 JPEG 字节
                    img_data = pix.tobytes("jpeg", level["quality"])
                    img = Image.open(io.BytesIO(img_data))
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format="JPEG", quality=level["quality"])
                    img_bytes = img_byte_arr.getvalue()
                    
                    # 创建新页面并插入图像
                    new_page = new_doc.new_page(width=pix.width, height=pix.height)
                    new_page.insert_image(fitz.Rect(0, 0, pix.width, pix.height), stream=img_bytes)
                
                doc.close()
                new_doc.save(output_pdf, garbage=4, deflate=True, clean=True)
                new_doc.close()
                
                # 读取压缩后内容
                with open(output_pdf, "rb") as f:
                    compressed_bytes = f.read()
                new_size = len(compressed_bytes) / (1024 * 1024)
                
                results.append({
                    "original_name": uploaded_file.name,
                    "original_size_mb": orig_size,
                    "compressed_bytes": compressed_bytes,
                    "compressed_size_mb": new_size,
                    "ratio": new_size / orig_size if orig_size > 0 else 0
                })
                
            except Exception as e:
                st.error(f"压缩 {uploaded_file.name} 时出错: {str(e)}")
            finally:
                # 清理临时文件
                if os.path.exists(input_pdf):
                    os.unlink(input_pdf)
                if os.path.exists(output_pdf):
                    os.unlink(output_pdf)
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.text("压缩完成！")
        
        # 显示结果表格
        if results:
            st.subheader("压缩结果")
            data = []
            for r in results:
                data.append({
                    "文件名": r["original_name"],
                    "原始大小 (MB)": f"{r['original_size_mb']:.2f}",
                    "压缩后 (MB)": f"{r['compressed_size_mb']:.2f}",
                    "压缩率": f"{r['ratio']:.1%}"
                })
            st.dataframe(data, use_container_width=True)
            
            # 提供单个文件下载（可选的）
            st.subheader("单个文件下载")
            cols = st.columns(min(4, len(results)))
            for i, r in enumerate(results):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    st.download_button(
                        label=f"📄 {r['original_name'][:20]}",
                        data=r["compressed_bytes"],
                        file_name=f"compressed_{r['original_name']}",
                        mime="application/pdf",
                        key=f"single_{i}"
                    )
            
            # 打包所有文件为 ZIP
            if len(results) > 1:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for r in results:
                        zipf.writestr(f"compressed_{r['original_name']}", r["compressed_bytes"])
                zip_buffer.seek(0)
                
                st.download_button(
                    label="📦 打包下载所有压缩文件 (ZIP)",
                    data=zip_buffer,
                    file_name="compressed_pdfs.zip",
                    mime="application/zip"
                )