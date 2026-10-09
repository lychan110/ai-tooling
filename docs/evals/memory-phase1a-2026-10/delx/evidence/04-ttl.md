## Evidence 04 — TTL probe
Command: delx-memory call memory_set --json '{"key":"eval-ttl-probe","value":{"note":"short-lived"},"ttl_seconds":2,"explicit_user_intent":true}'
-> {"action":"created","created_at":1791515569877,"ttl_expires_at":1791515571877}  (delta = 2000 ms)
Immediate get (NOW_MS=1791515570119, +242 ms after set): found:true, value returned, ttl_expires_at present.
After sleep 4: get -> {"found":false,"value":null}; memory_list prefix=eval-ttl -> count 0 (row swept).
PASS: entry retrievable before expiry with ttl_expires_at flag; lazy-deleted after expiry.
