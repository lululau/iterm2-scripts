#!/usr/bin/env python3.7

import asyncio
import iterm2

async def main(connection):
    app = await iterm2.async_get_app(connection)

    async def init_alternative_tab_id(window):
        first_tab = window.tabs[0]
        if not await window.async_get_variable("user.ALTERNATIVE_TAB_PREV_ID"):
            await window.async_set_variable("user.ALTERNATIVE_TAB_PREV_ID", first_tab.tab_id);
        if not await window.async_get_variable("user.ALTERNATIVE_TAB_CUR_ID"):
            await window.async_set_variable("user.ALTERNATIVE_TAB_CUR_ID", first_tab.tab_id);

    async def update_alternative_tab_id(tab_id):
        window = app.get_window_for_tab(tab_id)
        if await window.async_get_variable("user.ALTERNATIVE_TAB_CUR_ID") != tab_id:
            await window.async_set_variable("user.ALTERNATIVE_TAB_PREV_ID", await window.async_get_variable("user.ALTERNATIVE_TAB_CUR_ID"))
            await window.async_set_variable("user.ALTERNATIVE_TAB_CUR_ID", tab_id)


    for window in app.terminal_windows:
        await init_alternative_tab_id(window)

    @iterm2.RPC
    async def select_alternative_tab():
        await app.get_tab_by_id(await app.current_terminal_window.async_get_variable("user.ALTERNATIVE_TAB_PREV_ID")).async_activate()
    await select_alternative_tab.async_register(connection)

    async with iterm2.FocusMonitor(connection) as mon:
        while True:
            update = await mon.async_get_next_update()
            if update.selected_tab_changed:
                await update_alternative_tab_id(update.selected_tab_changed.tab_id)
            if update.window_changed:
                await init_alternative_tab_id(app.get_window_by_id(update.window_changed.window_id))

iterm2.run_forever(main)
