# MCP: a narrowly scoped interface proposal

**Status: design only. No MCP server has been implemented or published.**

The Model Context Protocol (MCP) provides a way for an assistant to access tools. An initial integration for this tower should expose only:

- `observe_capacity`: return bytes, observation time and method, without personal paths, process details or documents.
- `explain_admission`: evaluate an explicit observation, reserve and declared demand; return the reason and freshness limit, never execution permission.

Start with local stdio transport and strict input validation. This design needs neither credentials nor a public endpoint. The `readOnlyHint`, `destructiveHint` and `openWorldHint` annotations describe scope to a client; they do not replace server-side controls. See the [official explanation of tool annotations](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/).

A server that executes inference needs a separate contract: operator identity, verifiable exclusion, time limits, cancellation of descendant processes, budget, restoration and tests against the actual runtime. A favorable `explain_admission` response must not confer that authority.

Before implementation, pin the supported protocol version and official SDK. Test initialization, invalid schemas, errors, incomplete output and disconnection against the [official specification](https://github.com/modelcontextprotocol/modelcontextprotocol/tree/main/docs/specification). This proposal does not establish compatibility with MCP clients.
