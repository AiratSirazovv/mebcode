#!/usr/bin/env python3
"""Redis-воркер: BRPOP из очереди -> запускает blender -> пишет результат обратно в Redis."""
import json
import os
import signal
import subprocess
import sys
import time
import uuid

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
QUEUE = os.environ.get("CONVERT_QUEUE", "convert:jobs")
RESULT_QUEUE = os.environ.get("CONVERT_RESULT_QUEUE", "convert:results")
STATUS_PREFIX = os.environ.get("CONVERT_STATUS_PREFIX", "convert:job:")
DEFAULT_INPUT = os.environ.get("CONVERT_DEFAULT_INPUT", "/tmp/cabinet.obj")
DEFAULT_OUTPUT = os.environ.get("CONVERT_DEFAULT_OUTPUT", "/tmp/cabinet.glb")
CONVERT_SCRIPT = os.environ.get("CONVERT_SCRIPT", "/tmp/convert.py")
TIMEOUT = int(os.environ.get("CONVERT_TIMEOUT", "600"))

_stop = False


def _handle_signal(signum, frame):
    global _stop
    _stop = True


def parse_job(payload):
    """Возвращает (job_id, input, output). Поддерживает JSON-объект, строку-путь и пустую задачу."""
    payload = (payload or "").strip()
    if not payload:
        return f"auto-{uuid.uuid4().hex[:8]}", DEFAULT_INPUT, DEFAULT_OUTPUT

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        # голый путь в очереди = путь на вход, дефолтный выход
        return f"auto-{uuid.uuid4().hex[:8]}", payload, DEFAULT_OUTPUT

    if isinstance(data, str):
        return f"auto-{uuid.uuid4().hex[:8]}", data, DEFAULT_OUTPUT

    if isinstance(data, dict):
        job_id = data.get("id") or f"auto-{uuid.uuid4().hex[:8]}"
        src = data.get("input") or data.get("src") or DEFAULT_INPUT
        dst = data.get("output") or data.get("dst") or DEFAULT_OUTPUT
        return job_id, src, dst

    return f"auto-{uuid.uuid4().hex[:8]}", DEFAULT_INPUT, DEFAULT_OUTPUT


def report(r, job_id, status, *, output=None, error=None, log=None):
    body = {"id": job_id, "status": status, "updated_at": time.time()}
    if output:
        body["output"] = output
    if error:
        body["error"] = error
    if log:
        body["log"] = log

    # 1) «состояние задания» в хэше — удобно опрашивать по id
    mapping = {"status": status, "updated_at": str(body["updated_at"]), "payload": json.dumps(body)}
    if error:
        mapping["error"] = error
    if output:
        mapping["output"] = output
    try:
        r.hset(STATUS_PREFIX + job_id, mapping=mapping)
        # 2) уведомление в result-очередь — удобно BLPOP-ить
        r.lpush(RESULT_QUEUE, json.dumps(body))
    except redis.RedisError as e:
        print(f"redis report failed for {job_id}: {e}", flush=True)


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
    print(f"worker started: redis={REDIS_URL} queue={QUEUE} results={RESULT_QUEUE}", flush=True)

    while not _stop:
        try:
            item = r.brpop(QUEUE, timeout=5)
        except redis.RedisError as e:
            print(f"redis error: {e}; retry in 2s", flush=True)
            time.sleep(2)
            continue

        if item is None:
            continue

        _queue, payload = item
        job_id, src, dst = parse_job(payload)
        print(f"job {job_id}: {src} -> {dst}", flush=True)

        if not os.path.exists(src):
            report(r, job_id, "error", error=f"input not found: {src}")
            print(f"job {job_id}: input not found: {src}", flush=True)
            continue

        report(r, job_id, "running")

        try:
            proc = run_blender(src, dst)
        except subprocess.TimeoutExpired:
            report(r, job_id, "error", error=f"blender timed out after {TIMEOUT}s")
            print(f"job {job_id}: timeout", flush=True)
            continue
        except FileNotFoundError as e:
            report(r, job_id, "error", error=f"blender not found: {e}")
            print(f"job {job_id}: blender not found", flush=True)
            continue

        if proc.returncode != 0 or not os.path.exists(dst):
            log = ((proc.stdout or "") + "\n" + (proc.stderr or ""))[-4000:]
            err = f"conversion failed (rc={proc.returncode})"
            report(r, job_id, "error", error=err, log=log)
            print(f"job {job_id}: {err}\n{log}", flush=True)
            continue

        size = os.path.getsize(dst)
        report(r, job_id, "done", output=dst)
        print(f"job {job_id}: done -> {dst} ({size} bytes)", flush=True)

    print("worker stopped", flush=True)


if __name__ == "__main__":
    main()