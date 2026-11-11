---
name: mascot-dolharubang
description: 샤오홍슈 nadllog 마스코트 "색연필 돌하르방" 캐릭터 만들기 규칙(모양·색·질감·이미지 생성 문장·피그마 위치). "돌하르방 ○○ 포즈로 만들어줘", 마스코트 새 포즈·표정을 만들거나 사진을 보내며 "이 포즈로" 할 때 쓴다.
---

# 마스코트: 색연필 돌하르방 (2026-11-11)

> 강정준비준이 "앞으로 샤오홍슈 캐릭터로 만들 거야. 색연필 돌하르방을. 마스코트야."라고 정함. 공통 규칙(호칭·한국어·저장 위치 알림 등)은 CLAUDE.md를 따른다.

## 기준 그림 (피그마 파일 `dnlLDtgRZ4Kk2VjlhmlhU8` "샤오홍슈")

- 기본: `780:2` "SD 돌하르방 ② 색연필" — 손 흔드는 포즈
- 포즈 예시: `782:2` "SD 돌하르방 ② 색연필 - 이마짚기" — 아기 사진 보고 만든 "아이고…" 포즈
- 샘플로 만든 다른 느낌(①·③·④·⑤)은 쓰지 않는다.

## 모양 규칙 (세트로 보이게 꼭 지킨다)

- 크레파스·색연필 질감, 연필 결이 보이는 빗금 칠, 살짝 삐뚤한 진회색 크레파스 테두리
- SD 비율: 머리가 몸만큼 큼, 작고 통통한 몸, 짧은 팔다리
- 돌하르방 버섯 모양 둥근 모자, 넓적한 둥근 코
- 몸·모자는 회색 + 현무암 구멍 같은 작은 진회색 점
- 작은 점 눈(감을 때는 곡선), 크고 연한 분홍 볼
- 흰 종이 배경, 글자 없음. 감정 표시(반짝이·땀방울·놀람 선)는 짧은 크레파스 선으로

## 만드는 방법

- 피그마 `generate_image`(세로 1024×1536)로 만들고 이름은 "SD 돌하르방 ② 색연필 - (포즈)"로 단다.
- **강정준비준의 작업 프레임 안에 넣지 않는다.** 겹치지 않는 빈 캔버스(기준 그림 근처)에 둔다.
- 사진을 보내며 "이 포즈로"라고 하면 사진의 자세·표정만 가져오고 모양 규칙은 그대로 둔다.
- 이미지 생성 문장(포즈 부분만 바꿔 쓴다):

```
Cute hand-drawn children's doodle illustration in colored pencil / crayon style, of a chibi Jeju Island dolharubang stone grandfather character. Style: soft waxy crayon texture with visible pencil strokes, slightly wobbly scribbly outlines in dark gray crayon, simple flat coloring filled with hatched gray pencil strokes, big soft pink blush circles on cheeks, a few small dark dots on the body for basalt holes. Character: very big round head (SD proportion, head as large as body), wearing the dolharubang mushroom-shaped round brimless hat, wide round nose, tiny black dot eyes. Pose and expression: (여기에 포즈). Full body, centered, plain white paper background, no text, minimal and cute like a sticker sheet doodle.
```

## 아직 정하지 않은 것 (강정준비준에게 확인하며 채운다)

- 이름(한국어·중국어), 성격·말버릇, 배경 없는(투명) 버전 필요 여부
