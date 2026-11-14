---
type: verification
status: local-browser-qa
created: 2026-11-14
updated: 2026-11-14
tags: [skilllantern, browser, installation]
---

# Isolated installer browser verification

Run `node website/qa-installer.mjs` from the vault root. It starts a loopback-only
site server and fresh headless Edge profile. Normal checks replace only
`showDirectoryPicker` with `navigator.storage.getDirectory()`, exercising real
browser OPFS directory/file handles. Failure fixtures additionally alter fetch or
one `createWritable` operation; those failures are simulated, not observed OS errors.

No real project directory is selected. Native external folder-picker dialogs,
permission prompts, hosted HTTPS/embedded behavior, and Codex skill activation are
not exercised. File hash verification confirms installed bytes, not agent discovery.

See [results.json](results.json) for the latest run. The pre-fix result and source
snapshot preserve an ownership-write failure which stranded a payload file and empty
ownership JSON; Undo could not recover it. Deployment requires the latest run to pass
the rollback cases as well as normal installation and preservation checks.

Temporary browser profiles contain only test OPFS content. Browser and loopback server
are closed by the script. A process launch outside the restricted shell sandbox was
needed for reliable Edge DevTools operation on this machine.

[[Home]] · [[06_Build/Installation-Pilot/Result]]
