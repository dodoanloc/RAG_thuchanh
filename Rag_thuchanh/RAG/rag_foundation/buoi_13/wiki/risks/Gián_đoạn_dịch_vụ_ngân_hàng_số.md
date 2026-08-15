---
id: RR-005
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Gián đoạn dịch vụ ngân hàng số
- ID: `RR-005`
- **category**: Rui ro cong nghe thong tin
- **description**: Hệ thống thanh toán trực tuyến không sẵn sàng
- **cause**: Kế hoạch năng lực và dự phòng chưa đầy đủ
- **event**: Dịch vụ ngân hàng số bị gián đoạn
- **impact**: Mất doanh thu và khiếu nại khách hàng
- **inherent_level**: Cao
- **residual_level**: Trung binh
- **owner_unit_id**: DV-IT

## Quan hệ
- **MITIGATES**: [[controls/Kiểm_thử_khả_năng_chịu_tải_và_chuyển_đổi_dự_phòng|Kiểm thử khả năng chịu tải và chuyển đổi dự phòng]]
  - evidence: Dữ liệu mô phỏng: kiểm thử dự phòng giảm gián đoạn dịch vụ
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Dịch_vụ_ngân_hàng_số_gián_đoạn_trong_giờ_cao_điểm|Dịch vụ ngân hàng số gián đoạn trong giờ cao điểm]]
  - evidence: Dữ liệu mô phỏng: sự kiện gián đoạn dịch vụ
  - verification_status: VERIFIED
