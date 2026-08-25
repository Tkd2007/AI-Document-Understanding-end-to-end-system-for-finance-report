"""
Công cụ gán nhãn tập gold — máy chủ cục bộ, chạy trên máy người gán nhãn.

Gói này CỐ Ý không import bất cứ thứ gì thuộc đường trích xuất: không
`router`, không `extract_vlm`, không `extract_baseline`, không đọc
`data/output/`. Đó là Luật 1 của `ANNOTATION-GUIDELINE.md` được cưỡng chế
bằng cấu trúc chứ không bằng lời nhắc, và có test chặn ở
`tests/test_gan_nhan_mu_voi_pipeline.py`.
"""
