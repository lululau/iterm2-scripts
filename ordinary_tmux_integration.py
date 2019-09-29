#!/usr/bin/env python3.7

import iterm2

async def main(connection):
    app = await iterm2.async_get_app(connection)

    async def get_all_session():
        return [s for w in app.terminal_windows for t in w.tabs for s in t.sessions]

    async def get_session_by_tty(tty):
        sessions = [s for s in (await get_all_session()) if (await s.async_get_variable("tty")) == tty]
        if len(sessions) > 0:
            return sessions[0]
        else:
            return None

    async def exec_on_tab(tab, command):
        await tab.current_session.async_send_text(command+"\n")

    async def find_idle_tab():
        for tab in app.current_terminal_window.tabs:
            job_name = await tab.current_session.async_get_variable("jobName")
            if job_name == 'zsh' or job_name == 'bash' or job_name == 'sh' or job_name == 'fish':
                return tab
        return None

    async def find_tmux_tabs():
        return [t for t in enumerate(app.current_terminal_window.tabs) if (await t[1].current_session.async_get_variable("jobName")) == 'tmux']

    async def create_tab():
        window = app.current_terminal_window
        tmux_tabs = await find_tmux_tabs()
        if len(tmux_tabs) == 0:
            index = len(window.tabs)
        else:
            index, tab = tmux_tabs[0]
        return await window.async_create_tab(None, None, index)

    @iterm2.RPC
    async def activate_session_by_tty(tty):
        await app.async_activate()
        session = await get_session_by_tty(tty)
        if session != None:
            await session.async_activate()
    await activate_session_by_tty.async_register(connection)

    @iterm2.RPC
    async def exec_on_tab_at(tab_index, command):
        tab = [t for t in app.current_terminal_window.tabs][tab_index]
        await exec_on_tab(tab, command)
    await exec_on_tab_at.async_register(connection)

    @iterm2.RPC
    async def find_or_create_idle_tab():
       tab = await find_idle_tab()
       if tab != None:
           return tab
       else:
           tab = await create_tab()
           return tab
    await find_or_create_idle_tab.async_register(connection)

    @iterm2.RPC
    async def run_ssh(host):
       tab = await find_or_create_idle_tab()
       await app.async_activate()
       await tab.async_activate()
       await exec_on_tab(tab, "clear; SSH_INTERACTIVE=1 ssh " + host)
    await run_ssh.async_register(connection)

    @iterm2.RPC
    async def activate_tab_by_id(tab_id):
       await app.async_activate()
       tab = app.get_tab_by_id(tab_id)
       await tab.async_activate()
    await activate_tab_by_id.async_register(connection)

    @iterm2.RPC
    async def get_tab_commands():
        return [{"tab_id": t.tab_id, "command": await t.current_session.async_get_variable('commandLine')} for t in app.current_terminal_window.tabs]
    await get_tab_commands.async_register(connection)

iterm2.run_forever(main)
