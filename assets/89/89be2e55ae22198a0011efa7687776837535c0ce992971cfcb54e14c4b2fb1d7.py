"""Generate the first bounded straight-track test without running hardware."""
import ast
from pathlib import Path

source = Path('realtime_loss_stop_test.py').read_text()
expected = 'throttle = 450 if motor_start is not None and not motor_done else 370'
if source.count(expected) != 1:
    raise RuntimeError('源程序与预期不一致，未生成文件。')
source = source.replace('450', '400')
source = source.replace('Path("loss_stop_results")', 'Path("straight_400_results")')
source = source.replace('架空停车测试准备中；尚未启动电机。', '直道400测试准备中；尚未启动电机。')
source = source.replace('驱动轮必须离地。', '确认前方赛道清空，并准备随时断开电机电池。')
source = source.replace('准备遮挡镜头。', '不要遮挡镜头；按Ctrl+C可提前停车。')
source = source.replace('现在遮挡镜头，或按Ctrl+C。', '直道测试中；按Ctrl+C可提前停车。')
compile(source, 'realtime_straight_400.py', 'exec')
with Path('realtime_straight_400.py').open('x') as f:
    f.write(source)
print('已生成 realtime_straight_400.py；尚未运行硬件。')
