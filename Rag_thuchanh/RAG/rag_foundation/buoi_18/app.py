import streamlit as st
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/'scripts'))
from compliance_checker import check_pairs
from audit_checklist_gen import generate
from audit_logger import read_events
st.set_page_config(page_title='AI Compliance & Audit',layout='wide')
st.warning('Demo sản phẩm AI Kiểm toán - Kết quả gợi ý cần kiểm toán viên xác minh trước khi ban hành.')
st.title('AI Compliance Checker & Audit Checklist')
role=st.sidebar.selectbox('User Role',['Admin','Risk_Manager','KiemToanVien','Staff','Guest']); user=st.sidebar.text_input('User ID','demo01')
st.caption('SESSION / ACCESS SCOPE')
info1, info2, info3 = st.columns(3)
info1.metric('User ID', user)
info2.metric('User Role', role)
info3.metric('RBAC', 'PRE-FILTER')
t1,t2,t3=st.tabs(['UC3 Compliance Checker','UC4 Audit Checklist','Audit Log'])
with t1:
 domain=st.text_input('Domain','An toàn kho quỹ');
 if st.button('Phát hiện xung đột & Mâu thuẫn'):
  st.dataframe(check_pairs(domain,user_role=role),use_container_width=True)
with t2:
 domain2=st.text_input('Checklist Domain','Bảo mật CNTT & AI'); unit=st.text_input('Unit','Khối CNTT')
 if st.button('Tạo bản nháp Checklist'):
  st.dataframe(generate(domain2,unit,role),use_container_width=True)
with t3:
 st.dataframe(read_events(),use_container_width=True)
