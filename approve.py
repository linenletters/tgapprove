import os, time, requests

T = os.environ["TG_JOIN_BOT_TOKEN"]
API = f"https://api.telegram.org/bot{T}/"
deadline = time.time() + int(os.environ.get("RUN_SECONDS", "285"))


def call(method, **params):
    return requests.post(API + method, json=params, timeout=45).json()


offset, approved, failed, errors = None, 0, 0, 0
while time.time() < deadline:
    wait = max(1, min(20, int(deadline - time.time())))
    d = call("getUpdates", offset=offset, timeout=wait, allowed_updates=["chat_join_request"])
    if not d.get("ok"):
        errors += 1
        print("getUpdates error:", d.get("error_code"), d.get("description"))
        if errors > 5:
            break
        time.sleep(3)
        continue
    for u in d["result"]:
        offset = u["update_id"] + 1
        r = u.get("chat_join_request")
        if not r:
            continue
        a = call("approveChatJoinRequest", chat_id=r["chat"]["id"], user_id=r["from"]["id"])
        if a.get("ok"):
            approved += 1
        else:
            failed += 1
            print("approve failed:", a.get("description"))

if offset:
    call("getUpdates", offset=offset, timeout=0, allowed_updates=["chat_join_request"])
print(f"approved={approved} failed={failed}")
