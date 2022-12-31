#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import timedelta

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.adapters.onebot.v12 import Adapter as ONEBOT_V12Adapter

# Custom your logger
from nonebot.log import logger, default_format

log_path = Path(__file__).parent / "logs" / "info.log"
logger.add(log_path,
           rotation=timedelta(days=7),
           retention=timedelta(days=30),
           diagnose=True,
           backtrace=True,
           level="INFO",
           format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
driver.register_adapter(ONEBOT_V12Adapter)

# nonebot.load_builtin_plugins("echo")
# nonebot.load_builtin_plugins("single_session")

# Please DO NOT modify this file unless you know what you are doing!
# As an alternative, you should use command `nb` or modify `pyproject.toml` to load plugins
nonebot.load_from_toml("pyproject.toml")

# Modify some config / config depends on loaded configs
# 
# config = driver.config
# do something...


if __name__ == "__main__":
    # nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
