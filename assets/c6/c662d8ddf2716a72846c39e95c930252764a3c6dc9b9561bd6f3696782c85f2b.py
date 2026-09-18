"""Generate a steering-only test from the verified realtime visual script."""
import ast
from pathlib import Path

source = Path('realtime_vision_only.py').read_text()
def replace_once(old, new):
    global source
    if source.count(old) != 1:
        raise RuntimeError('Source differs from verified version: ' + old[:80])
    source = source.replace(old, new, 1)

replace_once('from picamera2 import Picamera2', 'from picamera2 import Picamera2\nfrom Adafruit_PCA9685 import PCA9685')
replace_once('Path("realtime_results")', 'Path("steering_vision_results")')
replace_once('camera = Picamera2()', 'pwm = None\ncamera = None')
replace_once('try:\n    config =', '''try:
    pwm = PCA9685(address=0x40, busnum=1)
    pwm.set_pwm_freq(60)
    pwm.set_pwm(1, 0, 350)
    camera = Picamera2()
    config =''')
replace_once('开始30秒纯视觉测试；Ctrl+C可提前结束。', '开始30秒视觉舵机测试；驱动电机必须断电；Ctrl+C结束。')
replace_once('"processing_ms", "track_status", "target_status", "offset"', '"processing_ms", "track_status", "target_status", "offset", "steering_pwm"')
replace_once('            process_ms =', '''            # Negative offset -> left (higher PWM); positive -> right.
            # Small bench-test range only: 330..370, not the full driving range.
            command = 350 if offset is None else int(round(
                350 - 20 * float(np.clip(offset / 0.5, -1, 1))
            ))
            pwm.set_pwm(1, 0, command)
            process_ms =''')
replace_once('"" if offset is None else offset\n', '"" if offset is None else offset, command\n')
replace_once('f"offset={offset} process={process_ms:.1f}ms"', 'f"offset={offset} steering_pwm={command} process_and_pwm={process_ms:.1f}ms"')
replace_once('''    try:
        if started:
            camera.stop()
    finally:
        camera.close()''', '''    try:
        if pwm is not None:
            try:
                pwm.set_pwm(1, 0, 350)
                time.sleep(0.3)
            finally:
                pwm.set_pwm(1, 0, 4096)
    finally:
        if camera is not None:
            try:
                if started:
                    camera.stop()
            finally:
                camera.close()''')
source = source.replace('视觉处理耗时', '视觉加PWM写入耗时')
ast.parse(source)
compile(source, 'realtime_steering_only.py', 'exec')
output = Path('realtime_steering_only.py')
with output.open('x') as f:
    f.write(source)
print('Created:', output.resolve())
