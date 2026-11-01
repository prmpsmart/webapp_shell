from webapp_shell.backend_process import BackendError
from webapp_shell.messages import MessageKey, ShellMessages
from webapp_shell.watchdog import BackendWatchdog


class FakeBackend:
    def __init__(self, fail_restart=False):
        self.died, self.restarts, self.fail_restart = False, 0, fail_restart

    def restart(self):
        self.restarts += 1
        if self.fail_restart:
            raise BackendError("the backend did not start")
        self.died = False


def watchdog(backend, **options):
    said = []
    clock = options.pop("clock", lambda: 0.0)
    return BackendWatchdog(backend, said.append, clock=clock, **options), said


def test_a_running_engine_is_left_alone():
    backend = FakeBackend()
    dog, said = watchdog(backend)
    dog.check()
    assert backend.restarts == 0 and said == []


def test_an_engine_that_stopped_is_started_again():
    backend = FakeBackend()
    dog, said = watchdog(backend)
    backend.died = True
    dog.check()
    assert backend.restarts == 1 and said == []


def test_it_gives_up_after_too_many_restarts_in_a_short_time():
    backend = FakeBackend()
    dog, said = watchdog(backend, max_restarts=2)
    for _ in range(3):
        backend.died = True
        dog.check()
    assert backend.restarts == 2 and said == [ShellMessages().text(MessageKey.BACKEND_GAVE_UP, name="the program")]


def test_old_restarts_are_forgotten():
    backend, now = FakeBackend(), [0.0]
    dog, said = watchdog(backend, max_restarts=1, window=60, clock=lambda: now[0])
    for at in (0, 100, 200):
        now[0] = at
        backend.died = True
        dog.check()
    assert backend.restarts == 3 and said == []


def test_a_restart_that_fails_is_reported():
    backend = FakeBackend(fail_restart=True)
    dog, said = watchdog(backend)
    backend.died = True
    dog.check()
    assert said == ["the backend did not start"]


def test_a_killed_backend_comes_back_on_the_same_address_and_token(settings):
    from webapp_shell.backend_process import BackendProcess

    backend = BackendProcess(settings, keeps_preferences=False)
    with backend:
        address, token = backend.base_url, backend.token
        backend._proc.kill()
        backend._proc.wait()
        assert backend.died
        backend.restart()
        assert not backend.died and backend.base_url == address and backend.token == token
        assert backend.version()["version"]
    assert not backend.died  # stopped on purpose is not a death


def test_the_give_up_message_names_the_program():
    backend = FakeBackend()
    said = []
    dog = BackendWatchdog(backend, said.append, name="Acme Notes", max_restarts=0)
    backend.died = True
    dog.check()
    assert "Acme Notes" in said[0]
