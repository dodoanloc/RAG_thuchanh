MATCH (n) RETURN labels(n), count(n);
MATCH ()-[r]->() RETURN type(r), count(r);
MATCH (k:KiemSoat {id:$control_id})-[:MITIGATES]->(r:RuiRo) RETURN k,r;
MATCH (r:RuiRo {id:$risk_id})-[:OBSERVED_AS]->(s:SuKienRuiRo) RETURN r,s;
MATCH p=(k:KiemSoat)-[:MITIGATES]->(r:RuiRo)-[:OBSERVED_AS]->(s:SuKienRuiRo) RETURN p;
MATCH (r:RuiRo) WHERE NOT (r)<-[:MITIGATES]-() RETURN r;
MATCH (a)-[rel]->(b) WHERE rel.verification_status <> 'VERIFIED' RETURN a,rel,b;
// No owner names are inferred: only owner_unit_id and owner_role_id are shown when present.

--

MATCH (r:RuiRo) RETURN r.id, r.name, r.owner_unit_id;
MATCH (k:KiemSoat) RETURN k.id, k.name, k.owner_role_id;
