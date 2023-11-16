# yeongam generation collector 

염암풍력발전소 발전량 수집 (작성중)

#### Table of contents: 

[Installation : Python env](#installation--python-env)  
[Test : Local](#test--local)  
[Run : Local Docker](#run--local-docker) 

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

## Test : Local
```
$ python src/test_opcua_client.py

....
....
DAEMYOUNG_EMS.REE02_WF_WTG16_Wind_Speed : (2023-10-18 08:28:42.591000, 2023-10-18 08:28:44.332949) 3.810408353805542
DAEMYOUNG_EMS.REE02_WF_WTG07_Wind_Speed : (2023-10-18 08:28:42.586000, 2023-10-18 08:28:44.330954) 1.8514256477355957
....
....
```

## Run : Local Docker
```
$ docker-compose up --build
```
kafka-ui에서 topic 확인 
- http://localhost:4004 
- topic 명   
  - local-hz-infra-power-generation-yeongam 
  - local-hz-infra-wind-direction-yeongam
  - local-hz-infra-wind-speed-yeongam

wind-collector log 확인
```
$ docker-compose logs -f wind-collector
```