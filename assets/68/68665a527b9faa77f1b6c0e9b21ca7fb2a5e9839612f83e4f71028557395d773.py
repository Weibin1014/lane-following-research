"""Create a bounded bench test from the steering-only test; does not run hardware."""
import ast
from pathlib import Path
s = Path('realtime_steering_only.py').read_text()
def change(old, new):
    global s
    if s.count(old) != 1:
        raise RuntimeError('Unexpected source: ' + old[:70])
    s = s.replace(old, new, 1)
change('Path("steering_vision_results")', 'Path("loss_stop_results")')
change('pwm.set_pwm(1, 0, 350)\n    camera =', 'pwm.set_pwm(0, 0, 370)\n    pwm.set_pwm(1, 0, 350)\n    camera =')
change('    begin = time.perf_counter()', '''    with open('/dev/tty') as terminal:
        print('已发送370。接通电机电池，等待ESC启动。驱动轮必须离地。', flush=True)
        print('回车后倒数3秒；检测到连续5帧有效目标后，450最多运行2秒。准备遮挡镜头。', flush=True)
        terminal.readline()
    for n in (3, 2, 1):
        print(n, flush=True)
        time.sleep(1)
    motor_start = None
    motor_done = False
    valid_streak = 0
    begin = time.perf_counter()''')
change('            pwm.set_pwm(1, 0, command)', '''            now = time.perf_counter()
            valid_streak = valid_streak + 1 if offset is not None else 0
            if motor_start is None and not motor_done and valid_streak >= 5:
                motor_start = now
                print('电机启动450：现在遮挡镜头，或按Ctrl+C。', flush=True)
            reason = None
            if motor_start is not None and not motor_done:
                if offset is None:
                    reason = 'target_unavailable'
                elif now - motor_start >= 2.0:
                    reason = 'time_limit'
                if reason:
                    motor_done = True
                    print('锁定停车原因: ' + reason, flush=True)
            throttle = 450 if motor_start is not None and not motor_done else 370
            pwm.set_pwm(0, 0, throttle)
            pwm.set_pwm(1, 0, command)''')
change('"offset", "steering_pwm"', '"offset", "steering_pwm", "throttle_pwm"')
change('else offset, command\n', 'else offset, command, throttle\n')
change('    try:\n        if pwm is not None:', '''    try:
        if pwm is not None:
            try:
                pwm.set_pwm(0, 0, 370)
                print('退出：已发送停止370。', flush=True)
            except Exception as exc:
                print('停止写入失败！立即断开电机电池：', exc, flush=True)
        with open('/dev/tty') as terminal:
            print('请先断开电机电池，再按回车完成清理。', flush=True)
            terminal.readline()
    finally:
        cleanup_steering_and_camera(pwm, camera, started)


def unused_cleanup_placeholder():
    try:
        if pwm is not None:''')
# Move the existing cleanup into a function defined before the main try.
start=s.index('def unused_cleanup_placeholder():')
end=s.index('\nprint("处理帧数:"', start)
cleanup=s[start:end].replace('def unused_cleanup_placeholder():', 'def cleanup_steering_and_camera(pwm, camera, started):', 1)
s=s[:start]+s[end:]
marker='try:\n    pwm = PCA9685'
assert s.count(marker)==1
s=s.replace(marker,cleanup+'\n\n'+marker,1)
s=s.replace('开始30秒视觉舵机测试；驱动电机必须断电；Ctrl+C结束。','架空停车测试准备中；尚未启动电机。')
ast.parse(s)
with Path('realtime_loss_stop_test.py').open('x') as f:
    f.write(s)
print('Created realtime_loss_stop_test.py')
