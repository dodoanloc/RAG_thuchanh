# Security Audit Report — Buổi 15

Corpus: 720 chunks

## PASS — Guest cannot read HR
- Roles: ['Guest']
- Target tags: ['Admin', 'HR']
- Target chunks: 113; visible target chunks: 0; all visible chunks: 317

## PASS — Staff cannot read HR
- Roles: ['Staff']
- Target tags: ['Admin', 'HR']
- Target chunks: 113; visible target chunks: 0; all visible chunks: 607

## PASS — Guest cannot read risk
- Roles: ['Guest']
- Target tags: ['Admin', 'Risk_Manager', 'Staff']
- Target chunks: 290; visible target chunks: 0; all visible chunks: 317

## PASS — Staff can read risk
- Roles: ['Staff']
- Target tags: ['Admin', 'Risk_Manager', 'Staff']
- Target chunks: 290; visible target chunks: 290; all visible chunks: 607

## PASS — Guest can read general
- Roles: ['Guest']
- Target tags: ['Admin', 'HR', 'Risk_Manager', 'Staff', 'Guest']
- Target chunks: 317; visible target chunks: 317; all visible chunks: 317

## Kết luận
5/5 test PASS.
Không rò rỉ tag cấp cao trong các test vai trò thấp.
