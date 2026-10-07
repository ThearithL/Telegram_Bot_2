(() => {
  'use strict';

  const tg = window.Telegram?.WebApp;
  tg?.ready();
  tg?.expand();

  const copy = {
    en: {
      today:'YOUR DAILY SPACE', eyebrow:'A little progress, every day', title:'Make today count.',
      sub:'Small steps grow into strong habits.', focus:'YOUR FOCUS', habits:'Daily habits',
      week:'KEEP GROWING', goals:'Weekly goals', todayLabel:'today', best:'best streak',
      footer:'One small win is still a win. 🌿', empty:'No habits yet. Add your first one to get started.',
      add:'Add a habit', edit:'Edit habit', habitName:'Habit name', added:'Habit added 🌱',
      done:'Nice work! Keep it growing 🌱', updated:'Saved successfully.', deleted:'Habit deleted.',
      save:'Save habit', addAction:'Add habit', cancel:'Cancel', delete:'Delete',
      confirmDelete:'Delete this habit and all its history?', invalidName:'Enter a habit name (1–80 characters).',
      duplicate:'You already have a habit with that name.', oops:'Could not save that. Please try again.',
      tasksEyebrow:'BUILD YOUR ROUTINE', allHabits:'All habits', goalHint:'Set how many days each week you want to do a habit.',
      settings:'Settings', preferences:'PREFERENCES', language:'Language', languageHint:'Choose Khmer or English',
      reminders:'Reminders', reminderHint:'Change reminder times from the bot menu → More.',
      admin:'Admin tools', adminOnly:'ADMIN ONLY', users:'users', totalTasks:'habits',
      maintenance:'Maintenance mode', maintenanceHint:'Pause bot actions for regular users', on:'On', off:'Off',
      todayTab:'Today', tasksTab:'Habits', goalsTab:'Goals', settingsTab:'Settings',
      welcome:'Welcome to your daily space.', welcomeSub:'A simple place to build habits and keep your routine moving.', menuEyebrow:'YOUR SPACE', menuTitle:'Choose where to go', menuHome:'Home', menuToday:'Today', menuTodaySub:'Check off today’s habits', menuTasks:'My habits', menuTasksSub:'Build your daily routine', menuGoals:'Weekly goals', menuGoalsSub:'See your progress this week', menuSettings:'Settings', menuSettingsSub:'Language and preferences', doneToday:'done today',
      menuCalendar:'Khmer Calendar', menuCalendarSub:'Open the trusted source', menuAdd:'Add a habit',
      goalDays:'days/week', auth:'Open this app from your Telegram bot.', serviceError:'Could not load your habits. Try reopening the app.',
      adminError:'Admin tools are unavailable.', close:'Close', loading:'Loading your habits…'
    },
    km: {
      today:'ទម្លាប់ប្រចាំថ្ងៃរបស់អ្នក', eyebrow:'រីកចម្រើនបន្តិចម្តងៗរាល់ថ្ងៃ',
      title:'ធ្វើឱ្យថ្ងៃនេះមានន័យ។', sub:'ជំហានតូចៗ បង្កើតទម្លាប់ល្អ។', focus:'គោលដៅរបស់អ្នក',
      habits:'ទម្លាប់ប្រចាំថ្ងៃ', week:'បន្តរីកចម្រើន', goals:'គោលដៅប្រចាំសប្តាហ៍',
      todayLabel:'ថ្ងៃនេះ', best:'កំណត់ត្រាល្អបំផុត', footer:'ជោគជ័យតូចមួយ ក៏ជាជោគជ័យដែរ 🌿',
      empty:'មិនទាន់មានទម្លាប់ទេ។ បន្ថែមទម្លាប់ដំបូងរបស់អ្នក។', add:'បន្ថែមទម្លាប់', edit:'កែទម្លាប់',
      habitName:'ឈ្មោះទម្លាប់', added:'បានបន្ថែមទម្លាប់ 🌱', done:'ល្អណាស់! បន្តទៅមុខទៀត 🌱',
      updated:'បានរក្សាទុករួចរាល់។', deleted:'បានលុបទម្លាប់។', save:'រក្សាទុកទម្លាប់',
      addAction:'បន្ថែមទម្លាប់', cancel:'បោះបង់', delete:'លុប',
      confirmDelete:'លុបទម្លាប់ និងប្រវត្តិរបស់វាមែនទេ?', invalidName:'សូមបញ្ចូលឈ្មោះទម្លាប់ (១–៨០ តួអក្សរ)។',
      duplicate:'មានទម្លាប់ឈ្មោះនេះរួចហើយ។', oops:'មិនអាចរក្សាទុកបានទេ។ សូមព្យាយាមម្តងទៀត។',
      tasksEyebrow:'បង្កើតទម្លាប់របស់អ្នក', allHabits:'ទម្លាប់ទាំងអស់',
      goalHint:'កំណត់ចំនួនថ្ងៃក្នុងមួយសប្តាហ៍ដែលអ្នកចង់ធ្វើទម្លាប់នីមួយៗ។',
      settings:'ការកំណត់', preferences:'ចំណូលចិត្ត', language:'ភាសា', languageHint:'ជ្រើសរើសខ្មែរ ឬអង់គ្លេស',
      reminders:'ការរំលឹក', reminderHint:'ប្តូរម៉ោងរំលឹកពីម៉ឺនុយ Bot → បន្ថែម។', admin:'ឧបករណ៍ Admin',
      adminOnly:'សម្រាប់ Admin', users:'អ្នកប្រើ', totalTasks:'ទម្លាប់', maintenance:'របៀបថែទាំ',
      maintenanceHint:'ផ្អាកសកម្មភាព Bot សម្រាប់អ្នកប្រើទូទៅ', on:'បើក', off:'បិទ',
      todayTab:'ថ្ងៃនេះ', tasksTab:'ទម្លាប់', goalsTab:'គោលដៅ', settingsTab:'ការកំណត់',
      welcome:'សូមស្វាគមន៍មកកាន់កន្លែងទម្លាប់ប្រចាំថ្ងៃ។', welcomeSub:'កន្លែងសាមញ្ញសម្រាប់បង្កើតទម្លាប់ និងបន្តសកម្មភាពប្រចាំថ្ងៃ។', menuEyebrow:'កន្លែងរបស់អ្នក', menuTitle:'ជ្រើសរើសម៉ឺនុយ', menuHome:'ដើម', menuToday:'ថ្ងៃនេះ', menuTodaySub:'គូសបញ្ជាក់ទម្លាប់ថ្ងៃនេះ', menuTasks:'ទម្លាប់របស់ខ្ញុំ', menuTasksSub:'រៀបចំទម្លាប់ប្រចាំថ្ងៃ', menuGoals:'គោលដៅប្រចាំសប្តាហ៍', menuGoalsSub:'មើលវឌ្ឍនភាពសប្តាហ៍នេះ', menuSettings:'ការកំណត់', menuSettingsSub:'ភាសា និងចំណូលចិត្ត', doneToday:'បានធ្វើថ្ងៃនេះ',
      menuCalendar:'ប្រតិទិនខ្មែរ', menuCalendarSub:'បើកប្រភពប្រតិទិន', menuAdd:'បន្ថែមទម្លាប់',
      goalDays:'ថ្ងៃ/សប្តាហ៍', auth:'សូមបើកកម្មវិធីនេះពី Telegram Bot។',
      serviceError:'មិនអាចផ្ទុកទម្លាប់បានទេ។ សូមបើកកម្មវិធីម្តងទៀត។',
      adminError:'មិនអាចបើកឧបករណ៍ Admin បានទេ។', close:'បិទ', loading:'កំពុងផ្ទុកទម្លាប់…'
    }
  };

  let lang = 'en';
  let tasks = [];
  let isAdmin = false;
  let editingTask = null;
  let initData = tg?.initData || '';
  const $ = (id) => document.getElementById(id);

  function notify(message) {
    const toast = $('toast');
    toast.textContent = message;
    toast.classList.add('show');
    window.clearTimeout(notify.timer);
    notify.timer = window.setTimeout(() => toast.classList.remove('show'), 2400);
    tg?.HapticFeedback?.notificationOccurred('success');
  }

  async function request(path, method = 'GET', body) {
    const response = await fetch(path, {
      method,
      headers: { 'Content-Type':'application/json', 'X-Telegram-Init-Data':initData },
      body: body === undefined ? undefined : JSON.stringify(body)
    });
    let data;
    try { data = await response.json(); }
    catch (_) { throw new Error(copy[lang].serviceError); }
    if (!response.ok) throw new Error(data.error || copy[lang].serviceError);
    return data;
  }

  function setText(id, value) { const element = $(id); if (element) element.textContent = value; }

  function applyLanguage() {
    const w = copy[lang];
    const fields = {
      todayLabel:w.today, heroEyebrow:w.eyebrow, heroTitle:w.title, heroSub:w.sub,
      focusLabel:w.focus, habitsTitle:w.habits, tasksEyebrow:w.tasksEyebrow,
      tasksHeading:w.allHabits, weekLabel:w.week, weekTitle:w.goals, goalHint:w.goalHint,
      settingsHeading:w.settings, settingsEyebrow:w.preferences, languageName:w.language,
      languageHint:w.languageHint, reminderName:w.reminders, reminderHint:w.reminderHint,
      adminEyebrow:w.adminOnly, adminHeading:w.admin, usersLabel:w.users,
      totalTasksLabel:w.totalTasks, maintenanceName:w.maintenance,
      maintenanceHint:w.maintenanceHint, navToday:w.todayTab, navTasks:w.tasksTab,
      navGoals:w.goalsTab, navSettings:w.settingsTab, todayProgressLabel:w.todayLabel,
      streakLabel:w.best, footerText:w.footer, dialogEyebrow:w.focus, habitLabel:w.habitName,
      cancelEdit:w.cancel, deleteBtn:w.delete, closeDialog:w.close
    };
    Object.assign(fields, { welcomeEyebrow:lang==='en'?'WELCOME BACK':'សូមស្វាគមន៍', welcomeTitle:w.welcome, welcomeSub:w.welcomeSub, menuEyebrow:w.menuEyebrow, menuTitle:w.menuTitle, navHome:w.menuHome, menuTodayTitle:w.menuToday, menuTodaySub:w.menuTodaySub, menuTasksTitle:w.menuTasks, menuTasksSub:w.menuTasksSub, menuGoalsTitle:w.menuGoals, menuGoalsSub:w.menuGoalsSub, menuCalendarTitle:w.menuCalendar, menuCalendarSub:w.menuCalendarSub, menuAddTitle:w.menuAdd, menuSettingsTitle:w.menuSettings, menuSettingsSub:w.menuSettingsSub, homeDoneLabel:w.doneToday, homeStreakLabel:w.best });
    Object.entries(fields).forEach(([id,value]) => setText(id,value));
    setText('langBtn', lang === 'en' ? 'ខ្មែរ' : 'English');
    setText('langSetting', lang === 'en' ? 'English' : 'ខ្មែរ');
    document.documentElement.lang = lang;
    $('editInput').placeholder = w.habitName;
    $('dialogTitle').textContent = editingTask ? w.edit : w.add;
    $('saveEdit').textContent = editingTask ? w.save : w.addAction;
    $('deleteBtn').hidden = !editingTask;
  }

  function makeHabitCard(task, editable = false) {
    const row = document.createElement('article');
    row.className = `task${task.done ? ' done' : ''}`;

    const check = document.createElement('button');
    check.type = 'button'; check.className = 'check';
    check.textContent = task.done ? '✓' : '';
    check.setAttribute('aria-label', task.done ? 'Mark not done' : 'Mark done');
    check.onclick = () => toggleTask(task);

    const info = document.createElement('div'); info.className = 'task-info';
    const name = document.createElement('div'); name.className = 'task-name'; name.textContent = task.name;
    const meta = document.createElement('div'); meta.className = 'task-meta';
    meta.textContent = `${task.week_done || 0} / ${task.goal || 7} ${copy[lang].goalDays}`;
    info.append(name, meta);

    const streak = document.createElement('span'); streak.className = 'task-streak';
    streak.textContent = `🔥 ${task.streak || 0}`;
    row.append(check, info, streak);

    if (editable) {
      const edit = document.createElement('button'); edit.type='button'; edit.className='more';
      edit.textContent='•••'; edit.setAttribute('aria-label',copy[lang].edit);
      edit.onclick=()=>openDialog(task);
      row.append(edit);
    }
    return row;
  }

  function makeGoalRow(task) {
    const row = document.createElement('div'); row.className='goal-row';
    const name = document.createElement('span'); name.className='goal-name'; name.textContent=task.name;
    const count = document.createElement('span'); count.className='goal-count';
    count.textContent=`${task.week_done || 0}/${task.goal || 7}`;
    const bar = document.createElement('div'); bar.className='bar';
    const fill = document.createElement('i');
    fill.style.width=`${Math.min(100,(task.week_done || 0)/(task.goal || 7)*100)}%`;
    bar.append(fill);
    const controls = document.createElement('div'); controls.className='goal-controls';
    const minus = document.createElement('button'); minus.type='button'; minus.textContent='−';
    const goal = document.createElement('span'); goal.textContent=String(task.goal || 7);
    const plus = document.createElement('button'); plus.type='button'; plus.textContent='+';
    minus.setAttribute('aria-label','Decrease weekly target');
    plus.setAttribute('aria-label','Increase weekly target');
    minus.disabled=(task.goal || 7)<=1; plus.disabled=(task.goal || 7)>=7;
    minus.onclick=()=>saveGoal(task,(task.goal || 7)-1);
    plus.onclick=()=>saveGoal(task,(task.goal || 7)+1);
    controls.append(minus,goal,plus);
    row.append(name,count,bar,controls);
    return row;
  }

  function render() {
    const todayList=$('taskList'), allList=$('allTaskList'), goalList=$('goalList');
    todayList.replaceChildren(); allList.replaceChildren(); goalList.replaceChildren();
    const completed=tasks.filter(task=>task.done).length;
    setText('doneCount',`${completed}/${tasks.length}`);
    setText('streakCount',String(tasks.reduce((max,task)=>Math.max(max,task.best || 0),0)));
    setText('homeDone',`${completed}/${tasks.length}`);
    setText('homeStreak',String(tasks.reduce((max,task)=>Math.max(max,task.best || 0),0)));

    if (!tasks.length) {
      const empty=document.createElement('div'); empty.className='empty';
      empty.innerHTML=`<span aria-hidden="true">🌱</span><strong>${copy[lang].empty}</strong>`;
      todayList.append(empty);
      allList.append(empty.cloneNode(true));
      const noGoals=empty.cloneNode(true); goalList.append(noGoals);
      return;
    }
    tasks.forEach(task=>{
      todayList.append(makeHabitCard(task));
      allList.append(makeHabitCard(task,true));
      goalList.append(makeGoalRow(task));
    });
  }

  async function load() {
    try {
      const data=await request('/api/miniapp/data');
      tasks=Array.isArray(data.tasks)?data.tasks:[];
      lang=data.language==='km'?'km':'en';
      isAdmin=Boolean(data.is_admin);
      applyLanguage(); render();
      if (isAdmin) await loadAdmin();
    } catch (error) {
      const message=error.message.includes('Open this app') ? copy[lang].auth : copy[lang].serviceError;
      $('taskList').replaceChildren();
      const box=document.createElement('div'); box.className='empty error-state'; box.textContent=message;
      $('taskList').append(box);
    }
  }

  async function toggleTask(task) {
    try {
      const result=await request('/api/miniapp/toggle','POST',{task_id:task.id});
      task.done=Boolean(result.done);
      await load();
      if (result.badges?.length) result.badges.forEach(notify);
      else if (result.done) notify(copy[lang].done);
      tg?.HapticFeedback?.impactOccurred('light');
    } catch (_) { notify(copy[lang].oops); }
  }

  async function saveGoal(task, goal) {
    try {
      await request(`/api/miniapp/goal/${task.id}`,'POST',{goal});
      await load();
    } catch (error) { notify(error.message || copy[lang].oops); }
  }

  function openDialog(task = null) {
    editingTask=task;
    $('dialogError').textContent='';
    $('editInput').value=task ? task.name : '';
    applyLanguage();
    $('editDialog').hidden=false;
    requestAnimationFrame(()=>$('editInput').focus());
  }

  function closeDialog() {
    $('editDialog').hidden=true;
    editingTask=null;
    $('dialogError').textContent='';
  }

  async function saveHabit() {
    const name=$('editInput').value.trim();
    if (!name || name.length>80) { $('dialogError').textContent=copy[lang].invalidName; return; }
    const wasEditing=Boolean(editingTask);
    try {
      if (editingTask) await request(`/api/miniapp/task/${editingTask.id}`,'PATCH',{name});
      else await request('/api/miniapp/task','POST',{name});
      closeDialog(); await load(); notify(wasEditing ? copy[lang].updated : copy[lang].added);
    } catch (error) {
      $('dialogError').textContent=error.message.includes('already exists') ? copy[lang].duplicate : error.message;
    }
  }

  async function deleteHabit() {
    if (!editingTask || !window.confirm(copy[lang].confirmDelete)) return;
    try {
      await request(`/api/miniapp/task/${editingTask.id}`,'DELETE');
      closeDialog(); await load(); notify(copy[lang].deleted);
    } catch (_) { notify(copy[lang].oops); }
  }

  async function changeLanguage() {
    const next=lang==='en'?'km':'en';
    try {
      await request('/api/miniapp/language','POST',{language:next});
      lang=next; applyLanguage(); render();
    } catch (_) { notify(copy[lang].oops); }
  }

  async function loadAdmin() {
    try {
      const data=await request('/api/miniapp/admin');
      $('adminPanel').hidden=false;
      setText('adminUsers',String(data.users)); setText('adminTasks',String(data.tasks));
      setText('maintenanceToggle',data.maintenance?copy[lang].on:copy[lang].off);
      $('maintenanceToggle').classList.toggle('danger',Boolean(data.maintenance));
      $('maintenanceToggle').dataset.enabled=String(Boolean(data.maintenance));
    } catch (_) { $('adminPanel').hidden=true; }
  }

  async function toggleMaintenance() {
    try {
      const enabled=$('maintenanceToggle').dataset.enabled==='true';
      const data=await request('/api/miniapp/admin','POST',{maintenance:!enabled});
      setText('maintenanceToggle',data.maintenance?copy[lang].on:copy[lang].off);
      $('maintenanceToggle').dataset.enabled=String(Boolean(data.maintenance));
      $('maintenanceToggle').classList.toggle('danger',Boolean(data.maintenance));
      notify(copy[lang].updated);
    } catch (_) { notify(copy[lang].adminError); }
  }

  document.querySelectorAll('.nav-item').forEach(button=>button.addEventListener('click',()=>{
    openTab(button.dataset.tab,button);
  }));
  function openTab(tab,button) {
    document.querySelectorAll('.screen').forEach(screen=>screen.classList.toggle('active',screen.id===`screen-${tab}`));
    document.querySelectorAll('.nav-item').forEach(item=>item.classList.toggle('active',item.dataset.tab===tab));
    if (tab==='settings' && isAdmin) loadAdmin();
    window.scrollTo({top:0,behavior:'smooth'});
    tg?.HapticFeedback?.selectionChanged();
  }
  document.querySelectorAll('.menu-card[data-open]').forEach(button=>button.addEventListener('click',()=>openTab(button.dataset.open)));
  $('quickAdd').addEventListener('click',()=>openDialog());
  $('calendarLink').addEventListener('click',()=>{
    const url='https://khmer-lunar-calendar.com/';
    if (tg?.openLink) tg.openLink(url); else window.open(url,'_blank','noopener');
  });

  $('addBtn').addEventListener('click',()=>openDialog());
  $('addBtn2').addEventListener('click',()=>openDialog());
  $('langBtn').addEventListener('click',changeLanguage);
  $('langSetting').addEventListener('click',changeLanguage);
  $('saveEdit').addEventListener('click',saveHabit);
  $('deleteBtn').addEventListener('click',deleteHabit);
  $('cancelEdit').addEventListener('click',closeDialog);
  $('closeDialog').addEventListener('click',closeDialog);
  $('maintenanceToggle').addEventListener('click',toggleMaintenance);
  $('editInput').addEventListener('keydown',event=>{if(event.key==='Enter')saveHabit();if(event.key==='Escape')closeDialog();});
  $('editDialog').addEventListener('click',event=>{if(event.target===$('editDialog'))closeDialog();});

  applyLanguage();
  if (!initData) {
    $('taskList').replaceChildren();
    const box=document.createElement('div'); box.className='empty error-state'; box.textContent=copy.en.auth;
    $('taskList').append(box);
  } else load();
})();
