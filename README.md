# Setup

Use a domain e.g. webbhook.hyteck.de and configure nginx as 
reverse proxy for port 4242 for this domain.

# Connect

Run the local server and connect via (29316 is the local maubot port)
`ssh -N -R 4242:localhost:29316 s`



# Send some data with


Put the following in `data.json`
```json
{"receiver":"matrix","status":"firing","alerts":[{"status":"firing","labels":{"alertname":"InstanceDown","environment":"h2916641.stratoserver.net","instance":"localhost:9100","job":"node_exporter","severity":"critical"},"annotations":{"description":"localhost:9100 of job node_exporter has been down for more than 5 minutes.","summary":"Instance localhost:9100 down"},"startsAt":"2022-06-23T11:53:14.318Z","endsAt":"0001-01-01T00:00:00Z","generatorURL":"http://h2916641.stratoserver.net:9090/graph?g0.expr=up+%3D%3D+0\u0026g0.tab=1","fingerprint":"9cd7837114d58797"}],"groupLabels":{"alertname":"InstanceDown"},"commonLabels":{"alertname":"InstanceDown","environment":"h2916641.stratoserver.net","instance":"localhost:9100","job":"node_exporter","severity":"critical"},"commonAnnotations":{"description":"localhost:9100 of job node_exporter has been down for more than 5 minutes.","summary":"Instance localhost:9100 down"},"externalURL":"https://alert.hyteck.de","version":"4","groupKey":"{}:{alertname=\"InstanceDown\"}","truncatedAlerts":0}
```
and then 
```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data "@data.json" \
  https://webhook.hyteck.de/_matrix/maubot/plugin/maubot/webhook
```
