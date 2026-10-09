## Evidence 02 — Control-fact roundtrip (CLI call surface, two distinct client processes)
Commands (DELX_MEMORY_PATH=<eval>/data/db.sqlite for all):
- Client A: bash scripts/client-a.sh  ->  `delx-memory call memory_set --json '{"key":"eval-control-fact","value":{"fact":"hub org delegates provider selection to credential pools"},"tags":["eval","control"],"explicit_user_intent":true}'`
- Client B: bash scripts/client-b.sh  ->  `delx-memory call memory_get --json '{"key":"eval-control-fact"}'`
Output A: CLIENT_A_PID=1836153 -> {"key":"eval-control-fact","action":"created","created_at":1791515536211,"bytes":67} A_EXIT:0
Output B: CLIENT_B_PID=1836160 -> {"found":true,"key":"eval-control-fact","value":{"fact":"hub org delegates provider selection to credential pools"},"tags":["eval","control"],"ttl_expires_at":null} B_EXIT:0
Output C (third process): memory_list prefix=eval- -> count 1, key eval-control-fact.
DB file after first write: stat mode=600 size=40960.
PASS: fact written by process 1836153, read verbatim by distinct process 1836160 against the same SQLite file.
