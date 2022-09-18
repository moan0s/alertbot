from maubot import Plugin, MessageEvent
from maubot.handlers import web, command
from aiohttp.web import Request, Response, json_response
import json
import datetime

helpstring = f"""# Alertbot

To control the alertbot you can use the following commands:
* `!help`: To show this help
* `!ping`: To check if the bot is alive
* `!raw`: To toggle raw mode (where webhook data is not parsed but simply forwarded as copyable text)
* `!roomid`: To let the bot show you the current matrix room id
* `!url`: To let the bot show you the webhook url

More information is on [Github](https://github.com/moan0s/alertbot)
"""


def get_alert_type(data):
    """
    Currently supported are ["grafana-alert", "grafana-resolved", "prometheus-alert", "not-found"]

    :return: alert type
    """

    # Uptime-kuma has heartbeat
    try:
        if data["heartbeat"]["status"] == 0:
            return "uptime-kuma-alert"
        elif data["heartbeat"]["status"] == 1:
            return "uptime-kuma-resolved"
    except KeyError:
        pass

    # Grafana
    try:
        data["alerts"][0]["labels"]["grafana_folder"]
        if data['status'] == "firing":
            return "grafana-alert"
        else:
            return "grafana-resolved"
    except KeyError:
        pass

    # Prometheus
    try:
        if data["alerts"][0]["labels"]["job"]:
            if data['status'] == "firing":
                return "prometheus-alert"
            else:
                return "grafana-resolved"
    except KeyError:
        pass

    return "not-found"


def get_alert_messages(alert_data: dict, raw_mode=False) -> list:
    """
    Returns a list of messages in markdown format

    :param alert_data: The data send to the bot as dict
    :param raw_mode: Toggles a mode where the data is not parsed but simply returned as code block in a message
    :return: List of alert messages in markdown format
    """

    alert_type = get_alert_type(alert_data)

    if raw_mode or alert_type == "not-found":
        return ["**Data received**\n```\n" + str(alert_data).strip("\n").strip() + "\n```"]
    else:
        if alert_type == "grafana-alert":
            messages = grafana_alert_to_markdown(alert_data)
        elif alert_type == "grafana-resolved":
            messages = grafana_alert_to_markdown(alert_data)
        elif alert_type == "prometheus-alert":
            messages = prometheus_alert_to_markdown(alert_data)
        elif alert_type == "uptime-kuma-alert":
            messages = uptime_kuma_alert_to_markdown(alert_data)
        elif alert_type == "uptime-kuma-resolved":
            messages = uptime_kuma_resolved_to_markdown(alert_data)
    return messages


def uptime_kuma_alert_to_markdown(alert_data: dict):
    tags_readable = ", ".join([tag["name"] for tag in alert_data["monitor"]["tags"]])
    message = (
        f"""**Firing 🔥**: Monitor down: {alert_data["monitor"]["url"]}

* **Error:** {alert_data["heartbeat"]["msg"]}
* **Started at:** {alert_data["heartbeat"]["time"]}
* **Tags:** {tags_readable}
* **Source:** "Uptime Kuma"
                    """
    )
    return [message]


def uptime_kuma_resolved_to_markdown(alert_data: dict):
    return ["**Uptime Kuma Resolved Data:**\n```\n" + str(alert_data).strip("\n").strip() + "\n```"]


def grafana_alert_to_markdown(alert_data: dict) -> list:
    """
    Converts a grafana alert json to markdown

    :param alert_data:
    :return: Alerts as formatted markdown string list
    """
    messages = []
    for alert in alert_data["alerts"]:
        datetime_format = "%Y-%m-%dT%H:%M:%S%z"
        if alert['status'] == "firing":
            message = (
                f"""**Firing 🔥**: {alert['labels']['alertname']}  
    
* **Instance:** {alert["valueString"]}
* **Silence:** {alert["silenceURL"]}
* **Started at:** {alert['startsAt']}
* **Fingerprint:** {alert['fingerprint']}
                """
            )
        if alert['status'] == "resolved":
            end_at = datetime.datetime.strptime(alert['endsAt'], datetime_format)
            start_at = datetime.datetime.strptime(alert['startsAt'], datetime_format)
            message = (
                f"""**Resolved 🥳**: {alert['labels']['alertname']}
    
* **Duration until resolved:** {end_at - start_at}
* **Fingerprint:** {alert['fingerprint']}
                """
            )
        messages.append(message)
    return messages


def prometheus_alert_to_markdown(alert_data: dict) -> str:
    """
    Converts a prometheus alert json to markdown

    :param alert_data:
    :return: Alert as fomatted markdown
    """
    messages = []
    for alert in alert_data["alerts"]:
        message = (
            f"""**{alert['status']}**: {alert['annotations']['description']}  
    
* **Alertname:** {alert["labels"]['alertname']}
* **Instance:** {alert["labels"]['instance']}
* **Job:** {alert["labels"]['job']}
            """
        )
        messages.append(message)
    return messages


class AlertBot(Plugin):
    raw_mode = False

    async def send_alert(self, req, room):
        text = await req.text()
        self.log.info(text)
        content = json.loads(f"{text}")
        for message in get_alert_messages(content, self.raw_mode):
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

    @command.new()
    async def raw(self, evt: MessageEvent) -> None:
        self.raw_mode = not self.raw_mode
        """Switches the bot to raw mode or disables raw mode (mode where data is not formatted but simply forwarded)"""
        await evt.reply(f"Mode is now: `{'raw' if self.raw_mode else 'normal'} mode`")

    @command.new()
    async def help(self, evt: MessageEvent) -> None:
        await self.client.send_markdown(evt.room_id, helpstring)
