"""room mock code"""
import asyncio
from typing import cast
import random

from wechaty import (   # type: ignore
    Wechaty,
    WechatyOptions
)

from wechaty_puppet import (    # type: ignore
    Puppet,
)

from wechaty_puppet_mock import (
    PuppetMock,
    PuppetMockOptions,
    EnvironmentMock,
    Mocker
)


async def mocker_example():
    """basic mocker example"""

    # init the mocker
    environment = EnvironmentMock()
    mocker = Mocker()
    mocker.use(environment)

    # init the puppet_mock
    puppet_options = PuppetMockOptions(mocker=mocker)
    puppet = PuppetMock(puppet_options)

    # init the wechaty
    wechaty_options = WechatyOptions(
        puppet=cast(Puppet, puppet),
        puppet_options=puppet_options
    )
    bot = Wechaty(wechaty_options)

    mocker.init(puppet, mocker)

    await bot.start()

    # send the message to a room
    room = mocker.new_room()
    members = await room.member_list()
    one_of_member = random.choice(members)
    mocker.send_message(
        talker=one_of_member,
        conversation=room,
        msg='ding'
    )


if __name__ == '__main__':
    asyncio.run(mocker_example())