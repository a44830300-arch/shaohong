#!/usr/bin/env bash
# 매일 날씨지도용(제주라이브, 2026-11-15부터 3구역): 기상청에서 3곳 × 4일(오늘~3일 뒤) 값을 뽑아 JSON으로 출력한다.
#   북 = 제주시 (동네예보 5011000000) / 남 = 서귀포시 (동네예보 5013000000) / 산 = 한라산 (산악날씨 mtId 11G001P1)
# 사용: bash .claude/skills/weather-calendar/kma_4days.sh  (Git Bash, perl 사용 — 파이썬 필요 없음)
# 출력: {"dates":["2026-11-15",...],"북":[[날짜숫자,아이콘,최저,최고,강수%],...],"남":[...],"산":[...]}
# 아이콘 규칙(위에서부터): 비·소나기·눈·빗방울 → rain / 흐림 → cloudy / 구름많음 → partly / 맑음 → sun
#   동네예보 = 오전·오후 중 하나라도. 한라산(시간별만 있음) = 그날 09~18시 중 하나라도. 기온은 시간별 최저·최고, 강수확률은 그날 가장 높은 값.
set -e
TMP="${TMPDIR:-${TEMP:-/tmp}}/kma4_$$"; mkdir -p "$TMP"
UA="Mozilla/5.0"
curl -s -A "$UA" "https://www.weather.go.kr/w/wnuri-fct2021/main/digital-forecast.do?code=5011000000&unit=m%2Fs&hr1=Y" -o "$TMP/북.html"
curl -s -A "$UA" "https://www.weather.go.kr/w/wnuri-fct2021/main/digital-forecast.do?code=5013000000&unit=m%2Fs&hr1=Y" -o "$TMP/남.html"
curl -s -A "$UA" "https://www.weather.go.kr/w/wnuri-fct2021/theme/mountains-forecast.do?mtId=11G001P1&hr1=Y&unit=m%2Fs" -o "$TMP/산.html"
perl -CSD -e '
  use utf8; my $dir=shift; my (%out,@dates);
  sub icon { my $w=shift; return $w=~/비|소나기|눈|빗방울/ ? "rain" : $w=~/흐림/ ? "cloudy" : $w=~/구름많음/ ? "partly" : $w=~/맑음/ ? "sun" : "--"; }
  sub slurp { open my $fh,"<:encoding(UTF-8)",shift or die; local $/; <$fh> }
  for my $k ("북","남"){
    my $h=slurp("$dir/$k.html"); my @rows;
    while($h =~ /data-date="(\d{4}-\d\d-\d\d)"(.*?)daily-pop-pm.*?<span>([^<]*)<\/span>/sg){
      my ($d,$blk,$ppm)=($1,$2,$3);
      my ($wam)=$blk=~/daily-weather-am.*?<div>(.*?)<\/div>\s*<\/div>/s;
      my ($wpm)=$blk=~/daily-weather-pm.*?<div>(.*?)<\/div>\s*<\/div>/s;
      my ($tmin)=$blk=~/최저 : <\/strong><span>(-?\d+)/; my ($tmax)=$blk=~/최고 : <\/strong><span>(-?\d+)/;
      my ($pam)=$blk=~/daily-pop-am.*?<span>([^<]*)<\/span>/s;
      my $w=($wam//"")." ".($wpm//""); $w=~s/<[^>]*title="[^"]*"[^>]*>//g; $w=~s/<[^>]*>//g;
      my @p = grep { /^\d+$/ } map { (my $x=$_)=~s/%//; $x } ($pam//"-",$ppm//"-");
      push @rows,[$d,icon($w),$tmin//"--",$tmax//"--",@p ? (sort {$b<=>$a} @p)[0]."%" : "--"];
      last if @rows==4;
    }
    @dates = map {$_->[0]} @rows unless @dates;
    $out{$k}=\@rows;
  }
  { # 한라산: 시간별 칸을 날짜별로 모은다
    my $h=slurp("$dir/산.html"); my (%t,%w,%wa,%p,%seen);
    while($h =~ /<ul class="item[^"]*" data-date="(\d{4}-\d\d-\d\d)" data-time="(\d\d):\d\d">(.*?)<\/ul>/sg){
      my ($d,$hr,$b)=($1,$2+0,$3); next if $seen{"$d $hr"}++;
      my ($wt)=$b=~/class="wic[^"]*" title="([^"]*)"/; my ($tc)=$b=~/feel">(-?\d+)/; my ($pp)=$b=~/강수확률: <\/span><span>(\d+)%/;
      push @{$t{$d}},$tc if defined $tc; push @{$p{$d}},$pp if defined $pp;
      $w{$d}.=" ".($wt//"") if $hr>=9 && $hr<=18; $wa{$d}.=" ".($wt//"");
    }
    my @rows;
    for my $d (@dates){
      my @tt=sort {$a<=>$b} @{$t{$d}||[]}; my @pp=sort {$b<=>$a} @{$p{$d}||[]};
      my $ww = ($w{$d}//"") =~ /\S/ ? $w{$d} : ($wa{$d}//"");  # 9~18시가 지났으면 남은 시간으로
      push @rows,[$d, icon($ww), @tt ? $tt[0] : "--", @tt ? $tt[-1] : "--", @pp ? $pp[0]."%" : "--"];
    }
    $out{"산"}=\@rows;
  }
  print "{\"dates\":[".join(",",map{"\"$_\""}@dates)."]";
  for my $k ("북","남","산"){ print ",\"$k\":[".join(",", map { my ($d)=$_->[0]=~/-(\d\d)$/; $d+=0; "[\"$d\",\"$_->[1]\",\"$_->[2]\",\"$_->[3]\",\"$_->[4]\"]" } @{$out{$k}})."]"; }
  print "}\n";
' "$TMP"
rm -rf "$TMP"
