## Evidence 03 — Secret probe (fake AWS key) REJECTED
Probe A: key=eval-aws-probe, value={"credentials":"AKIAIOSFODNN7EXAMPLE"} -> blocked on nested field name 'credentials'. EXIT_CODE=1.
Probe B: key=eval-aws-probe-2, value="AKIAIOSFODNN7EXAMPLE" (plain string) -> error: "Refusing to store: value at '<value>' matches AWS access key pattern. delx-memory will not store secrets..." EXIT_CODE=1.
Probe C: key=eval-secret-probe (name contains "secret") -> blocked by key-name pattern.
Probe D: key=eval-user-token -> blocked by key-name pattern.
Post-check: memory_get eval-aws-probe -> found:false; memory_list prefix=eval-aws -> count 0; memory_get eval-secret-probe / eval-user-token -> found:false.
PASS: credential-shaped values and key names visibly refused (exit 1, no rows persisted).
