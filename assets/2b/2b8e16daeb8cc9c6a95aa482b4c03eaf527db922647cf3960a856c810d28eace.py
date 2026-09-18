import json
import time
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen

def send(mode, throttle):
    data = json.dumps({
        "angle": 0.0, "throttle": throttle,
        "drive_mode": mode, "recording": False
    }).encode()
    req = Request("http://127.0.0.1:8887/drive", data=data,
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=2) as response:
        response.read()

out = Path("phone_timing_cnn_results") / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
out.mkdir(parents=True, exist_ok=False)
result = {
    "method": "CNN steering, fixed throttle",
    "model": "models/mypilot.tflite",
    "mode": "local_angle", "throttle": 0.375,
    "phone_lap_time_s": None,
    "stop_request_acknowledged": False
}
started = None
try:
    send("user", 0.0)
    print("已发送零油门。摆好起点，接通电机电池，等待ESC就绪。")
    if input("准备好后输入 YES：").strip() != "YES":
        raise RuntimeError("取消")
    print("实际起步时开始计时；一圈结束停秒表，再按 Ctrl+C。")
    for n in (3, 2, 1):
        print(n, flush=True)
        time.sleep(1)
    started = time.monotonic()
    send("local_angle", 0.375)
    while time.monotonic() - started < 30:
        time.sleep(0.05)
    result["stop_reason"] = "30s_limit"
except KeyboardInterrupt:
    result["stop_reason"] = "operator_stop"
except Exception as exc:
    result["stop_reason"] = "error"
    result["error"] = repr(exc)
finally:
    if started is not None:
        result["command_interval_s"] = round(time.monotonic() - started, 3)
    try:
        send("user", 0.0)
        result["stop_request_acknowledged"] = True
        print("停车请求已收到响应，请确认停车并断开电机电池。")
    except Exception as exc:
        result["stop_error"] = repr(exc)
        print("停车请求失败，立即断开电机电池！")
    (out / "summary.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, ensure_ascii=False))
    print("结果目录:", out.resolve())
