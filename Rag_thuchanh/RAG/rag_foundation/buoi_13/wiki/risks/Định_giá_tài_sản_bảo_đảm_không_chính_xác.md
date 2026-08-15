---
id: RR-008
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Định giá tài sản bảo đảm không chính xác
- ID: `RR-008`
- **category**: Rui ro tin dung
- **description**: Dữ liệu định giá không độc lập hoặc hết hạn
- **cause**: Thiếu rà soát lại giá trị tài sản
- **event**: Tài sản bảo đảm được định giá cao hơn thực tế
- **impact**: Tăng tổn thất khi xử lý nợ
- **inherent_level**: Cao
- **residual_level**: Trung binh
- **owner_unit_id**: DV-CREDIT

## Quan hệ
- **MITIGATES**: [[controls/Rà_soát_độc_lập_định_giá_tài_sản_bảo_đảm|Rà soát độc lập định giá tài sản bảo đảm]]
  - evidence: Dữ liệu mô phỏng: rà soát độc lập giảm sai định giá
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Rà_soát_phát_hiện_giá_trị_tài_sản_bảo_đảm_đã_hết_hiệu_lực|Rà soát phát hiện giá trị tài sản bảo đảm đã hết hiệu lực]]
  - evidence: Dữ liệu mô phỏng: sự kiện sai định giá tài sản
  - verification_status: VERIFIED
