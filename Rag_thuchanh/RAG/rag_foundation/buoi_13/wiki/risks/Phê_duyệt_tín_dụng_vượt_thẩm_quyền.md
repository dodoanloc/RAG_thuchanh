---
id: RR-002
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Phê duyệt tín dụng vượt thẩm quyền
- ID: `RR-002`
- **category**: Rui ro tin dung
- **description**: Kiểm tra hạn mức phê duyệt không hiệu lực
- **cause**: Phân quyền trên hệ thống không cập nhật
- **event**: Khoản vay được phê duyệt vượt thẩm quyền
- **impact**: Tăng nợ xấu và vi phạm quy định
- **inherent_level**: Cao
- **residual_level**: Trung binh
- **owner_unit_id**: DV-CREDIT

## Quan hệ
- **MITIGATES**: [[controls/Kiểm_tra_hạn_mức_phê_duyệt_trên_hệ_thống|Kiểm tra hạn mức phê duyệt trên hệ thống]]
  - evidence: Dữ liệu mô phỏng: kiểm tra hạn mức ngăn phê duyệt vượt thẩm quyền
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Hồ_sơ_tín_dụng_được_phê_duyệt_vượt_hạn_mức_của_người_phê_duyệt|Hồ sơ tín dụng được phê duyệt vượt hạn mức của người phê duyệt]]
  - evidence: Dữ liệu mô phỏng: sự kiện vượt thẩm quyền
  - verification_status: VERIFIED
