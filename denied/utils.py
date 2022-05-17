from typing import Awaitable, Callable

# unasync does not handle Awaitable so we define
# both types here and AccessMethod will be translated
# to SyncAccessMethod by unasync in the _sync folder.
AccessMethod = Callable[..., Awaitable[bool]]
SyncAccessMethod = Callable[..., bool]
