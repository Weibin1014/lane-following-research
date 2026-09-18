"""15-second camera-only capture; no motor/servo libraries or PWM writes."""
import csv,json,time,shutil
from datetime import datetime
from pathlib import Path
import cv2
from picamera2 import Picamera2

def main():
    print('保持驱动电机电池断开。小车放在桌椅背景的左弯入口。')
    print('本程序仅采集图像；开始后用手缓慢向前推过原停车区域，不要遮住镜头。')
    with open('/dev/tty') as terminal:
        print('准备好后输入YES：',flush=True)
        if terminal.readline().strip()!='YES':return
    camera=None;frames=[];rows=[];error=None
    out=Path('problem_sequence_results')/datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    out.mkdir(parents=True)
    try:
        camera=Picamera2()
        camera.configure(camera.create_video_configuration(main={'size':(160,120),'format':'RGB888'},controls={'FrameRate':20},buffer_count=4,queue=False))
        camera.start();time.sleep(2)
        for n in (3,2,1):print(n,flush=True);time.sleep(1)
        print('开始15秒采集：缓慢推过问题区域，经过后可停住。',flush=True)
        start=time.monotonic()
        while time.monotonic()-start<15 and len(frames)<600:
            request=camera.capture_request()
            try:
                frame=request.make_array('main').copy();metadata=request.get_metadata()
            finally:request.release()
            frames.append(frame)
            rows.append(dict(frame=len(frames),elapsed_s=time.monotonic()-start,sensor_timestamp=metadata.get('SensorTimestamp'),exposure_time=metadata.get('ExposureTime'),analogue_gain=metadata.get('AnalogueGain')))
    except BaseException as exc:error=f'{type(exc).__name__}: {exc}'
    finally:
        if camera is not None:
            try:camera.stop()
            finally:camera.close()
    print('采集结束，开始保存全部帧。',flush=True)
    for number,frame in enumerate(frames,1):
        if not cv2.imwrite(str(out/f'{number:06d}_raw.png'),frame):raise RuntimeError('图像保存失败')
    if rows:
        with (out/'frames.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    shutil.copy2(__file__,out/'capture_problem_sequence.py')
    summary=dict(frames=len(frames),saved_frames=len(frames),error=error,hardware_pwm=False,duration_limit_s=15,frame_limit=600)
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));print('结果目录:',out.resolve())
if __name__=='__main__':main()
