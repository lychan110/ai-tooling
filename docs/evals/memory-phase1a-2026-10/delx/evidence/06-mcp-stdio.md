## Evidence 06 — Real MCP stdio roundtrip (lite transport, two client+server pairs)
Driver: scripts/mcp-client.mjs (JSON-RPC over stdio: initialize -> notifications/initialized -> tools/list -> tools/call).
Client A (write): node scripts/mcp-client.mjs set eval-mcp-fact '{"fact":"written over MCP stdio by client A"}'
  MCP_CLIENT_PID=1839199 SPAWNED_SERVER_PID=1839207 ; TOOLS_COUNT=15
  tools/call memory_set -> structuredContent {"key":"eval-mcp-fact","action":"created","bytes":45} A_EXIT:0
Client B (read): node scripts/mcp-client.mjs get eval-mcp-fact
  MCP_CLIENT_PID=1839214 SPAWNED_SERVER_PID=1839222 ; TOOLS_COUNT=15
  tools/call memory_get -> structuredContent {"found":true,"value":{"fact":"written over MCP stdio by client A"},...} B_EXIT:0
PASS: two independent MCP client processes, each with its own spawned server process, sharing one SQLite file over the real MCP wire protocol.
