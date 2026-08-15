---
id: RR-010
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Sai lệch số liệu báo cáo quản trị
- ID: `RR-010`
- **category**: Rui ro bao cao
- **description**: Dữ liệu nguồn không được đối chiếu
- **cause**: Thay đổi dữ liệu không có kiểm soát
- **event**: Báo cáo quản trị có số liệu sai
- **impact**: Quyết định quản trị sai lệch
- **inherent_level**: Trung binh
- **residual_level**: Thap
- **owner_unit_id**: DV-FINANCE

## Quan hệ
- **MITIGATES**: [[controls/Đối_chiếu_dữ_liệu_nguồn_trước_khi_phát_hành_báo_cáo|Đối chiếu dữ liệu nguồn trước khi phát hành báo cáo]]
  - evidence: Dữ liệu mô phỏng: đối chiếu nguồn giảm sai lệch báo cáo
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Báo_cáo_quản_trị_sử_dụng_dữ_liệu_nguồn_chưa_đối_chiếu|Báo cáo quản trị sử dụng dữ liệu nguồn chưa đối chiếu]]
  - evidence: Dữ liệu mô phỏng: sự kiện sai lệch báo cáo
  - verification_status: VERIFIED
