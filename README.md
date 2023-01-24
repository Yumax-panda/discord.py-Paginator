# Discord.py Pagination

本プログラムでは、Discord.pyにてページ表示をサポートするクラスを定義しました。

## クラスとメソッドの詳細

```py
class Page(
    content: str | None = None,
    embeds: list[Embed] | None = None,
    files: list[File] | None = None
)
```

１ページで表示する内容を定義したクラス。<br>
`content`か`embeds`のいずれかは`None`以外でないといけません。

### パラメータ

content (`str`) - １ページに表示する文字列。<br>
embeds (`list[discord.Embed]`) - １ページに表示する埋め込みのリスト。<br>
files (`list[discord.File]`) - １ページに添付するファイルのリスト。 <br>

```py

class Paginator(
    pages: list[Page],
    add_stop_button: bool = False,
    author_check: bool = True,
    delete_on_timeout: bool = False,
    timeout: Optional[float] = 180.0
)
```

ページをまとめたクラス。`discord.ui.View`クラスを継承しています。

### パラメータ

pages (`list[Page]`) - 送信するページのリスト。<br>
add_stop_button (`bool`) - ページを停止させるボタンを付けるかどうか。<br>
author_check (`bool`) - ページの送信者のみがページを操作できるかどうか。<br>
delete_on_timeout (`bool`) - タイムアウト時にページを削除するかどうか。<br>
timeout (`float`) -　`discord.ui.View`の`timeout`と同じです。　<br>

### メソッド

```py
async def send(context: commands.Context) -> Message
```

作成したページを送信するメソッド。

```py
async def respond(
    interaction: discord.Interaction,
    ephemeral: bool = False
) -> Message | WebhookMessage
```

作成したページをインタラクションを介して送信するメソッド。<br>
このメソッドが呼び出されるまえにインタラクションの応答を返している場合は内部的に`interaction.followup.send`が、そうでない場合は`interaction.response.send_message`が呼び出されています。

### 使用例

以下は`$info`コマンドで、サーバー内のメンバーの情報が1人あたり１ページで表示される例です。

```py
from discord.ext import commands
from discord import Embed
import discord

from pagination import Page, Paginator


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = Bot()


@bot.command()
async def info(ctx: commands.Context):
    embeds: list[Embed] = []
    for member in ctx.guild.members:
        embeds.append(Embed(title=str(member),description=f'id {member.id}'))

    await Paginator(
        pages = [Page(embeds = [e]) for e in embeds],
        add_stop_button = True,
        delete_on_timeout = True
    ).send(ctx)

    return


```
