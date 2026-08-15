---
id: RR-003
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Giải ngân thiếu hồ sơ bảo đảm
- ID: `RR-003`
- **category**: Rui ro tin dung
- **description**: Hồ sơ giải ngân chưa đủ điều kiện
- **cause**: Kiểm tra điều kiện tiên quyết bị bỏ qua
- **event**: Giải ngân khi thiếu chứng từ bắt buộc
- **impact**: Khó thu hồi nợ và vi phạm quy trình
- **inherent_level**: Cao
- **residual_level**: Trung binh
- **owner_unit_id**: DV-CREDIT

## Quan hệ
- **MITIGATES**: [[controls/Checklist_điều_kiện_giải_ngân_bắt_buộc|Checklist điều kiện giải ngân bắt buộc]]
  - evidence: Dữ liệu mô phỏng: checklist ngăn giải ngân thiếu hồ sơ
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Giải_ngân_trước_khi_hoàn_thiện_chứng_từ_bảo_đảm|Giải ngân trước khi hoàn thiện chứng từ bảo đảm]]
  - evidence: Dữ liệu mô phỏng: sự kiện giải ngân thiếu hồ sơ
  - verification_status: VERIFIED
