$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$utf8 = [System.Text.UTF8Encoding]::new($false)
function Save($file, $content) { [IO.File]::WriteAllText((Join-Path $root $file), $content, $utf8) }
function Enc($text) { [System.Net.WebUtility]::HtmlEncode($text) }
function Url($text) { (($text -split '/') | ForEach-Object { [Uri]::EscapeDataString($_) }) -join '/' }
$css = @'
:root{--ink:#152940;--muted:#4b6175;--paper:#f3f6fa;--line:#d5dfe8;--green:#08765c}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.6 'Segoe UI',Arial,sans-serif}a{color:#194db5}a:focus-visible{outline:3px solid #d88600;outline-offset:5px}header{background:var(--ink);color:white;padding:20px max(24px,calc((100vw - 1200px)/2));display:flex;justify-content:space-between;align-items:center;gap:20px}header a{color:white;text-decoration:none}.brand{display:flex;align-items:center;gap:13px;font-weight:700}.mark{background:#62e3c0;color:var(--ink);padding:4px 10px;border-radius:8px}.small{font-size:14px;color:var(--muted)}header .small{color:#c7d7e9}.layout{max-width:1200px;margin:36px auto;padding:0 24px;display:grid;grid-template-columns:220px minmax(0,1fr);gap:38px}aside nav{display:grid;gap:8px;margin:18px 0}aside a{padding:10px 14px;border-radius:12px;text-decoration:none;color:var(--ink);font-size:16px}aside a:hover,aside a[aria-current=page]{background:#d9e9e4}.eyebrow{font-size:14px;font-weight:750;letter-spacing:.1em;text-transform:uppercase;color:var(--green)}h1{font-size:clamp(32px,4.2vw,48px);line-height:1.13;letter-spacing:-.035em;margin:13px 0 20px}h2{font-size:25px;line-height:1.25;margin:0 0 14px}p{margin:0 0 16px}.lead{font-size:20px;color:var(--muted)}.hero{background:#edf6f3;border:1px solid #c9dfd7;border-radius:22px;padding:28px;margin-bottom:24px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.card{background:white;border:1px solid var(--line);border-radius:20px;padding:24px;display:flex;flex-direction:column;align-items:start}.card:nth-child(3n+2){background:#edf4f8}.card:nth-child(3n+3){background:#f3f0f8}.card p{color:var(--muted)}.tag{font-size:14px;padding:3px 10px;background:#e7edf6;border-radius:7px;font-weight:600;margin-bottom:16px}.button{display:inline-block;padding:10px 16px;background:var(--ink);color:white;border-radius:12px;text-decoration:none;font-weight:600;margin-top:auto}.button:hover{background:#2b4868}.lessons{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.breadcrumb{font-size:14px;margin-bottom:20px}footer{font-size:14px;color:var(--muted);border-top:1px solid var(--line);padding:20px 0;margin-top:32px}.skip{position:absolute;left:16px;top:-80px;background:white;padding:10px}.skip:focus{top:10px}@media(max-width:800px){header{padding:16px 20px}header>.small{display:none}.layout{grid-template-columns:1fr;gap:12px;margin-top:20px;padding:0 16px}aside nav{display:flex;flex-wrap:wrap;margin:0 0 12px}aside>.eyebrow,aside>.small{display:none}.grid,.lessons{grid-template-columns:1fr}.hero,.card{padding:22px}h1{font-size:34px}}
'@
New-Item -ItemType Directory -Force (Join-Path $root 'assets') | Out-Null
Save 'assets/site.css' $css
function Page($title,$prefix,$active,$body){
 $nav = '<a href="'+$prefix+'index.html"'+$(if($active -eq 0){' aria-current="page"'})+'>Усі класи</a>'
 foreach($g in 5..7){$nav += '<a href="'+$prefix+(Url "$g клас")+'/index.html"'+$(if($active -eq $g){' aria-current="page"'})+">$g клас</a>"}
 return '<!doctype html><html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+(Enc $title)+' · Лабораторія робототехніки</title><meta name="description" content="Інтерактивні уроки робототехніки для 5–7 класів: досліджуй, програмуй та перевіряй знання."><link rel="stylesheet" href="'+$prefix+'assets/site.css"></head><body><a class="skip" href="#main">До вмісту</a><header><a class="brand" href="'+$prefix+'index.html"><span class="mark" aria-hidden="true">R/</span>Лабораторія робототехніки</a><span class="small">Досліджуй · Створюй · Перевіряй</span></header><div class="layout"><aside><div class="eyebrow">Твій маршрут</div><nav aria-label="Класи">'+$nav+'</nav><p class="small">Обери клас і тему.<br>Навчайся у своєму темпі.</p></aside><main id="main">'+$body+'<footer>Лабораторія робототехніки · 5–7 класи</footer></main></div></body></html>'
}
$gradeCards = ''
$total = 0
foreach($g in 5..7){
 $files = @(Get-ChildItem -LiteralPath (Join-Path $root "$g клас/Робототехніка") -Recurse -Filter '*.html' | Sort-Object FullName)
 $total += $files.Count
 $cards = ''
 for($i=0;$i -lt $files.Count;$i++){
  $file = $files[$i]
  $html = [IO.File]::ReadAllText($file.FullName)
  $title = $file.BaseName -replace '^Урок \d+ — ',''
  $description = [regex]::Match($html,'<meta name="description" content="([^"]*)"').Groups[1].Value
  $relative = $file.FullName.Substring((Join-Path $root "$g клас").Length+1).Replace('\','/')
  $cards += '<article class="card"><span class="tag">Урок '+($i+1).ToString('00')+'</span><h2>'+(Enc $title)+'</h2><p>'+ $description +'</p><a class="button" href="'+(Url $relative)+'">Відкрити урок →</a>'+'</article>'
  $lessonNav = '<div id="site-navigation" style="max-width:1200px;margin:16px auto;padding:0 24px;display:flex;flex-wrap:wrap;gap:16px;font:14px/1.6 Segoe UI,Arial,sans-serif" role="navigation" aria-label="Навігація між уроками"><a href="../../../index.html">Усі класи</a><a href="../../index.html">'+$g+' клас · Усі уроки</a>'
  if($i -gt 0){$lessonNav += '<a href="../'+(Url ($files[$i-1].Directory.Name+'/'+$files[$i-1].Name))+'">← Попередній урок</a>'}
  if($i -lt $files.Count-1){$lessonNav += '<a href="../'+(Url ($files[$i+1].Directory.Name+'/'+$files[$i+1].Name))+'">Наступний урок →</a>'}
  $lessonNav += '</div>'
  $html = [regex]::Replace($html,'<div id="site-navigation".*?</div>','',[Text.RegularExpressions.RegexOptions]::Singleline)
  $html = $html.Replace('</header>','</header>'+$lessonNav)
  [IO.File]::WriteAllText($file.FullName,$html,$utf8)
 }
 $body = '<div class="breadcrumb"><a href="../index.html">Усі класи</a> / '+$g+' клас</div><section class="hero"><div class="eyebrow">Робототехніка · '+$files.Count+' уроки</div><h1>'+$g+' клас</h1><p class="lead">Обери тему та почни дослідження. Кожен урок містить пояснення, інтерактивні вправи й перевірку знань.</p></section><div class="lessons">'+$cards+'</div>'
 Save "$g клас/index.html" (Page "$g клас" '../' $g $body)
 $topics = ($files | ForEach-Object {$_.BaseName -replace '^Урок \d+ — ',''}) -join ' · '
 $gradeCards += '<article class="card"><span class="tag">'+$files.Count+' уроки</span><h2>'+$g+' клас</h2><p>'+(Enc $topics)+'</p><a class="button" href="'+(Url "$g клас")+'/index.html">Обрати урок →</a></article>'
}
$body = '<section class="hero"><div class="eyebrow">Інтерактивні уроки · 5–7 класи</div><h1>Від першої ідеї<br>до власного проєкту</h1><p class="lead">Досліджуй можливості micro:bit, створюй алгоритми та експериментуй. Обери свій клас — і вирушай до лабораторії.</p><span class="tag">3 класи · '+$total+' уроків</span></section><div class="grid">'+$gradeCards+'</div><section class="hero" style="margin-top:24px"><h2>Як працювати з уроками</h2><p>Обери клас і тему. Рухайся етапами уроку, виконуй досліди та проходь квіз. Якщо урок пропонує зберегти результат, завантаж його перед закриттям сторінки.</p><p class="small">Для інтерактивних вправ увімкни JavaScript у браузері.</p></section>'
Save 'index.html' (Page 'Усі класи' '' 0 $body)
Save '.nojekyll' ''
Write-Output "Generated homepage, 3 grade indexes and navigation for $total lessons."
