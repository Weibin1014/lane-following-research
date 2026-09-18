"""Static CNN recording check only. No drivetrain, no driving option."""
from pathlib import Path
from datetime import datetime
import os
import sys
import json
import hashlib
import shutil


def main():
    car = Path('/home/student/projects/mycar')
    os.chdir(car)
    sys.path.insert(0, str(car))
    import manage
    import donkeycar as dk

    cfg = dk.load_config(myconfig=str(car / 'myconfig.py'))
    out = car / 'pixel_evaluation_20260912' / ('CNN_STATIC_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    out.mkdir(parents=True, exist_ok=False)
    model = car / 'models/mypilot.tflite'
    cfg.DRIVE_TRAIN_TYPE = 'MOCK'
    cfg.USE_JOYSTICK_AS_DEFAULT = False
    cfg.WEB_INIT_MODE = 'local_angle'
    cfg.AUTO_RECORD_ON_THROTTLE = False
    cfg.RECORD_DURING_AI = True
    cfg.AUTO_CREATE_NEW_TUB = False
    cfg.DATA_PATH = str(out / 'tub')
    cfg.MAX_LOOPS = 300
    cfg.HAVE_RGB_LED = False
    cfg.USE_SSD1306_128_32 = False
    cfg.HAVE_MQTT_TELEMETRY = False

    def no_drivetrain(vehicle, config):
        assert config.DRIVE_TRAIN_TYPE == 'MOCK'
        print('STATIC CHECK: drivetrain omitted; no steering or throttle output.', flush=True)

    # These overrides apply only inside this dedicated static-check process.
    manage.add_drivetrain = no_drivetrain
    manage.ToggleRecording.run = lambda self, mode, recording: True
    for name in ['manage.py', 'config.py', 'myconfig.py']:
        shutil.copy2(car / name, out / name)
    shutil.copy2(__file__, out / 'cnn_static_capture.py')
    info = dict(kind='static_only_not_driving', hardware_pwm=False,
                model=str(model), model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
                model_type='tflite_linear', max_loops=cfg.MAX_LOOPS,
                image_width=cfg.IMAGE_W, image_height=cfg.IMAGE_H,
                recording_forced=True, error=None, completed=False)
    print('RESULT DIRECTORY:', out, flush=True)
    (out / 'capture_info.json').write_text(json.dumps(info, indent=2))
    try:
        manage.drive(cfg, model_path=str(model), model_type='tflite_linear',
                     use_joystick=False, camera_type='single', meta=['purpose:static_capture_check'])
        info['completed'] = True
    except BaseException as exc:
        info['error'] = repr(exc)
        raise
    finally:
        info['saved_jpg_count'] = len(list((out / 'tub').rglob('*.jpg')))
        (out / 'capture_info.json').write_text(json.dumps(info, indent=2))
        print(json.dumps(info, indent=2), flush=True)
        print('RESULT DIRECTORY:', out, flush=True)


if __name__ == '__main__':
    main()
