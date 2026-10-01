'use strict';
const audios=[...document.querySelectorAll('audio')];
audios.forEach(audio=>{
 audio.addEventListener('play',()=>audios.forEach(other=>{if(other!==audio)other.pause()}));
 audio.addEventListener('error',()=>{const status=audio.parentElement.querySelector('.audio-status');if(status)status.textContent='Не вдалося відкрити аудіо. Спробуй завантажити запис або оновити сторінку.'});
});
const search=document.getElementById('podcast-search'),grade=document.getElementById('podcast-grade');
if(search&&grade){
 const cards=[...document.querySelectorAll('.podcast-card')];
 const filter=()=>{let count=0;cards.forEach(card=>{const visible=(!grade.value||card.dataset.grade===grade.value)&&card.textContent.toLocaleLowerCase('uk').includes(search.value.trim().toLocaleLowerCase('uk'));card.hidden=!visible;if(visible)count++;else card.querySelector('audio').pause()});document.getElementById('podcast-count').textContent='Знайдено: '+count;document.getElementById('podcast-empty').hidden=count!==0};
 search.addEventListener('input',filter);grade.addEventListener('change',filter);filter();
}
const player=document.getElementById('podcast-audio'),lines=[...document.querySelectorAll('.utterance')];
if(player){
 document.querySelectorAll('[data-time]').forEach(button=>button.addEventListener('click',async()=>{
  try{player.currentTime=Number(button.dataset.time);await player.play()}catch(error){document.querySelector('.audio-status').textContent='Натисни кнопку відтворення у плеєрі, щоб почати слухати.'}
 }));
 player.addEventListener('timeupdate',()=>{let current=null;for(const line of lines){if(Number(line.dataset.start)<=player.currentTime)current=line;else break}lines.forEach(line=>line.classList.toggle('current',line===current))});
 const textSearch=document.getElementById('transcript-search');
 if(textSearch)textSearch.addEventListener('input',()=>{let count=0;const query=textSearch.value.trim().toLocaleLowerCase('uk');lines.forEach(line=>{line.hidden=!line.textContent.toLocaleLowerCase('uk').includes(query);if(!line.hidden)count++});document.getElementById('transcript-status').textContent='Реплік: '+count});
}
