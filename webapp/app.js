(() => {
  const tg = window.Telegram?.WebApp;
  tg?.ready(); tg?.expand();
  const words = {
    en:{today:'YOUR DAILY SPACE',eyebrow:'A little progress, every day',title:'Make today count.',sub:'Small steps grow into strong habits.',focus:'YOUR FOCUS',habits:'Daily habits',week:'KEEP GROWING',goals:'Weekly goals',todayLabel:'today',best:'best streak',footer:'One small win is still a win. 🌿',empty:'No habits yet. Tap + to add your first one.',add:'What habit would you like to add?',added:'Habit added 🌱',done:'Nice work! Keep it growing 🌱',oops:'Could not save that. Try again.',none:'No habits yet'},
    km:{today:'ទម្លាប់ប្រចាំថ្ងៃរបស់អ្នក',eyebrow:'រីកចម្រើនបន្តិចម្តងៗរាល់ថ្ងៃ',title:'ធ្វើឱ្យថ្ងៃនេះមានន័យ។',sub:'ជំហានតូចៗ បង្កើតទម្លាប់ល្អ។',focus:'គោលដៅរបស់អ្នក',habits:'ទម្លាប់ប្រចាំថ្ងៃ',week:'បន្តរីកចម្រើន',goals:'គោលដៅប្រចាំសប្តាហ៍',todayLabel:'ថ្ងៃនេះ',best:'កំណត់ត្រាល្អបំផុត',footer:'ជោគជ័យតូចមួយ ក៏ជាជោគជ័យដែរ 🌿',empty:'មិនទាន់មានទម្លាប់ទេ។ ចុច + ដើម្បីបន្ថែម។',add:'តើអ្នកចង់បន្ថែមទម្លាប់អ្វី?',added:'បានបន្ថែមទម្លាប់ 🌱',done:'ល្អណាស់! បន្តទៅមុខទៀត 🌱',oops:'មិនអាចរក្សាទុកបានទេ។ សូមព្យាយាមម្តងទៀត។',none:'មិនទាន់មានទម្លាប់ទេ'}
  };
  let lang='en', tasks=[], initData=tg?.initData||'';
  const $=id=>document.getElementById(id);
  const toast=(s)=>{const el=$('toast');el.textContent=s;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2200)};
  async function api(path, body){
    const res=await fetch(path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json','X-Telegram-Init-Data':initData},body:body?JSON.stringify(body):undefined});
    const data=await res.json();if(!res.ok)throw new Error(data.error||'Request failed');return data;
  }
  function text(){const w=words[lang];$('todayLabel').textContent=w.today;$('heroEyebrow').textContent=w.eyebrow;$('heroTitle').textContent=w.title;$('heroSub').textContent=w.sub;$('focusLabel').textContent=w.focus;$('habitsTitle').textContent=w.habits;$('weekLabel').textContent=w.week;$('weekTitle').textContent=w.goals;$('todayProgressLabel').textContent=w.todayLabel;$('streakLabel').textContent=w.best;$('footerText').textContent=w.footer;$('langBtn').textContent=lang==='en'?'ខ្មែរ':'English';document.documentElement.lang=lang;}
  function render(){
    const list=$('taskList'), goals=$('goalList'); list.innerHTML='';goals.innerHTML='';
    if(!tasks.length){list.innerHTML=`<div class="empty">🌿 ${words[lang].empty}</div>`;}
    let done=tasks.filter(x=>x.done).length;
    $('doneCount').textContent=`${done}/${tasks.length}`;
    $('streakCount').textContent=tasks.reduce((n,x)=>Math.max(n,x.best||0),0);
    for(const task of tasks){
      const row=document.createElement('article');row.className='task'+(task.done?' done':'');
      const btn=document.createElement('button');btn.className='check';btn.textContent=task.done?'✓':'';btn.setAttribute('aria-label',task.done?'Mark not done':'Mark done');
      btn.onclick=()=>toggle(task);
      const info=document.createElement('div');info.className='task-info';
      const name=document.createElement('div');name.className='task-name';name.textContent=task.name;
      const meta=document.createElement('div');meta.className='task-meta';meta.textContent=`${task.week_done||0} / ${task.goal||7} this week`;
      info.append(name,meta);
      const streak=document.createElement('span');streak.className='task-streak';streak.textContent=`🔥 ${task.streak||0}`;
      row.append(btn,info,streak);list.append(row);
      const grow=document.createElement('div');grow.className='goal-row';
      const gname=document.createElement('span');gname.className='goal-name';gname.textContent=task.name;
      const count=document.createElement('span');count.className='goal-count';count.textContent=`${task.week_done||0}/${task.goal||7}`;
      const bar=document.createElement('div');bar.className='bar';const fill=document.createElement('i');fill.style.width=`${Math.min(100,(task.week_done||0)/(task.goal||7)*100)}%`;bar.append(fill);grow.append(gname,count,bar);goals.append(grow);
    }
  }
  async function load(){try{const data=await api('/api/miniapp/data');tasks=data.tasks;lang=data.language||'en';text();render();}catch(e){$('taskList').innerHTML=`<div class="empty">🔒 ${e.message}</div>`;}}
  async function toggle(task){try{const data=await api('/api/miniapp/toggle',{task_id:task.id});task.done=data.done;task.week_done=Math.max(0,(task.week_done||0)+(data.done?1:-1));if(data.badges?.length)data.badges.forEach(toast);else if(data.done)toast(words[lang].done);render();}catch(e){toast(words[lang].oops);}}
  $('addBtn').onclick=async()=>{const name=window.prompt(words[lang].add);if(!name?.trim())return;try{await api('/api/miniapp/task',{name:name.trim()});toast(words[lang].added);await load();}catch(e){toast(e.message||words[lang].oops);}};
  $('langBtn').onclick=async()=>{const next=lang==='en'?'km':'en';try{await api('/api/miniapp/language',{language:next});lang=next;text();render();}catch(e){toast(words[lang].oops);}};
  text(); if(!initData){$('taskList').innerHTML=`<div class="empty">Open this page from the Telegram bot using its Mini App button.</div>`;}else load();
})();
