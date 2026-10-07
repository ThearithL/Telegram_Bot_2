(() => {
  const tg = window.Telegram?.WebApp;
  tg?.ready(); tg?.expand();
  const words = {
    en:{today:'YOUR DAILY SPACE',eyebrow:'A little progress, every day',title:'Make today count.',sub:'Small steps grow into strong habits.',focus:'YOUR FOCUS',habits:'Daily habits',week:'KEEP GROWING',goals:'Weekly goals',todayLabel:'today',best:'best streak',footer:'One small win is still a win. 🌿',empty:'No habits yet. Tap + to add your first one.',add:'What habit would you like to add?',added:'Habit added 🌱',done:'Nice work! Keep it growing 🌱',oops:'Could not save that. Try again.',none:'No habits yet',tasksEyebrow:'BUILD YOUR ROUTINE',allHabits:'All habits',goalHint:'Choose a target from 1 to 7 days per week. Progress covers the last seven days.',settings:'Settings',preferences:'PREFERENCES',language:'Language',languageHint:'Choose Khmer or English',reminders:'Reminders',reminderHint:'Manage reminder times in the bot menu',admin:'Admin tools',adminOnly:'ADMIN ONLY',users:'users',totalTasks:'tasks',maintenance:'Maintenance mode',maintenanceHint:'Pause normal bot actions',on:'On',off:'Off',todayTab:'Today',tasksTab:'Tasks',goalsTab:'Goals',settingsTab:'Settings',edit:'Edit habit',save:'Save',cancel:'Cancel',delete:'Delete',confirmDelete:'Delete this habit and its history?',goalPrompt:'Weekly target (1–7 days):',updated:'Updated successfully',deleted:'Habit deleted',adminError:'Admin tools are unavailable.'},
    km:{today:'ទម្លាប់ប្រចាំថ្ងៃរបស់អ្នក',eyebrow:'រីកចម្រើនបន្តិចម្តងៗរាល់ថ្ងៃ',title:'ធ្វើឱ្យថ្ងៃនេះមានន័យ។',sub:'ជំហានតូចៗ បង្កើតទម្លាប់ល្អ។',focus:'គោលដៅរបស់អ្នក',habits:'ទម្លាប់ប្រចាំថ្ងៃ',week:'បន្តរីកចម្រើន',goals:'គោលដៅប្រចាំសប្តាហ៍',todayLabel:'ថ្ងៃនេះ',best:'កំណត់ត្រាល្អបំផុត',footer:'ជោគជ័យតូចមួយ ក៏ជាជោគជ័យដែរ 🌿',empty:'មិនទាន់មានទម្លាប់ទេ។ ចុច + ដើម្បីបន្ថែម។',add:'តើអ្នកចង់បន្ថែមទម្លាប់អ្វី?',added:'បានបន្ថែមទម្លាប់ 🌱',done:'ល្អណាស់! បន្តទៅមុខទៀត 🌱',oops:'មិនអាចរក្សាទុកបានទេ។ សូមព្យាយាមម្តងទៀត។',none:'មិនទាន់មានទម្លាប់ទេ',tasksEyebrow:'បង្កើតទម្លាប់របស់អ្នក',allHabits:'ទម្លាប់ទាំងអស់',goalHint:'ជ្រើសរើសគោលដៅពី ១ ដល់ ៧ ថ្ងៃក្នុងមួយសប្តាហ៍។',settings:'ការកំណត់',preferences:'ចំណូលចិត្ត',language:'ភាសា',languageHint:'ជ្រើសរើសខ្មែរ ឬអង់គ្លេស',reminders:'ការរំលឹក',reminderHint:'គ្រប់គ្រងម៉ោងរំលឹកក្នុងម៉ឺនុយ Bot',admin:'ឧបករណ៍ Admin',adminOnly:'សម្រាប់ Admin',users:'អ្នកប្រើ',totalTasks:'ទម្លាប់',maintenance:'របៀបថែទាំ',maintenanceHint:'ផ្អាកសកម្មភាពធម្មតារបស់ Bot',on:'បើក',off:'បិទ',todayTab:'ថ្ងៃនេះ',tasksTab:'ទម្លាប់',goalsTab:'គោលដៅ',settingsTab:'ការកំណត់',edit:'កែទម្លាប់',save:'រក្សាទុក',cancel:'បោះបង់',delete:'លុប',confirmDelete:'លុបទម្លាប់ និងប្រវត្តិរបស់វា?',goalPrompt:'គោលដៅប្រចាំសប្តាហ៍ (១–៧ ថ្ងៃ):',updated:'បានកែប្រែរួចរាល់',deleted:'បានលុបទម្លាប់',adminError:'មិនអាចបើកឧបករណ៍ Admin បានទេ។'}
  };
  let lang='en', tasks=[], initData=tg?.initData||'';
  let isAdmin=false, editingTask=null, activeTab='today';
  const $=id=>document.getElementById(id);
  const toast=(s)=>{const el=$('toast');el.textContent=s;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2200)};
  async function api(path, body){
    const res=await fetch(path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json','X-Telegram-Init-Data':initData},body:body?JSON.stringify(body):undefined});
    const data=await res.json();if(!res.ok)throw new Error(data.error||'Request failed');return data;
  }
  function text(){const w=words[lang];$('todayLabel').textContent=w.today;$('heroEyebrow').textContent=w.eyebrow;$('heroTitle').textContent=w.title;$('heroSub').textContent=w.sub;$('focusLabel').textContent=w.focus;$('habitsTitle').textContent=w.habits;$('tasksEyebrow').textContent=w.tasksEyebrow;$('tasksHeading').textContent=w.allHabits;$('weekLabel').textContent=w.week;$('weekTitle').textContent=w.goals;$('goalHint').textContent=w.goalHint;$('settingsHeading').textContent=w.settings;$('settingsEyebrow').textContent=w.preferences;$('languageName').textContent=w.language;$('languageHint').textContent=w.languageHint;$('reminderName').textContent=w.reminders;$('reminderHint').textContent=w.reminderHint;$('adminEyebrow').textContent=w.adminOnly;$('adminHeading').textContent=w.admin;$('usersLabel').textContent=w.users;$('totalTasksLabel').textContent=w.totalTasks;$('maintenanceName').textContent=w.maintenance;$('maintenanceHint').textContent=w.maintenanceHint;$('navToday').textContent=w.todayTab;$('navTasks').textContent=w.tasksTab;$('navGoals').textContent=w.goalsTab;$('navSettings').textContent=w.settingsTab;$('dialogTitle').textContent=w.edit;$('saveEdit').textContent=w.save;$('cancelEdit').textContent=w.cancel;$('deleteBtn').textContent=w.delete;$('todayProgressLabel').textContent=w.todayLabel;$('streakLabel').textContent=w.best;$('footerText').textContent=w.footer;$('langBtn').textContent=lang==='en'?'ខ្មែរ':'English';$('langSetting').textContent=lang==='en'?'English':'ខ្មែរ';document.documentElement.lang=lang;}
  function render(){
    const list=$('taskList'), all=$('allTaskList'), goals=$('goalList'); list.innerHTML='';all.innerHTML='';goals.innerHTML='';
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
      const allRow=row.cloneNode(true);allRow.querySelector('.check').onclick=()=>toggle(task);const actions=document.createElement('button');actions.className='more';actions.textContent='•••';actions.setAttribute('aria-label','Edit habit');actions.onclick=()=>openEdit(task);allRow.append(actions);all.append(allRow);
      const grow=document.createElement('div');grow.className='goal-row';
      const gname=document.createElement('span');gname.className='goal-name';gname.textContent=task.name;
      const count=document.createElement('span');count.className='goal-count';count.textContent=`${task.week_done||0}/${task.goal||7}`;
      const bar=document.createElement('div');bar.className='bar';const fill=document.createElement('i');fill.style.width=`${Math.min(100,(task.week_done||0)/(task.goal||7)*100)}%`;bar.append(fill);grow.append(gname,count,bar);
      const goalAction=document.createElement('button');goalAction.className='goal-action';goalAction.textContent=`＋ / －`;
      goalAction.onclick=async()=>{const value=window.prompt(words[lang].goalPrompt,String(task.goal||7));if(value===null)return;try{const goal=Math.max(1,Math.min(7,parseInt(value,10)));if(!Number.isInteger(goal))throw Error('');await request(`/api/miniapp/goal/${task.id}`,'POST',{goal});await load();}catch(e){toast(e.message||words[lang].oops);}};
      grow.append(goalAction);goals.append(grow);
    }
  }
  async function load(){try{const data=await api('/api/miniapp/data');tasks=data.tasks;lang=data.language||'en';isAdmin=!!data.is_admin;text();render();if(isAdmin)loadAdmin();}catch(e){$('taskList').innerHTML=`<div class="empty">🔒 ${e.message}</div>`;}}
  async function toggle(task){try{const data=await api('/api/miniapp/toggle',{task_id:task.id});task.done=data.done;task.week_done=Math.max(0,(task.week_done||0)+(data.done?1:-1));if(data.badges?.length)data.badges.forEach(toast);else if(data.done)toast(words[lang].done);render();}catch(e){toast(words[lang].oops);}}
  $('addBtn').onclick=async()=>{const name=window.prompt(words[lang].add);if(!name?.trim())return;try{await api('/api/miniapp/task',{name:name.trim()});toast(words[lang].added);await load();}catch(e){toast(e.message||words[lang].oops);}};
  $('langBtn').onclick=async()=>{const next=lang==='en'?'km':'en';try{await api('/api/miniapp/language',{language:next});lang=next;text();render();}catch(e){toast(words[lang].oops);}};
  async function addTask(){const name=window.prompt(words[lang].add);if(!name?.trim())return;try{await api('/api/miniapp/task',{name:name.trim()});toast(words[lang].added);await load();}catch(e){toast(e.message||words[lang].oops);}}
  $('addBtn').onclick=addTask;$('addBtn2').onclick=addTask;
  function openEdit(task){editingTask=task;$('editInput').value=task.name;$('editDialog').hidden=false;setTimeout(()=>$('editInput').focus(),50);}
  $('cancelEdit').onclick=()=>{$('editDialog').hidden=true;editingTask=null;};
  $('saveEdit').onclick=async()=>{if(!editingTask)return;try{await request(`/api/miniapp/task/${editingTask.id}`,'PATCH',{name:$('editInput').value.trim()});toast(words[lang].updated);$('editDialog').hidden=true;await load();}catch(e){toast(e.message||words[lang].oops);}};
  $('deleteBtn').onclick=async()=>{if(!editingTask||!window.confirm(words[lang].confirmDelete))return;try{await request(`/api/miniapp/task/${editingTask.id}`,'DELETE');toast(words[lang].deleted);$('editDialog').hidden=true;await load();}catch(e){toast(e.message||words[lang].oops);}};
  async function request(path,method,body){const res=await fetch(path,{method,headers:{'Content-Type':'application/json','X-Telegram-Init-Data':initData},body:body?JSON.stringify(body):undefined});const data=await res.json();if(!res.ok)throw new Error(data.error||'Request failed');return data;}
  async function loadAdmin(){try{const data=await api('/api/miniapp/admin');$('adminPanel').hidden=false;$('adminUsers').textContent=data.users;$('adminTasks').textContent=data.tasks;$('maintenanceToggle').textContent=data.maintenance?words[lang].on:words[lang].off;$('maintenanceToggle').classList.toggle('danger',data.maintenance);}catch(_){$('adminPanel').hidden=true;}}
  $('maintenanceToggle').onclick=async()=>{try{const data=await api('/api/miniapp/admin',{maintenance:$('maintenanceToggle').textContent!==words[lang].on});$('maintenanceToggle').textContent=data.maintenance?words[lang].on:words[lang].off;toast(words[lang].updated);}catch(e){toast(words[lang].adminError);}};
  document.querySelectorAll('.nav-item').forEach(btn=>btn.onclick=()=>{activeTab=btn.dataset.tab;document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));$(`screen-${activeTab}`).classList.add('active');document.querySelectorAll('.nav-item').forEach(n=>n.classList.toggle('active',n===btn));if(activeTab==='settings'&&isAdmin)loadAdmin();window.scrollTo({top:0,behavior:'smooth'});});
  $('langSetting').onclick=$('langBtn').onclick;
  text(); if(!initData){$('taskList').innerHTML=`<div class="empty">Open this page from the Telegram bot using its Mini App button.</div>`;}else load();
})();
