#!/usr/bin/env python3

import json
import os
import signal
import subprocess
import sys
import time
import uuid
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
CONVERT_SCRIPT = os.environ.get("CONVERT_SCRIPT", "/tmp/blender/convert.py")
TIMEOUT = int(os.environ.get("CONVERT_TIMEOUT", "600"))

BLENDER_QUEUE = os.environ.get("BLENDER_QUEUE", "laravel-database-model:blender")
SAVER_QUEUE = os.environ.get("SAVER_QUEUE", "laravel-database-model:saver")
STATUS_PREFIX = os.environ.get("STATUS_PREFIX", "laravel-database-model:status:")
MODEL_OBJ_DIR_PREFIX = os.environ.get("MODEL_OBJ_DIR_PREFIX", "/tmp/storage/app/private/model/")
MODEL_GLB_DIR_PREFIX = os.environ.get("MODEL_GLB_DIR_PREFIX", "/tmp/storage/app/public/model/")

_stop = False

def _handle_signal(signum, frame):
    global _stop
    _stop = True

def dispatch_save_done(r, id, file_name):
    pipe = r.pipeline(transaction=True)

    pipe.hset(STATUS_PREFIX + id, mapping={
        "stage": "saver",
        "status": "queued"
    })

    pipe.lpush(SAVER_QUEUE, json.dumps({
        "id": id,
        "fileName": file_name
    }, ensure_ascii=False))

    pipe.execute()

def run_blender(src, dst):
    return subprocess.run(
        ["blender", "-b", "--python", CONVERT_SCRIPT, "--", src, dst],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )

def main():
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    print(f"worker started: redis={REDIS_URL} queue={BLENDER_QUEUE} saver_queue={SAVER_QUEUE}", flush=True)

    while not _stop:
        try:
            item = r.brpop(BLENDER_QUEUE, timeout=5)
        except redis.RedisError as e:
            print(f"redis error: {e}; retry in 2s", flush=True)
            time.sleep(2)
            continue

        if item is None:
            continue

        _queue, payload = item

        data = json.loads(payload)
        id = data['id']
        model_path = MODEL_OBJ_DIR_PREFIX + id + '/' + data['fileName']
        print(f"Found model: {model_path}", flush=True)

        if not os.path.exists(model_path):
#             report(r, job_id, "error", error=f"input not found: {src}")
            print(f"job {id}: input not found: {model_path}", flush=True)
            continue

        fileName = os.path.splitext(os.path.basename(data['fileName']))[0]
        dst = MODEL_GLB_DIR_PREFIX + id + "/" + fileName + ".glb"
        print(dst)

        try:
            r.hset(STATUS_PREFIX + id, mapping={"stage": "blender", "status": "processing"})

            proc = run_blender(model_path, dst)
        except subprocess.TimeoutExpired:
#             report(r, job_id, "error", error=f"blender timed out after {TIMEOUT}s")
#             print(f"job {job_id}: timeout", flush=True)
            continue
        except FileNotFoundError as e:
#             report(r, job_id, "error", error=f"blender not found: {e}")
#             print(f"job {job_id}: blender not found", flush=True)
            continue

        if proc.returncode != 0 or not os.path.exists(dst):
            log = ((proc.stdout or "") + "\n" + (proc.stderr or ""))[-4000:]
            err = f"conversion failed (rc={proc.returncode})"
#             report(r, job_id, "error", error=err, log=log)
#             print(f"job {job_id}: {err}\n{log}", flush=True)
            continue

        dispatch_save_done(r, id, fileName)

        size = os.path.getsize(dst)
        print(f"Done - ID: {id}: done -> {dst} ({size} bytes)", flush=True)

    print("worker stopped", flush=True)


if __name__ == "__main__":
    main()
