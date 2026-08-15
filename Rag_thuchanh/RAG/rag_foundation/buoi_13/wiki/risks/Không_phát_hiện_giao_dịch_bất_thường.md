---
id: RR-009
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Không phát hiện giao dịch bất thường
- ID: `RR-009`
- **category**: Rui ro gian lan
- **description**: Luật phát hiện gian lận không được cập nhật
- **cause**: Ngưỡng cảnh báo không phù hợp
- **event**: Giao dịch nghi ngờ không bị chặn kịp thời
- **impact**: Tổn thất tài chính và uy tín
- **inherent_level**: Cao
- **residual_level**: Trung binh
- **owner_unit_id**: DV-OPS

## Quan hệ
- **MITIGATES**: [[controls/Hiệu_chỉnh_luật_phát_hiện_giao_dịch_gian_lận|Hiệu chỉnh luật phát hiện giao dịch gian lận]]
  - evidence: Dữ liệu mô phỏng: hiệu chỉnh luật giảm bỏ sót giao dịch bất thường
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Giao_dịch_bất_thường_chỉ_bị_phát_hiện_sau_khi_khách_hàng_khiếu_nại|Giao dịch bất thường chỉ bị phát hiện sau khi khách hàng khiếu nại]]
  - evidence: Dữ liệu mô phỏng: sự kiện không phát hiện bất thường
  - verification_status: VERIFIED
