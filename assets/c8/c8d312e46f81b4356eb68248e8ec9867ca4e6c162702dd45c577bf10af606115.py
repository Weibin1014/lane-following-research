"""Stationary steering-only validation. Keep drive motor battery disconnected."""
import argparse
import csv
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
import cv2
from s2_preview_core_v2 import analyze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steering', action='store_true', help='Enable servo channel 1; motor battery must stay disconnected')
    args = parser.parse_args()
    from picamera2 import Picamera2
    out = Path('preview_v2_results') / datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    out.mkdir(parents=True)
    for name in ('s2_preview_core_v2.py', 'realtime_preview_v2.py'):
        shutil.copy2(Path(__file__).with_name(name), out/name)
    (out/'settings.json').write_text(json.dumps(dict(steering=args.steering, pwm_frequency=60,
        steering_channel=1, near_height=.65, far_heights=[.55,.60], trend_gain=1.5,
        pwm_range=[330,390], duration_seconds=30, drive_motor='battery disconnected'),indent=2))
    camera = None; pwm = None; started = False
    counts = {}; frames = 0
    try:
        if args.steering:
            print('V2边界配对：本程序仅做静态舵机验证。驱动电机电池必须一直断开，舵机保持供电。',flush=True)
            with open('/dev/tty') as terminal:
                print('确认电机电池已断开、车轮架空后，按回车开始：',flush=True)
                if not terminal.readline():
                    raise RuntimeError('未读取到开始输入')
            from Adafruit_PCA9685 import PCA9685
            pwm = PCA9685(address=0x40,busnum=1)
            pwm.set_pwm_freq(60)
            pwm.set_pwm(1,0,350)
        camera = Picamera2()
        camera.configure(camera.create_video_configuration(main={'size':(160,120),'format':'RGB888'},
            controls={'FrameRate':20},buffer_count=4,queue=False))
        (out/'camera_config.txt').write_text(str(camera.camera_configuration()))
        camera.start(); started=True; time.sleep(2)
        begin=time.perf_counter(); next_save=0; next_log=0; previous_direction=0
        fields=['frame','elapsed_s','capture_wait_ms','vision_and_pwm_ms','track_status','control_status',
            'near_status','far_status','pair_status','near_offset','far_y','far_x','preview_error','steering_pwm','pwm_sent']
        with (out/'frames.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            while time.perf_counter()-begin < 30:
                capture=time.perf_counter();frame=camera.capture_array('main');process=time.perf_counter()
                result=analyze(frame)
                if pwm is not None:pwm.set_pwm(1,0,result['steering_pwm'])
                done=time.perf_counter();elapsed=done-begin;frames+=1
                counts[result['control_status']]=counts.get(result['control_status'],0)+1
                row={k:result[k] for k in fields if k in result}
                row.update(frame=frames,elapsed_s=elapsed,capture_wait_ms=(process-capture)*1000,
                           vision_and_pwm_ms=(done-process)*1000,pwm_sent=pwm is not None)
                writer.writerow(row)
                direction = 0 if result['preview_error'] is None else (1 if result['preview_error'] > 0 else -1)
                if elapsed>=next_save or result['control_status']=='unavailable' or direction!=previous_direction:
                    next_save=elapsed+.2
                    view=cv2.resize(frame,(640,480))
                    cv2.line(view,(320,0),(320,479),(255,255,0),1)
                    for y,x in result['points']:cv2.circle(view,(round(x*4),round(y*480)),4,(0,0,255),-1)
                    if result['near_x'] is not None:cv2.circle(view,(round(result['near_x']*4),312),9,(0,255,0),2)
                    if result['far_x'] is not None:cv2.circle(view,(round(result['far_x']*4),round(result['far_y']*480)),9,(255,0,255),2)
                    cv2.putText(view,f"{result['control_status']} PWM={result['steering_pwm']}",(8,22),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,255,0),1)
                    for suffix,img in [('raw',frame),('debug',view)]:
                        if not cv2.imwrite(str(out/f'{frames:06d}_{suffix}.png'),img):raise RuntimeError('图片保存失败')
                previous_direction=direction
                if elapsed>=next_log:
                    next_log=elapsed+1;f.flush()
                    print(f"{elapsed:.1f}s {result['control_status']} near={result['near_offset']} far_y={result['far_y']} preview={result['preview_error']} PWM={result['steering_pwm']}",flush=True)
    except KeyboardInterrupt:
        print('已中断。',flush=True)
    finally:
        try:
            if pwm is not None:
                try:
                    pwm.set_pwm(1,0,350);time.sleep(.3)
                finally:
                    pwm.set_pwm(1,0,4096)
        except Exception as exc:
            print('舵机清理失败，请关闭舵机电源：',exc,flush=True)
        finally:
            if camera is not None:
                try:
                    if started:camera.stop()
                finally:camera.close()
            print('处理帧数:',frames,'控制状态:',counts,'结果目录:',out.resolve(),flush=True)

if __name__=='__main__':
    main()
