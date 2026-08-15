"""Buoi 12 pipeline: validate/clean, rule candidates, optional router NER, normalize, validate."""
from __future__ import annotations
import csv, json, os, re, sys, unicodedata
from pathlib import Path
from collections import Counter
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
KB = BASE / "ner_kb"
load_dotenv(BASE / ".env")
VALID_TYPES = {"CoQuan", "NguoiKy", "DoiTuongApDung", "LinhVuc"}
REL_TYPES = {"THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI", "BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"}
REF_RE = re.compile(r"\b\d{1,4}/\d{4}/[A-ZĐ]{2,12}(?:-[A-ZĐ]{1,8})?\b", re.I)
TRIGGERS = [("Sửa đổi, bổ sung", re.compile(r"sửa đổi\s*,?\s*bổ sung", re.I)), ("thay thế", re.compile(r"thay thế", re.I)), ("bãi bỏ", re.compile(r"bãi bỏ", re.I)), ("Căn cứ", re.compile(r"căn cứ", re.I)), ("Thông tư số", re.compile(r"thông tư\s+số", re.I)), ("Nghị định số", re.compile(r"nghị định\s+số", re.I)), ("Luật số", re.compile(r"luật\s+số", re.I))]

def clean_html(value):
    text = BeautifulSoup(str(value or ""), "html.parser").get_text(" ")
    return re.sub(r"\s+", " ", text).strip()

def norm(v):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(v or "")).strip())

def dump(df, name):
    df.to_csv(KB / name, index=False, encoding="utf-8-sig")

def step1():
    meta = pd.read_csv(KB / "metadata.csv", dtype=str).fillna("")
    content = pd.read_csv(KB / "content.csv", dtype=str).fillna("")
    md, cd = set(meta.id), set(content.id)
    merged = meta.merge(content, on="id", how="outer", indicator=True)
    merged["content_clean"] = merged["content_html"].map(clean_html)
    dump(merged, "cleaned_documents.csv")
    print(f"[PASS] BƯỚC 1 documents={len(merged)} duplicates_meta={meta.id.duplicated().sum()} duplicates_content={content.id.duplicated().sum()} mismatch={len(md ^ cd)}")
    print("missing_metadata", int(meta.isna().sum().sum()), "empty_clean", int((merged.content_clean.str.len()==0).sum()))
    return merged

def evidence(text, match):
    a, b = max(0, match.start()-180), min(len(text), match.end()+220)
    return text[a:b]

def step2(df):
    rows, seen = [], set()
    for _, r in df.iterrows():
        text, source = r.content_clean, norm(r.so_ky_hieu)
        refs = list(REF_RE.finditer(text))
        for m in refs:
            target = m.group(0)
            if target.casefold() == source.casefold(): continue
            context = evidence(text, m)
            trig = next((name for name, rx in TRIGGERS if rx.search(context)), "reference")
            key = (r.id, target.casefold(), trig)
            if key in seen: continue
            seen.add(key); rows.append({"source_id":r.id,"source_so_ky_hieu":source,"target_so_ky_hieu":target,"trigger":trig,"evidence":context})
    out = pd.DataFrame(rows, columns=["source_id","source_so_ky_hieu","target_so_ky_hieu","trigger","evidence"])
    dump(out, "relation_candidates.csv")
    print(f"[PASS] BƯỚC 2 candidates={len(out)} triggers={dict(Counter(out.trigger)) if len(out) else {}}")
    return out

def router_extract(text, title):
    """Call local OpenAI-compatible router. Return parsed JSON or error."""
    import urllib.request
    base = os.getenv("ROUTER_BASE_URL", "http://127.0.0.1:20128/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "openclaw0")
    prompt = ("Trích xuất entity pháp lý từ văn bản Việt Nam. Chỉ trả JSON object với các mảng "
              "co_quan, nguoi_ky, doi_tuong_ap_dung, linh_vuc. Mỗi item gồm entity, confidence, evidence. "
              "Không bịa; evidence phải là trích đoạn nguyên văn.\nTIÊU ĐỀ:\n" + title + "\nNỘI DUNG:\n" + text[:6000])
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps({"model":model,"messages":[{"role":"system","content":"Return valid JSON only."},{"role":"user","content":prompt}],"temperature":0,"max_tokens":1800}).encode(), headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as res: data=json.loads(res.read())
    raw=data["choices"][0]["message"].get("content", "")
    raw=re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
    return json.loads(raw)

def add_entity(rows, doc, entity, typ, method, conf, ev):
    entity, ev = norm(entity), norm(ev)
    if entity and ev and typ in VALID_TYPES:
        rows.append({"source_doc_id":doc,"entity":entity,"entity_type":typ,"source":"content_clean","method":method,"confidence":max(0,min(1,float(conf))),"evidence":ev})

def step3(df):
    rows=[]; errors=[]
    mapping={"co_quan":"CoQuan","nguoi_ky":"NguoiKy","doi_tuong_ap_dung":"DoiTuongApDung","linh_vuc":"LinhVuc"}
    llm_budget = int(os.getenv("LLM_MAX_DOCUMENTS", "1"))
    llm_used = 0
    for _,r in df.iterrows():
        # Trusted raw metadata first; router only enriches and never overwrites raw values.
        for col,typ in [("co_quan_ban_hanh","CoQuan"),("nguoi_ky","NguoiKy"),("thong_tin_ap_dung","DoiTuongApDung"),("linh_vuc","LinhVuc")]:
            if norm(r.get(col)): add_entity(rows,r.id,r[col],typ,"metadata",1.0,"metadata.csv: "+norm(r[col]))
        # Rule extraction covers frequent application phrases without an LLM call.
        for m in re.finditer(r"(?:áp dụng đối với|đối tượng áp dụng là|áp dụng cho)\s+([^.;]{3,180})", r.content_clean, re.I):
            add_entity(rows,r.id,m.group(1),"DoiTuongApDung","rule",0.85,evidence(r.content_clean,m))
        # Call openclaw0 only where raw metadata needs enrichment.
        needs_llm = (not norm(r.nguoi_ky) or not norm(r.linh_vuc) or "chưa phân loại" in norm(r.linh_vuc).casefold())
        if needs_llm and llm_used < llm_budget:
            llm_used += 1
            try:
                result=router_extract(r.content_clean, r.title)
                for key,typ in mapping.items():
                    for item in result.get(key,[]) if isinstance(result,dict) else []:
                        if isinstance(item,dict): add_entity(rows,r.id,item.get("entity"),typ,"openclaw0",item.get("confidence",0),item.get("evidence"))
            except Exception as e: errors.append({"document_id":r.id,"error":type(e).__name__+": "+str(e)[:300]})
    raw=pd.DataFrame(rows, columns=["source_doc_id","entity","entity_type","source","method","confidence","evidence"]); dump(raw,"extracted_entities_raw.csv")
    enriched=df.copy()
    grouped=raw[raw.method!="metadata"].groupby(["source_doc_id","entity_type"])["entity"].apply(lambda x:"; ".join(dict.fromkeys(x))).to_dict() if len(raw) else {}
    for col,typ in [("co_quan_ban_hanh","CoQuan"),("nguoi_ky","NguoiKy"),("thong_tin_ap_dung","DoiTuongApDung"),("linh_vuc","LinhVuc")]:
        enriched[col+"_enriched"]=[norm(r[col]) or grouped.get((r.id,typ),"") for _,r in df.iterrows()]
    dump(enriched,"enriched_metadata.csv")
    pd.DataFrame(errors).to_csv(KB/"extraction_errors.csv",index=False,encoding="utf-8-sig")
    print(f"[PASS] BƯỚC 3 entities={len(raw)} documents={len(df)-len(errors)} failed={len(errors)} openclaw0_calls={llm_used} methods={dict(Counter(raw.method)) if len(raw) else {}}")
    return raw,enriched

def step4(raw):
    aliases={"NHNN":"Ngân hàng Nhà nước Việt Nam","ngân hàng nhà nước":"Ngân hàng Nhà nước Việt Nam"}
    rows=[]; seen=set()
    for _,r in raw.iterrows():
        original=norm(r.entity); canonical=aliases.get(original.casefold(),original)
        key=(r.entity_type,canonical.casefold(),r.source_doc_id)
        if key in seen: continue
        seen.add(key); rows.append({"entity_id":f"{r.entity_type}:{canonical.casefold()}","entity_type":r.entity_type,"canonical_name":canonical,"original_name":original,"source_doc_id":r.source_doc_id,"method":r.method,"confidence":r.confidence,"evidence":r.evidence})
    out=pd.DataFrame(rows,columns=["entity_id","entity_type","canonical_name","original_name","source_doc_id","method","confidence","evidence"]); dump(out,"entities.csv"); print(f"[PASS] BƯỚC 4 before={len(raw)} after={len(out)}"); return out

def step5(df,candidates,entities):
    rows=[]
    for _,r in candidates.iterrows():
        trig=r.trigger
        typ="THAM_CHIEU"
        if trig=="Sửa đổi, bổ sung": typ="SUA_DOI_BO_SUNG"
        elif trig=="thay thế": typ="THAY_THE_BOI"
        elif trig=="bãi bỏ": typ="THAY_THE_BOI"
        rows.append({"source":r.source_so_ky_hieu,"target":r.target_so_ky_hieu,"relationship_type":typ,"method":"rule","confidence":0.8 if typ!="THAM_CHIEU" else 0.7,"evidence":r.evidence})
    for _,e in entities.drop_duplicates(["entity_type","canonical_name"]).iterrows():
        doc=df[df.id==e.source_doc_id].iloc[0]; typ={"CoQuan":"BAN_HANH_BOI","NguoiKy":"KY_BOI","DoiTuongApDung":"AP_DUNG_CHO","LinhVuc":"THUOC_LINH_VUC"}[e.entity_type]
        rows.append({"source":norm(doc.so_ky_hieu),"target":e.canonical_name,"relationship_type":typ,"method":e.method,"confidence":e.confidence,"evidence":e.evidence})
    out=pd.DataFrame(rows).drop_duplicates(subset=["source","target","relationship_type"]); dump(out,"relationships_raw.csv"); print(f"[PASS] BƯỚC 5 relations={len(out)} types={dict(Counter(out.relationship_type))}"); return out

def step6(raw,df,entities):
    docs=set(df.so_ky_hieu.map(norm)); ents=set(zip(entities.entity_type,entities.canonical_name.map(norm))); good=[]; report=[]; seen=set()
    for i,r in raw.iterrows():
        reason=""; rt=r.relationship_type; target=norm(r.target); source=norm(r.source)
        if rt not in REL_TYPES: reason="invalid relationship_type"
        elif not source: reason="missing source"
        elif not target: reason="missing target"
        elif not norm(r.evidence): reason="missing evidence"
        elif rt in {"THAM_CHIEU","SUA_DOI_BO_SUNG","THAY_THE_BOI"} and target not in docs: reason="target document not in closed corpus"
        elif rt in {"BAN_HANH_BOI","KY_BOI","AP_DUNG_CHO","THUOC_LINH_VUC"} and not any(target.casefold()==n.casefold() for _,n in ents): reason="target entity not found"
        key=(source,target,rt)
        if key in seen and not reason: reason="duplicate edge"
        seen.add(key)
        status="PASS" if not reason else "FAIL"; report.append({"row":i,"status":status,"reason":reason,"source":source,"target":target,"relationship_type":rt,"evidence":r.evidence})
        if not reason: good.append(r.to_dict())
    dump(pd.DataFrame(good),"relationships.csv"); dump(pd.DataFrame(report),"validation_report.csv")
    print(f"[PASS] BƯỚC 6 raw={len(raw)} pass={len(good)} fail={len(report)-len(good)}"); return pd.DataFrame(good)

def main():
    df=step1(); c=step2(df); raw,en=step3(df); ents=step4(raw); rr=step5(df,c,ents); step6(rr,df,ents)
    print("PIPELINE_DONE")
if __name__=="__main__": main()
