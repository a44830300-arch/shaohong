#!/usr/bin/env bash
# 매일 날씨지도용: 기상청 동네예보에서 4구역 × 4일(오늘~3일 뒤) 값을 뽑아 JSON으로 출력한다.
# 사용: bash .claude/skills/weather-calendar/kma_4days.sh  (Git Bash, perl 사용 — 파이썬 필요 없음)
# 출력: {"dates":["2026-11-15",...],"북":[[날짜숫자,아이콘,최저,최고,강수%],...],...}
# 아이콘 규칙(오전·오후 중 하나라도, 위에서부터): 비·소나기·눈·빗방울 → rain / 흐림 → cloudy / 구름많음 → partly / 맑음 → sun
set -e
TMP="${TMPDIR:-/tmp}/kma4_$$"; mkdir -p "$TMP"
declare -A CODES=( [북]=5011000000 [서]=5011025000 [동]=5013025900 [남]=5013000000 )
for k in 북 서 동 남; do
  curl -s "https://www.weather.go.kr/w/wnuri-fct2021/main/digital-forecast.do?code=${CODES[$k]}&unit=m%2Fs&hr1=Y" -o "$TMP/$k.html"
done
perl -CSD -e '
  use utf8; my $dir=shift; my @keys=("북","서","동","남"); my (%out,@dates);
  for my $k (@keys){
    open my $fh,"<:encoding(UTF-8)","$dir/$k.html" or die; local $/; my $h=<$fh>;
    my @rows;
    while($h =~ /data-date="(\d{4}-\d\d-\d\d)"(.*?)daily-pop-pm.*?<span>([^<]*)<\/span>/sg){
      my ($d,$blk,$ppm)=($1,$2,$3);
      my ($wam)=$blk=~/daily-weather-am.*?<div>(.*?)<\/div>\s*<\/div>/s;
      my ($wpm)=$blk=~/daily-weather-pm.*?<div>(.*?)<\/div>\s*<\/div>/s;
      my ($tmin)=$blk=~/최저 : <\/strong><span>(-?\d+)/; my ($tmax)=$blk=~/최고 : <\/strong><span>(-?\d+)/;
      my ($pam)=$blk=~/daily-pop-am.*?<span>([^<]*)<\/span>/s;
      my $w=($wam//"")." ".($wpm//""); $w=~s/<[^>]*title="[^"]*"[^>]*>//g; $w=~s/<[^>]*>//g;
      my $icon = $w=~/비|소나기|눈|빗방울/ ? "rain" : $w=~/흐림/ ? "cloudy" : $w=~/구름많음/ ? "partly" : $w=~/맑음/ ? "sun" : "--";
      my @p = grep { /^\d+$/ } map { (my $x=$_)=~s/%//; $x } ($pam//"-",$ppm//"-");
      my $pop = @p ? (sort {$b<=>$a} @p)[0]."%" : "--";
      push @rows,[$d,$icon,$tmin//"--",$tmax//"--",$pop];
      last if @rows==4;
    }
    @dates = map {$_->[0]} @rows unless @dates;
    $out{$k} = join(",", map { my ($d)=$_->[0]=~/-(\d\d)$/; $d+=0; "[\"$d\",\"$_->[1]\",\"$_->[2]\",\"$_->[3]\",\"$_->[4]\"]" } @rows);
  }
  print "{\"dates\":[".join(",",map{"\"$_\""}@dates)."]";
  print ",\"$_\":[$out{$_}]" for @keys; print "}\n";
' "$TMP"
rm -rf "$TMP"
