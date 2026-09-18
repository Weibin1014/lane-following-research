"""One-shot motion gate. No hardware imports."""
DURATION_SECONDS = 8.0

class Gate:
    def __init__(self):
        self.started = None
        self.streak = 0
        self.reason = None
    def stop(self, reason):
        if self.reason is None:
            self.reason = reason
    def tick(self, now, ready, fresh=True):
        if self.reason:
            return 370
        if self.started is not None:
            if now - self.started >= DURATION_SECONDS:
                self.stop('time_limit')
            elif not fresh:
                self.stop('stale_frame')
            elif not ready:
                self.stop('target_unavailable')
        else:
            self.streak = self.streak + 1 if ready and fresh else 0
            if self.streak >= 5:
                self.started = now
        return 400 if self.started is not None and self.reason is None else 370

def self_test():
    g = Gate()
    assert all(g.tick(i*.05, True) == 370 for i in range(4))
    assert g.tick(.2, True) == 400
    assert g.tick(.25, False) == 370
    assert g.reason == 'target_unavailable'
    assert all(g.tick(i, True) == 370 for i in range(1, 10))
    g = Gate()
    for i in range(5): g.tick(i*.05, True)
    assert g.tick(2.21, True) == 400
    assert g.tick(5.21, True) == 400
    assert g.tick(8.19, True) == 400
    assert g.tick(8.21, True) == 370 and g.reason == 'time_limit'
    g = Gate()
    for i in range(5): g.tick(i*.05, True)
    assert g.tick(.25, True, False) == 370 and g.reason == 'stale_frame'
    g = Gate()
    for i in range(4): g.tick(i*.05, True)
    assert g.tick(.2, False) == 370 and g.streak == 0
    g.stop('watchdog')
    assert g.tick(1, True) == 370
    print('PASS: five-frame gate, loss latch, timeout, stale frame, streak reset, external stop')

if __name__ == '__main__': self_test()
