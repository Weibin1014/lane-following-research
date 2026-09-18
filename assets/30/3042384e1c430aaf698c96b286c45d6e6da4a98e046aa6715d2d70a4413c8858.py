"""Default: camera-only dry run. --drive: bounded 8-second straight-to-left-curve test."""
import argparse
import csv
import hashlib
import json
import math
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from bounded_state_8s import Gate, self_test, DURATION_SECONDS

CORE_HASH = '16939c76010f1e2ac90ad14a8df27d24e5619acea2c356536b0e96061a2eecaf'

def confirm(message):
    print(message, flush=True)
    with open('/dev/tty') as terminal:
        if terminal.readline().strip() != 'YES':
            raise RuntimeError('未输入YES，取消')

class Output:
    def __init__(self, pwm):
        self.pwm = pwm
        self.gate = Gate()
        self.lock = threading.Lock()
        self.last = time.monotonic()
        self.closed = threading.Event()
        self.fault = None
        self.worker = threading.Thread(target=self.watch, daemon=True)
        self.worker.start()
    def write(self, throttle, steering):
        if self.pwm is not None:
            self.pwm.set_pwm(0, 0, throttle)
            self.pwm.set_pwm(1, 0, steering)
    def update(self, ready, steering, fresh):
        with self.lock:
            now = time.monotonic()
            if self.gate.started is not None and now-self.last > .25:
                self.gate.stop('watchdog')
            self.last = now
            throttle = self.gate.tick(now, ready, fresh)
            steering = steering if ready and fresh and not self.gate.reason else 365
            self.write(throttle, steering)
            return throttle, steering, self.gate.reason
    def watch(self):
        while not self.closed.wait(.01):
            with self.lock:
                if self.gate.started is None or self.gate.reason:
                    continue
                now = time.monotonic()
                if now-self.gate.started >= DURATION_SECONDS:
                    self.gate.stop('time_limit')
                elif now-self.last > .25:
                    self.gate.stop('watchdog')
                if self.gate.reason:
                    try: self.write(370, 365)
                    except Exception as exc:
                        self.fault = repr(exc)
                        print('停止写入失败，立即断开驱动电机电池！', exc, flush=True)
    def stop(self):
        with self.lock:
            self.gate.stop('exit')
            self.write(370, 365)
        self.closed.set()
        self.worker.join(timeout=1)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--drive', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    core = Path(__file__).with_name('s2_preview_core_thin.py')
    if hashlib.sha256(core.read_bytes()).hexdigest() != CORE_HASH:
        raise RuntimeError('V2核心哈希不同，停止测试')
    import cv2
    from picamera2 import Picamera2
    from s2_preview_core_thin import analyze
    out = Path('transition_thin_8s_results')/datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    out.mkdir(parents=True)
    for name in ('v2_thin_transition_8s.py', 'bounded_state_8s.py', 's2_preview_core_thin.py'):
        shutil.copy2(Path(__file__).with_name(name), out/name)
    (out/'settings.json').write_text(json.dumps(dict(drive=args.drive, duration=DURATION_SECONDS,
        watchdog_seconds=.25, fresh_limit_seconds=.2, throttle=400, stop=370,
        servo_center=365, servo_range=[290,440], initial_ready_frames=5), indent=2))
    camera = pwm = output = None
    rows = []; snapshots = []; error = None
    try:
        if args.drive:
            confirm('直道进入左弯测试：驱动电机电池先断开。小车放在直道中央，车头沿直道方向，前方连续赛道应足够本次8秒行驶，前方清空并准备断电。确认后输入YES：')
            from Adafruit_PCA9685 import PCA9685
            pwm = PCA9685(address=0x40, busnum=1)
            pwm.set_pwm_freq(60)
            pwm.set_pwm(0, 0, 370)
            pwm.set_pwm(1, 0, 365)
        camera = Picamera2()
        camera.configure(camera.create_video_configuration(main={'size':(160,120),'format':'RGB888'},
            controls={'FrameRate':20}, buffer_count=4, queue=False))
        camera.start(); time.sleep(2)
        if args.drive:
            confirm('已发送停止370。接通电机电池并等待ESC就绪。输入YES后倒数3秒，目标连续有效才前进，最多8秒。不要遮挡镜头；准备随时断电：')
            for n in (3,2,1): print(n, flush=True); time.sleep(1)
        else:
            print('DRY RUN：不导入PCA9685、不写PWM。模拟一次8秒控制；请保持电机电池断开。', flush=True)
        output = Output(pwm)
        begin = time.monotonic(); last_sensor = None; last_save = -1
        while time.monotonic()-begin < 10:
            if output.gate.reason: break
            before = time.monotonic()
            request = camera.capture_request()
            try:
                frame = request.make_array('main').copy()
                metadata = request.get_metadata()
            finally: request.release()
            acquired = time.monotonic()
            result = analyze(frame)
            done = time.monotonic()
            sensor = metadata.get('SensorTimestamp')
            age = None if sensor is None else (time.clock_gettime_ns(time.CLOCK_BOOTTIME)-int(sensor))/1e9
            fresh = (age is not None and 0 <= age <= .2 and
                (last_sensor is None or sensor > last_sensor) and done-before <= .2)
            last_sensor = sensor
            command = result.get('steering_pwm')
            ready = (result.get('control_status') == 'ready' and
                     command is not None and math.isfinite(command) and 290 <= command <= 440)
            throttle, steering, reason = output.update(ready, int(command) if ready else 365, fresh)
            elapsed = time.monotonic()-begin
            row = dict(frame=len(rows)+1, elapsed_s=elapsed, sensor_timestamp=sensor,
                frame_age_s=age, fresh=fresh, capture_ms=(acquired-before)*1000,
                vision_ms=(done-acquired)*1000, control_status=result['control_status'],
                near_offset=result['near_offset'], preview_error=result['preview_error'],
                requested_throttle=throttle, requested_steering=steering, pwm_enabled=args.drive, stop_reason=reason)
            rows.append(row)
            # Bounded memory only during control: no image encoding or file writes.
            if elapsed-last_save >= .1 or not ready or reason:
                if len(snapshots) < 220: snapshots.append((len(rows), frame, result))
                last_save = elapsed
            if reason: break
    except BaseException as exc:
        error = f'{type(exc).__name__}: {exc}'
        print(error, flush=True)
    finally:
        try:
            if output is not None: output.stop()
            elif pwm is not None:
                pwm.set_pwm(0,0,370); pwm.set_pwm(1,0,365)
        except Exception as exc:
            print('停止指令写入失败，立即断开电机电池：', exc, flush=True)
            error = str(exc)
        if pwm is not None:
            # Keep neutral signal active; never reinitialize the board here.
            try: confirm('已请求停车。先物理断开驱动电机电池，再输入YES保存记录：')
            except Exception as exc: print(exc, flush=True)
        if camera is not None:
            try: camera.stop()
            finally: camera.close()
        if rows:
            with (out/'frames.csv').open('w', newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        for number, frame, result in snapshots:
            view=cv2.resize(frame,(640,480))
            for y,x in result['points']:
                cv2.circle(view,(round(x*4),round(y*480)),4,(0,0,255),-1)
            for x,y,color in [(result['near_x'],.65,(0,255,0)),(result['far_x'],result['far_y'],(255,0,255))]:
                if x is not None and y is not None:
                    cv2.circle(view,(round(x*4),round(y*480)),8,color,2)
            cv2.putText(view,f"{result['control_status']} PWM={result['steering_pwm']}",(8,22),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0),1)
            for suffix,img in [('raw',frame),('debug',view)]:
                if not cv2.imwrite(str(out/f'{number:06d}_{suffix}.png'),img):
                    raise RuntimeError('保存失败')
        summary=dict(frames=len(rows), stop_reason=output.gate.reason if output else 'setup_failure',
            hardware_pwm=args.drive, error=error, watchdog_error=output.fault if output else None,
            ready_frames=sum(r['control_status']=='ready' for r in rows),
            fresh_frames=sum(r['fresh'] for r in rows))
        (out/'summary.json').write_text(json.dumps(summary,indent=2))
        print(json.dumps(summary,ensure_ascii=False),flush=True)
        print('结果目录:',out.resolve(),flush=True)

if __name__ == '__main__': main()
