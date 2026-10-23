# -*- coding: utf-8 -*-
import json, subprocess, urllib.request

def get_token():
    p = subprocess.Popen(["git", "credential", "fill"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    out, _ = p.communicate(b"protocol=https\nhost=github.com\n\n")
    for line in out.decode().splitlines():
        if line.startswith("password="):
            return line[9:]
    raise SystemExit("credential 取不到 password")

tok = get_token()
local_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
print("本地 HEAD:", local_sha[:8])

req = urllib.request.Request(
    "https://api.github.com/repos/Neo-icc/edu-psych-child-knowledge/git/refs/heads/main",
    method="PATCH")
req.add_header("Authorization", "Bearer " + tok)
req.add_header("Accept", "application/vnd.github+json")
req.add_header("Content-Type", "application/json")
with urllib.request.urlopen(req, json.dumps({"sha": local_sha, "force": True}).encode(), timeout=60) as r:
    d = json.loads(r.read().decode())
print("远端 main 已对齐本地:", d["object"]["sha"][:8], "(force)")

subprocess.run(["git", "update-ref", "refs/remotes/origin/main", local_sha], check=True)
print("本地 origin/main 已同步")
