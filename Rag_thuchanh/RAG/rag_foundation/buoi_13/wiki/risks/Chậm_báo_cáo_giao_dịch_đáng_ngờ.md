---
id: RR-007
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Chậm báo cáo giao dịch đáng ngờ
- ID: `RR-007`
- **category**: Rui ro tuan thu
- **description**: Theo dõi cảnh báo AML không kịp thời
- **cause**: Khối lượng cảnh báo vượt năng lực xử lý
- **event**: Báo cáo giao dịch đáng ngờ nộp muộn
- **impact**: Chế tài và rủi ro pháp lý
- **inherent_level**: Cao
- **residual_level**: Trung binh
- **owner_unit_id**: DV-COMPLIANCE

## Quan hệ
- **MITIGATES**: [[controls/Theo_dõi_SLA_xử_lý_cảnh_báo_AML|Theo dõi SLA xử lý cảnh báo AML]]
  - evidence: Dữ liệu mô phỏng: theo dõi SLA giảm nguy cơ báo cáo muộn
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Báo_cáo_giao_dịch_đáng_ngờ_nộp_quá_hạn_nội_bộ|Báo cáo giao dịch đáng ngờ nộp quá hạn nội bộ]]
  - evidence: Dữ liệu mô phỏng: sự kiện báo cáo AML muộn
  - verification_status: VERIFIED
