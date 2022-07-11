from maubot import Plugin, MessageEvent
from maubot.handlers import web, command
from aiohttp.web import Request, Response, json_response
import json


def get_alert_messages(alertmanager_data: dict) -> list:
    """
    Returns a list of messages in markdown format

    :param alertmanager_data:
    :return: List of alert messages in markdown format
    """
    messages = []
    for alert in alertmanager_data["alerts"]:
        messages.append(alert_to_markdown(alert))
    return messages


def alert_to_markdown(alert: dict) -> str:
    """
    Converst a alert json to markdown

    :param alert:
    :return: Alert as fomatted markdown
    """
    message = (
        f"""**{alert['status']}**: {alert['annotations']['description']}  

* **Alertname:** {alert["labels"]['alertname']}
* **Instance:** {alert["labels"]['instance']}
* **Job:** {alert["labels"]['job']}
"""
    )
    return message



class AlertBot(Plugin):

    async def send_alert(self, req, room):
        text = await req.text()
        self.log.info(text)
        content = json.loads(f"{text}")
        for message in get_alert_messages(content):
            self.log.debug(f"Sending alert to {room}")
            await self.client.send_markdown(room, message)

    @web.post("/webhook/{room_id}")
    async def webhook_room(self, req: Request) -> Response:
        room_id = req.match_info["room_id"].strip()
        await self.send_alert(req, room=room_id)
        return json_response({"status": "ok"})

    @command.new()
    async def ping(self, evt: MessageEvent) -> None:
        """Answers pong to check if the bot is running"""
        await evt.reply("pong")

    @command.new()
    async def roomid(self, evt: MessageEvent) -> None:
        """Answers with the current room id"""
        await evt.reply(f"`{evt.room_id}`")

    @command.new()
    async def url(self, evt: MessageEvent) -> None:
        """Answers with the url of the webhook"""
        await evt.reply(f"`{self.webapp_url}/webhook`")
