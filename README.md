![Alertbot banner](assets/alertbanner.png)

# Alertbot

This bot uses the webhook functionality of monitoring/alerting solutions like Grafana or Alertmanager to forward alerts to matrix rooms.
This means that you no longer have to use E-Mail or Slack to receive alerts. See the setup below for how to use it or
join the [Alertbot room on matrix](https://matrix.to/#/#alertbot:hyteck.de)

# Getting Started

## OPTION 1: Use provided alertbot

* Create a Matrix room and invite @alertbot:hyteck.de
* Send `!url` to the room. The bot will answer with the webhook URL
* Put the Webhook URL into your monitoring solution (see below)

## OPTION 2: Selfhost alertbot

**Prerequisites:**
* A Matrix server where you have access to a maubot instance: Please [refer to the docs](https://docs.mau.fi/maubot/usage/setup/index.html) for setting up one
* An instance of alertmanager or grafana or a similar alerting program that is able to send webhooks

**Getting the code**

Clone this repository to your local computer and install maubot to have access to the maubot CLI
```shell
git clone https://github.com/moan0s/alertbot
cd alertbot
pip install maubot
```

**Login to your maubot instance**

```shell
mbc login
```

**Build&Upload the plugin**

```shell
mbc build -u
```

You now have the plugin installed. Now you have to set up an instance of the bot in the maubot manager and invite it to
the room where the alerts should be sent. Also find out the room id by asking the bot for it with `!roomid`.



# Setup Alertmanager

This configuration will send all your alerts to the room `!zOcbWjsWzdREnihgeC:example.com` (if the bot has access to it).
Put in your own room-id (`!roomid`) behind the webhook base url (`!url`):
```yaml

receivers:
- name: alertbot
  webhook_configs:
  - url: https://synapse.hyteck.de/_matrix/maubot/plugin/alertbot/webhook/!zOcbWjsWzdREnihgeC:example.com
route:
  group_by:
  - alertname
  - cluster
  - service
  group_interval: 5m
  group_wait: 30s
  receiver: alertbot
  repeat_interval: 3h

```


# Setup Grafana

The grafana setup is fairly simple and can be used to forward grafana alerts to matrix.

![Screenshot of the Grafana Setup](assets/grafana.png)


# Test your setup

It can be a bit annoying to trigger an alert (e.g. by shutting down a server) to test if your configuration is right and if the bot works as intended.
Therefore, you find a few example alerts in `alert_examples/` which allow you to test the bot.

Use them with the following command (but adjust the webhook URL):

```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data "@alert_examples/data.json" \
  https://webhook.example.com/_matrix/maubot/plugin/maubot/webhook/!zOcbWjsWzdREnihreC:example.com
```

# Local testing Setup

You might want to test the bot on your local machine but send webhooks to a public server. To do that use a domain 
e.g. webbhook.example.com and configure nginx as reverse proxy for port 4242 for this domain.

## Connect

Run the local server and connect via (29316 is the local maubot port)
`ssh -N -R 4242:localhost:29316 webhook.example.com`

## Send some data with

Use an example from the `alert_examples/` to test your setup
```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data "@alert_examples/prometheus.json" \
  https://webhook.example.com/_matrix/maubot/plugin/maubot/webhook/!zOcbWjsWzdREnihreC:example.com
```

