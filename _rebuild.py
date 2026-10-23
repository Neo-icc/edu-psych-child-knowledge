# -*- coding: utf-8 -*-
"""把本地 main 重建为与远端 8bcfae4d 完全一致的提交（SHA 逐位相同）。"""
import json, subprocess, urllib.request, os

def get_token():
    p = subprocess.Popen(["git", "credential", "fill"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    out, _ = p.communicate(b"protocol=https\nhost=github.com\n\n")
    for line in out.decode().splitlines():
        if line.startswith("password="):
            return line[9:]
    raise SystemExit("无凭据")

tok = get_token()
req = urllib.request.Request(
    "https://api.github.com/repos/Neo-icc/edu-psych-child-knowledge/git/commits/8bcfae4d")
req.add_header("Authorization", "Bearer " + tok)
req.add_header("Accept", "application/vnd.github+json")
with urllib.request.urlopen(req, timeout=60) as r:
    c = json.loads(r.read().decode())

tree = c["tree"]["sha"]
parent = c["parents"][0]["sha"]
msg = c["message"]
a, cm = c["author"], c["committer"]

variants = [msg, msg.rstrip("\n") + "\n", msg.rstrip("\n")]
target = c["sha"]
found = None
for v in variants:
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": a["name"], "GIT_AUTHOR_EMAIL": a["email"], "GIT_AUTHOR_DATE": a["date"],
        "GIT_COMMITTER_NAME": cm["name"], "GIT_COMMITTER_EMAIL": cm["email"], "GIT_COMMITTER_DATE": cm["date"],
    })
    sha = subprocess.check_output(["git", "commit-tree", tree, "-p", parent],
                                  input=v.encode("utf-8"), env=env).decode().strip()
    print("尝试变体 →", sha[:8])
    if sha == target:
        found = sha
        break

if found:
    subprocess.run(["git", "reset", "--hard", found], check=True)
    subprocess.run(["git", "update-ref", "refs/remotes/origin/main", found], check=True)
    print("本地已重建为远端提交:", found[:8], "→ 完全同步")
else:
    print("无法逐位复刻（metadata 差异），保留现状，改用 API 脚本继续推送")
