## Evidence 05 — Namespace isolation probe
Write: DELX_MEMORY_NAMESPACE=eval-agent-A call memory_set key=eval-ns-probe value={"scope":"written-by-A"} -> created.
Read as B: DELX_MEMORY_NAMESPACE=eval-agent-B call memory_get key=eval-ns-probe -> {"found":false,"namespace":"eval-agent-B"}; memory_list -> count 0.
Read as A: DELX_MEMORY_NAMESPACE=eval-agent-A call memory_get key=eval-ns-probe -> {"found":true,"value":{"scope":"written-by-A"},"namespace":"eval-agent-A"}.
Default scope list (prefix=eval-) shows PHYSICAL key "eval-agent-A::eval-ns-probe" -> namespacing is a key-prefix scheme; default/unscoped clients see all namespaced keys.
PASS with caveat: namespace isolation works per-client when env var honored; not enforced at storage layer.
