---
name: mascot-dolharubang
description: 샤오홍슈 nadllog 마스코트 "르방"(색연필 돌하르방) 캐릭터 만들기 규칙(모양·색·질감·이미지 생성 문장·피그마 위치). "돌하르방 ○○ 포즈로 만들어줘", 마스코트 새 포즈·표정을 만들거나 사진을 보내며 "이 포즈로" 할 때 쓴다.
---

# 마스코트: 르방 — 색연필 돌하르방 (2026-11-11)

- **이름: 르방** (강정준비준이 정함, 2026-11-11). "돌하르방"의 끝을 딴 이름.
- **중국어 이름: 小鲁邦** (Xiǎo Lǔbāng, 꼬마 루방) — 돌하르방 음역 多尔哈鲁邦의 끝 鲁邦 + 귀여운 애칭 小. (2026-11-11 정함)
- **설정: 돌하르방(石头爷爷, 돌 할아버지)의 손주.** 이름만으로는 돌하르방인 걸 알기 어려워서, 르방이 처음 나오는 글·프로필에 아래 소개 한 줄을 넣는다.
  - 我是小鲁邦，济州岛石头爷爷的小孙孙🗿 (Wǒ shì Xiǎo Lǔbāng, Jìzhōudǎo shítou yéye de xiǎo sūnsun)
  - 뜻: 저는 꼬마 루방, 제주도 돌하르방(돌 할아버지)의 꼬마 손주예요🗿
  - 손주를 쓸 때 **孙子는 쓰지 않는다**(중국에서 욕으로도 쓰임). 귀여운 말 孙孙을 쓴다.

> 강정준비준이 "앞으로 샤오홍슈 캐릭터로 만들 거야. 색연필 돌하르방을. 마스코트야."라고 정함. 공통 규칙(호칭·한국어·저장 위치 알림 등)은 CLAUDE.md를 따른다.

## 기준 그림 (피그마 파일 `dnlLDtgRZ4Kk2VjlhmlhU8` "샤오홍슈")

- 기본: `780:2` "SD 돌하르방 ② 색연필" — 손 흔드는 포즈
- 포즈 예시: `782:2` "SD 돌하르방 ② 색연필 - 이마짚기" — 아기 사진 보고 만든 "아이고…" 포즈
- 표정 예시: `786:2` "SD 돌하르방 ② 색연필 - 슬픈 표정" (2026-11-11) — 처진 눈썹, 파란 눈물 한 방울, 시무룩한 입, 팔 축 늘어짐, 머리 위 파란 우울 선. 분실물 팻말 프레임(`784:349`) 오른쪽 빈 캔버스에 둠.
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

- 성격·말버릇, 배경 없는(투명) 버전 필요 여부

## 친구 캐릭터: 감귤 (2026-11-11 첫 시안)

- 르방 느낌(색연필·SD·점 눈·분홍 볼·삐뚤한 테두리)으로 만든 감귤 캐릭터. 피그마 `783:2` "감귤 캐릭터 ① 색연필 - 손 흔들기 (르방 친구)" — 르방 페이지(<작업중>바닷길, 마을소개(구좌))의 빈 캔버스에 둠.
- 모양: 살짝 납작한 귤 머리 = 몸만큼 큼, 주황 빗금 칠 + 진한 주황 점(귤껍질 구멍), 머리 위 갈색 꼭지 + 초록 잎 2장(르방 모자 자리), 손 흔들기 + 노란 반짝 선.
- 이름·확정 여부는 아직 안 정함. 새 포즈는 위 생성 문장에서 캐릭터 부분을 "chibi Jeju tangerine (gamgyul mandarin) ... short brown stem with two green leaves on top like a little hat, orange hatched strokes, darker orange dots for peel pores"로 바꿔 쓴다.
- 샘플 6개 (2026-11-11), 첫 시안 오른쪽에 2줄로 둠. 윗줄은 강정준비준이 "이런 느낌"이라고 준 **검은 선화 르방(`780:4`)** 스타일(색 없음, 얇은 검은 선, 네 꼭지 반짝이 별): `785:5` 귤+잎 손 흔들기 · `785:6` 한라봉 만세 · `785:7` 귤껍질 모자. 아랫줄은 색연필: `785:2` 한라봉 만세 · `785:3` 반쯤 깐 귤 · `785:4` 아기 귤 바구니. 고를 때까지 확정 아님.
