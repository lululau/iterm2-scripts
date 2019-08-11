#!/usr/bin/env python3.7

import iterm2

async def main(connection):
    app = await iterm2.async_get_app(connection)
    window = app.current_terminal_window

    async def get_all_session():
        return [s for w in app.terminal_windows for t in w.tabs for s in t.sessions]

    async def get_session_by_tty(tty):
        sessions = [s for s in (await get_all_session()) if (await s.async_get_variable("tty")) == tty]
        if len(sessions) > 0:
            return sessions[0]
        else:
            return None

    @iterm2.RPC
    async def activate_session_by_tty(tty):
        await app.async_activate()
        session = await get_session_by_tty(tty)
        if session != None:
            await session.async_activate()
    await activate_session_by_tty.async_register(connection)

iterm2.run_forever(main)
