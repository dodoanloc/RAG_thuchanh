CREATE CONSTRAINT rui_ro_id IF NOT EXISTS FOR (n:RuiRo) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT kiem_soat_id IF NOT EXISTS FOR (n:KiemSoat) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT su_kien_id IF NOT EXISTS FOR (n:SuKienRuiRo) REQUIRE n.id IS UNIQUE;
CREATE INDEX rui_ro_category IF NOT EXISTS FOR (n:RuiRo) ON (n.category);

// Load nodes and relations through scripts/load_neo4j.py.
// All relationship metadata preserves source, evidence_quote, confidence, verification_status, data_origin.
