import streamlit as st
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/'scripts'))
from internal_lookup import lookup
from compliance_gap import run as gap_run
from audit_logger import read_events
st.set_page_config(page_title='Secure RAG Buổi 17',layout='wide')
st.warning('Demo đào tạo — kết quả AI cần kiểm toán viên xác minh.')
st.title('SECURE RAG & COMPLIANCE — BUỔI 17')
role=st.sidebar.selectbox('User Role',['Admin','HR','Risk_Manager','Staff','Guest']); user=st.sidebar.text_input('User ID','demo01')
st.caption('SESSION / ACCESS SCOPE')
info1, info2, info3 = st.columns(3)
info1.metric('User ID', user)
info2.metric('User Role', role)
info3.metric('RBAC', 'PRE-FILTER')
t1,t2,t3=st.tabs(['TRA CỨU QUY ĐỊNH','GAP CHECKER','AUDIT'])
with t1:
 q=st.text_input('Question')
 if st.button('RUN LOOKUP'):
  r=lookup(q,role,5); st.write(r['answer']); st.write('Request ID:',r['request_id']); st.dataframe(r['citations'])
with t2:
 st.info('Gap analysis bị chặn an toàn nếu thiếu INTERNAL_POLICY thật.')
 if st.button('RUN GAP CHECK'): st.dataframe(gap_run())
with t3: st.dataframe(read_events())
