---
id: RR-006
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Gian lận giả mạo yêu cầu chuyển tiền
- ID: `RR-006`
- **category**: Rui ro gian lan
- **description**: Nhận diện và xác thực yêu cầu chưa đủ mạnh
- **cause**: Nhân viên không xác minh kênh liên lạc
- **event**: Yêu cầu chuyển tiền giả mạo được xử lý
- **impact**: Tổn thất tài chính
- **inherent_level**: Cao
- **residual_level**: Trung binh
- **owner_unit_id**: DV-OPS

## Quan hệ
- **MITIGATES**: [[controls/Xác_thực_hai_kênh_với_lệnh_chuyển_tiền_ngoại_lệ|Xác thực hai kênh với lệnh chuyển tiền ngoại lệ]]
  - evidence: Dữ liệu mô phỏng: xác thực hai kênh giảm gian lận chuyển tiền
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Yêu_cầu_chuyển_tiền_giả_mạo_được_xử_lý_trước_khi_bị_thu_hồi|Yêu cầu chuyển tiền giả mạo được xử lý trước khi bị thu hồi]]
  - evidence: Dữ liệu mô phỏng: sự kiện giả mạo chuyển tiền
  - verification_status: VERIFIED
