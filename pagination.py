from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from discord.ui import button, Button
from discord import ButtonStyle
import discord

if TYPE_CHECKING:
    from discord.ext.commands import Context
    from discord import (
        Message,
        Embed,
        Interaction,
        WebhookMessage,
        File
    )


class Page:

    __slots__ =('_content', '_embeds','_files')

    def __init__(
        self,
        content: Optional[str] = None,
        embeds: Optional[list[Embed]] = None,
        files: Optional[list[File]] = None
    ):
        self._content: Optional[str] = content
        self._embeds: list[Embed] = embeds or []
        self._files : list[File] = files or []


    @property
    def content(self) -> Optional[str]:
        return self._content


    @content.setter
    def content(self, value: Optional[str]):
        self._content = value


    @property
    def embeds(self) -> Optional[list[Embed]]:
        return self._embeds


    @embeds.setter
    def embeds(self, value: Optional[list[Embed]]):
        self._embeds = value


    @property
    def files(self) -> Optional[list[File]]:
        return self._files


    @files.setter
    def files(self, value: Optional[list[File]]):
        self._files = value



class Paginator(discord.ui.View):

    def __init__(
        self,
        pages: list[Page],
        add_stop_button: bool = False,
        author_check: bool = True,
        delete_on_timeout: bool = False,
        timeout: Optional[float] = 180.0
    ):
        super().__init__(timeout=timeout)
        self.pages: list[Page] = pages
        self.current_page: int = 0
        self.add_stop_button: bool = add_stop_button
        self.delete_on_timeout: bool = delete_on_timeout

        if not all(isinstance(p, Page) for p in pages):
            raise ValueError('`pages` argument only receive list[Page].')

        self.user_check: bool = author_check
        self.user = None
        self.message: Union[Message,WebhookMessage,None] = None
        self.clear_items()
        self.fill_items()


    @property
    def page_number(self) -> int:
        return len(self.pages)


    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if self.user_check:
            return self.user == interaction.user
        return True

    async def on_timeout(self) -> None:
        if self.message:
            if self.delete_on_timeout:
                await self.message.delete()
                return
            else:
                await self.message.edit(view=None)
        return



    def fill_items(self) -> None:
        use_last_and_first: bool = (self.page_number >=2)
        if use_last_and_first:
            self.add_item(self.to_first_page)
        self.add_item(self.to_previous_page)
        self.add_item(self.to_current_page)
        if use_last_and_first:
            self.add_item(self.to_next_page)
        self.add_item(self.to_last_page)
        if self.add_stop_button:
            self.add_item(self.stop_pages)
        return


    def update_labels(self, page_number: int) -> None:
        self.to_first_page.disabled = (page_number == 0)

        self.to_current_page.label = f'{self.current_page + 1}/{self.page_number}'
        self.to_next_page.disabled = False
        self.to_previous_page.disabled = False
        self.to_first_page.disabled = False

        self.to_last_page.disabled = (page_number + 1 >= self.page_number)

        if self.to_last_page.disabled:
            self.to_last_page.disabled = True
            self.to_next_page.disabled = True
        if page_number == 0:
            self.to_previous_page.disabled = True
            self.to_first_page.disabled = True

        return


    async def show_checked_page(self, interaction: Interaction ,page_number: int) -> None:
        if 0 <= page_number < self.page_number:
            try:
                await self.show_page(interaction,page_number)
            except IndexError:
                pass
        return


    async def show_page(self, interaction: Interaction ,page_number: int) -> None:
        self.current_page = page_number
        self.update_labels(page_number)
        page = self.pages[self.current_page]

        if interaction.response.is_done():
            if self.message:
                await self.message.edit(
                    content = page.content or None,
                    embeds = page.embeds or [],
                    attachments = page.files or [],
                    view = self
                )
        else:
            await interaction.response.edit_message(
                    content = page.content or None,
                    embeds = page.embeds or [],
                    attachments = page.files or [],
                    view = self
            )
        return


    async def send(self,context: Context) -> Message:
        self.update_labels(self.current_page)
        self.user = context.author
        page = self.pages[self.current_page]
        self.message = await context.send(
            content = page.content or None,
            embeds = page.embeds or [],
            files = page.files or [],
            view = self
        )
        return self.message


    async def respond(
        self,
        interaction: Interaction,
        ephemeral: bool = False
    ) -> Union[Message,WebhookMessage]:
        self.update_labels(self.current_page)
        self.user = interaction.user
        page = self.pages[self.current_page]

        if interaction.response.is_done():
            self.message = await interaction.followup.send(
                content = page.content or None,
                embeds = page.embeds or [],
                files = page.files or [],
                view = self,
                ephemeral = ephemeral
            )
        else:
            self.message = await interaction.response.send_message(
                content = page.content or None,
                embeds = page.embeds or [],
                files = page.files or [],
                view = self,
                ephemeral = ephemeral
            )
        return self.message


    @button(label='≪', style=ButtonStyle.grey, custom_id='to_first')
    async def to_first_page(self, interaction: Interaction, button: Button):
        await self.show_page(interaction,0)
        return


    @button(label='<', style=ButtonStyle.blurple, custom_id='to_previous')
    async def to_previous_page(self, interaction: Interaction, button: Button):
        await self.show_checked_page(interaction,self.current_page-1)
        return


    @button(label='Current', style=ButtonStyle.grey, disabled=True, custom_id='current_page')
    async def to_current_page(self, interaction: Interaction, button: Button):
        pass


    @button(label='>', style=ButtonStyle.blurple, custom_id='to_next')
    async def to_next_page(self, interaction: Interaction, button: Button):
        await self.show_checked_page(interaction,self.current_page+1)
        return


    @button(label='≫',style=ButtonStyle.gray, custom_id='to_last')
    async def to_last_page(self, interaction: Interaction, button: Button):
        await self.show_checked_page(interaction,self.page_number -1)
        return


    @button(label='Quit', style=ButtonStyle.red, custom_id='quit')
    async def stop_pages(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()