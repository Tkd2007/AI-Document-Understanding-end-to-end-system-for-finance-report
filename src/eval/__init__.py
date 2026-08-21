"""
Eval harness — mọi con số trong paper đi qua đây.

Bốn phần, tách theo trách nhiệm:

  schema  — định dạng ground truth, kèm metadata nguồn để phát hành dataset
  metrics — các chỉ số ở mục 9 của proposal
  stats   — bootstrap theo cụm, kiểm định ghép cặp, hiệu chỉnh đa so sánh
  split   — chia tập theo TÀI LIỆU, không theo trang

Phần `stats` là phần dễ làm sai nhất và cũng là nhóm lý do gây reject nhiều
hơn cả novelty, nên nó có docstring dài bất thường. Đọc trước khi sửa.

LƯU Ý VỀ TÊN: `eval.metrics` KHÁC `metrics` ở thư mục src. Cái sau là
monitoring của service (thời gian từng giai đoạn, bộ đếm Prometheus); cái
này là chỉ số ĐÁNH GIÁ chất lượng trích xuất. Hai thứ không liên quan gì
tới nhau ngoài cái tên.
"""
