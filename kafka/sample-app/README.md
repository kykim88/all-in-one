# kafka sample app

kafka sample producer / consumer

## Installation : Python env
 
[1] Install [pdm](https://pdm.fming.dev/latest/#installation)
```
$ brew install pdm
```
[2] Install packages & create .venv
```
$ pdm install

...
....
🎉 All complete!
```
[3] [Activate venv](https://pdm.fming.dev/latest/usage/venv/#activate-a-virtualenv)
```
$ eval $(pdm venv activate)
```

## Run : Local Docker
```
$ docker-compose up --build

# consumer만 다시 빌드/실행
$ docker compose up -d --no-deps --build test-consumer
```
kafka-ui에서 topic 확인 
- http://localhost:4004 

log 확인
```
$ docker-compose logs -f test-producer
$ docker-compose logs -f test-consumer
```