---
id: RR-004
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Lộ thông tin khách hàng
- ID: `RR-004`
- **category**: Rui ro cong nghe thong tin
- **description**: Quyền truy cập dữ liệu không được kiểm soát phù hợp
- **cause**: Cấp quyền vượt nhu cầu công việc
- **event**: Dữ liệu khách hàng bị truy cập hoặc chia sẻ trái phép
- **impact**: Vi phạm bảo mật và tổn hại uy tín
- **inherent_level**: Cao
- **residual_level**: Trung binh
- **owner_unit_id**: DV-IT

## Quan hệ
- **MITIGATES**: [[controls/Rà_soát_quyền_truy_cập_định_kỳ|Rà soát quyền truy cập định kỳ]]
  - evidence: Dữ liệu mô phỏng: rà soát quyền hạn giảm lộ dữ liệu
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Tài_khoản_có_quyền_truy_cập_dữ_liệu_vượt_phạm_vi_công_việc|Tài khoản có quyền truy cập dữ liệu vượt phạm vi công việc]]
  - evidence: Dữ liệu mô phỏng: sự kiện quyền truy cập quá mức
  - verification_status: VERIFIED
