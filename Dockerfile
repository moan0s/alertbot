FROM dock.mau.dev/maubot/maubot:v0.5.2-standalone AS deps

WORKDIR /plugin

RUN apk add --no-cache py3-dateutil-pyc=2.9.0-r1

FROM deps AS build

COPY . .

RUN mkdir build extract && mbc build -o build && unzip build/* -d extract

FROM deps

COPY --from=build --chmod=444 /plugin/extract/ /plugin

ENTRYPOINT ["python"]
CMD ["-m", "maubot.standalone"]

