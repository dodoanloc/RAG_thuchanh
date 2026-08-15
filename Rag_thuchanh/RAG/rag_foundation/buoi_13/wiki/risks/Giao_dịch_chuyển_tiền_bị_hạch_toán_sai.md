---
id: RR-001
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---
# Giao dịch chuyển tiền bị hạch toán sai
- ID: `RR-001`
- **category**: Rui ro van hanh
- **description**: Đối soát giao dịch cuối ngày không đầy đủ
- **cause**: Thiếu đối chiếu giữa hệ thống thanh toán và sổ cái
- **event**: Giao dịch được ghi nhận sai trạng thái
- **impact**: Tổn thất tài chính và khiếu nại khách hàng
- **inherent_level**: Cao
- **residual_level**: Trung binh
- **owner_unit_id**: DV-OPS

## Quan hệ
- **MITIGATES**: [[controls/Đối_soát_tự_động_giao_dịch_và_sổ_cái|Đối soát tự động giao dịch và sổ cái]]
  - evidence: Dữ liệu mô phỏng: đối soát tự động giảm nguy cơ hạch toán sai
  - verification_status: VERIFIED
- **OBSERVED_AS**: [[events/Sai_lệch_trạng_thái_giao_dịch_được_phát_hiện_khi_đối_soát_cuối_ngày|Sai lệch trạng thái giao dịch được phát hiện khi đối soát cuối ngày]]
  - evidence: Dữ liệu mô phỏng: sự kiện đối soát giao dịch
  - verification_status: VERIFIED
