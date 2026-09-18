"""Launch existing manage.py with HTTP mode/recording latch compatibility fix."""
import json
import runpy
import sys
from pathlib import Path


def install_http_latches(api_class):
    original_post = api_class.post

    def post_with_latches(self):
        data = json.loads(self.request.body)
        result = original_post(self)
        # Apply requested state after vehicle-loop defaults, as WebSocket does.
        if data.get('drive_mode') is not None:
            self.application.mode_latch = data['drive_mode']
        if data.get('recording') is not None:
            self.application.recording_latch = data['recording']
        return result

    api_class.post = post_with_latches


def main():
    from donkeycar.parts.web_controller.web import DriveAPI
    install_http_latches(DriveAPI)
    print('HTTP mode and recording latch fix active.', flush=True)
    manage = Path(__file__).resolve().with_name('manage.py')
    sys.argv[0] = str(manage)
    runpy.run_path(str(manage), run_name='__main__')


if __name__ == '__main__':
    main()
