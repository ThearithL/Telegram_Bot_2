(() => {
  'use strict';

  const tg = window.Telegram?.WebApp;
  tg?.ready();

  const copy = {
    en: {
      screenSize:'Screen size',screenHint:'Fullscreen is the default. Switch to windowed mode whenever you want.',fullscreen:'Fullscreen',windowed:'Windowed',fullscreenUnsupported:'Fullscreen is not supported on this Telegram version or device.',
      space:'YOUR DAILY SPACE',welcome:'Welcome back.',welcomeSub:'Small steps make strong routines.',menu:'Choose an option',today:'Today',todaySub:"Check off today's habits",habits:'My habits',habitsSub:'View and edit habits',goals:'Weekly goals',goalsSub:'Track your progress',stats:'Stats',statsSub:'Your last 7 days',reminders:'Reminders',remindersSub:'Manage reminder times',export:'Export data',exportSub:'Download your history',calendar:'Khmer Calendar',calendarSub:'Open the calendar source',settings:'Settings',settingsSub:'Language and preferences',help:'Help',helpSub:'How to use the app',add:'Add a habit',
      eyebrow:'A little progress, every day',heroTitle:'Make today count.',heroSub:'Small steps grow into strong habits.',focus:'YOUR FOCUS',dailyHabits:"Today's habits",todayLabel:'today',best:'best streak',footer:'One small win is still a win. 🌿',empty:'No habits yet. Add your first one to get started.',edit:'Edit habit',habitName:'Habit name',added:'Habit added 🌱',done:'Nice work! Keep it growing 🌱',updated:'Saved successfully.',deleted:'Habit deleted.',save:'Save habit',addAction:'Add habit',cancel:'Cancel',delete:'Delete',confirmDelete:'Delete this habit and all its history?',invalidName:'Enter a habit name (1–80 characters).',duplicate:'You already have a habit with that name.',oops:'Could not save that. Please try again.',
      tasksEyebrow:'BUILD YOUR ROUTINE',allHabits:'All habits',week:'KEEP GROWING',weeklyGoals:'Weekly goals',goalHint:'Choose how many days each week you want to complete each habit.',goalDays:'days/week',statsEyebrow:'YOUR PROGRESS',lastSeven:'Last 7 days',completedHabits:'habit check-ins',statsHint:'Completed habits across your routine each day.',moreEyebrow:'TOOLS',moreOptions:'More options',reminderEyebrow:'STAY ON TRACK',reminderTimes:'Reminder times',reminderHint:'Choose when the bot sends your daily check-in.',addTime:'Add time',noReminders:'No reminders yet. Add a time that works for you.',reminderAdded:'Reminder added.',reminderRemoved:'Reminder removed.',invalidTime:'Choose a valid time.',duplicateTime:'That reminder time already exists.',exporting:'Preparing your download…',exported:'Your Excel file is ready.',exportFailed:'Could not export your data.',templatesEyebrow:'GET STARTED',templatesHeading:'Habit ideas',templatesHint:'Add a suggested habit with one tap. You can edit it any time.',templateWater:'Drink 6 glasses of water',templateRead:'Read 10 pages',templateWalk:'Walk 20 minutes',templateStretch:'Stretch for 5 minutes',templateSleep:'Sleep before 10:30 PM',templateMeditate:'Meditate 5 minutes',templateAdded:'Habit added to your routine 🌱',templateDuplicate:'You already have that habit.',
      preferences:'PREFERENCES',language:'Language',languageHint:'Choose Khmer or English',admin:'Admin tools',adminOnly:'ADMIN ONLY',users:'users',totalTasks:'habits',maintenance:'Maintenance mode',maintenanceHint:'Pause bot actions for regular users',on:'On',off:'Off',homeTab:'Home',todayTab:'Today',tasksTab:'Habits',moreTab:'More',helpEyebrow:'QUICK GUIDE',howToUse:'How to use',help1Title:'Add a habit',help1:'Tap + and enter a short habit name.',help2Title:'Check in daily',help2:'Open Today and tap a circle when you finish a habit.',help3Title:'Track your week',help3:'Use Goals and Stats to see your progress.',help4Title:'Set reminders',help4:'Choose one or more reminder times in More.',
      auth:'Telegram could not verify this session. Close and reopen the Mini App from your bot. If it continues, the bot setup needs fixing.',serviceError:'Could not load your habits. Reopen the app from Telegram.',adminError:'Admin tools are unavailable.',close:'Close',loading:'Loading your habits…',noTasksForStats:'Add habits to see your weekly stats.'
    },
    km: {
      screenSize:'ទំហំអេក្រង់',screenHint:'Fullscreen ជាលំនាំដើម។ អ្នកអាចប្តូរទៅទម្រង់ធម្មតាបានគ្រប់ពេល។',fullscreen:'ពេញអេក្រង់',windowed:'ទម្រង់ធម្មតា',fullscreenUnsupported:'Telegram ឬឧបករណ៍នេះមិនគាំទ្រ Fullscreen ទេ។',
      space:'ទម្លាប់ប្រចាំថ្ងៃរបស់អ្នក',welcome:'សូមស្វាគមន៍មកវិញ។',welcomeSub:'ជំហានតូចៗ បង្កើតទម្លាប់ល្អ។',menu:'ជ្រើសរើសម៉ឺនុយ',today:'ថ្ងៃនេះ',todaySub:'គូសបញ្ជាក់ទម្លាប់ថ្ងៃនេះ',habits:'ទម្លាប់របស់ខ្ញុំ',habitsSub:'មើល និងកែទម្លាប់',goals:'គោលដៅប្រចាំសប្តាហ៍',goalsSub:'តាមដានវឌ្ឍនភាព',stats:'ស្ថិតិ',statsSub:'ទិន្នន័យ ៧ ថ្ងៃចុងក្រោយ',reminders:'ការរំលឹក',remindersSub:'គ្រប់គ្រងម៉ោងរំលឹក',export:'ទាញយកទិន្នន័យ',exportSub:'ទាញយកប្រវត្តិរបស់អ្នក',calendar:'ប្រតិទិនខ្មែរ',calendarSub:'បើកគេហទំព័រប្រភព',settings:'ការកំណត់',settingsSub:'ភាសា និងចំណូលចិត្ត',help:'ជំនួយ',helpSub:'របៀបប្រើកម្មវិធី',add:'បន្ថែមទម្លាប់',
      eyebrow:'រីកចម្រើនបន្តិចម្តងៗរាល់ថ្ងៃ',heroTitle:'ធ្វើឱ្យថ្ងៃនេះមានន័យ។',heroSub:'ជំហានតូចៗ បង្កើតទម្លាប់ល្អ។',focus:'គោលដៅរបស់អ្នក',dailyHabits:'ទម្លាប់ថ្ងៃនេះ',todayLabel:'ថ្ងៃនេះ',best:'កំណត់ត្រាល្អបំផុត',footer:'ជោគជ័យតូចមួយ ក៏ជាជោគជ័យដែរ 🌿',empty:'មិនទាន់មានទម្លាប់ទេ។ បន្ថែមទម្លាប់ដំបូងរបស់អ្នក។',edit:'កែទម្លាប់',habitName:'ឈ្មោះទម្លាប់',added:'បានបន្ថែមទម្លាប់ 🌱',done:'ល្អណាស់! បន្តទៅមុខទៀត 🌱',updated:'បានរក្សាទុករួចរាល់។',deleted:'បានលុបទម្លាប់។',save:'រក្សាទុកទម្លាប់',addAction:'បន្ថែមទម្លាប់',cancel:'បោះបង់',delete:'លុប',confirmDelete:'លុបទម្លាប់ និងប្រវត្តិរបស់វាមែនទេ?',invalidName:'សូមបញ្ចូលឈ្មោះទម្លាប់ (១–៨០ តួអក្សរ)។',duplicate:'មានទម្លាប់ឈ្មោះនេះរួចហើយ។',oops:'មិនអាចរក្សាទុកបានទេ។ សូមព្យាយាមម្តងទៀត។',
      tasksEyebrow:'បង្កើតទម្លាប់របស់អ្នក',allHabits:'ទម្លាប់ទាំងអស់',week:'បន្តរីកចម្រើន',weeklyGoals:'គោលដៅប្រចាំសប្តាហ៍',goalHint:'កំណត់ចំនួនថ្ងៃក្នុងមួយសប្តាហ៍ដែលអ្នកចង់ធ្វើទម្លាប់នីមួយៗ។',goalDays:'ថ្ងៃ/សប្តាហ៍',statsEyebrow:'វឌ្ឍនភាពរបស់អ្នក',lastSeven:'៧ ថ្ងៃចុងក្រោយ',completedHabits:'ការធ្វើទម្លាប់',statsHint:'ចំនួនទម្លាប់ដែលបានធ្វើក្នុងមួយថ្ងៃ។',moreEyebrow:'ឧបករណ៍',moreOptions:'ម៉ឺនុយបន្ថែម',reminderEyebrow:'កុំភ្លេចទម្លាប់',reminderTimes:'ម៉ោងរំលឹក',reminderHint:'ជ្រើសម៉ោងដែល bot ផ្ញើការរំលឹកប្រចាំថ្ងៃ។',addTime:'បន្ថែមម៉ោង',noReminders:'មិនទាន់មានម៉ោងរំលឹកទេ។ បន្ថែមម៉ោងដែលសមនឹងអ្នក។',reminderAdded:'បានបន្ថែមម៉ោងរំលឹក។',reminderRemoved:'បានលុបម៉ោងរំលឹក។',invalidTime:'សូមជ្រើសម៉ោងត្រឹមត្រូវ។',duplicateTime:'មានម៉ោងរំលឹកនេះរួចហើយ។',exporting:'កំពុងរៀបចំឯកសារ…',exported:'ឯកសារ Excel រួចរាល់។',exportFailed:'មិនអាចទាញយកទិន្នន័យបានទេ។',templatesEyebrow:'ចាប់ផ្តើមងាយៗ',templatesHeading:'គំនិតសម្រាប់ទម្លាប់',templatesHint:'ចុចម្ដងដើម្បីបន្ថែមទម្លាប់ណែនាំ។ អ្នកអាចកែវាពេលណាក៏បាន។',templateWater:'ផឹកទឹក ៦ កែវ',templateRead:'អានសៀវភៅ ១០ ទំព័រ',templateWalk:'ដើរ ២០ នាទី',templateStretch:'ហាត់ប្រាណស្រាល ៥ នាទី',templateSleep:'គេងមុនម៉ោង ១០:៣០ យប់',templateMeditate:'សមាធិ ៥ នាទី',templateAdded:'បានបន្ថែមទម្លាប់ទៅក្នុងបញ្ជី 🌱',templateDuplicate:'មានទម្លាប់នេះរួចហើយ។',
      preferences:'ចំណូលចិត្ត',language:'ភាសា',languageHint:'ជ្រើសរើសខ្មែរ ឬអង់គ្លេស',admin:'ឧបករណ៍ Admin',adminOnly:'សម្រាប់ Admin',users:'អ្នកប្រើ',totalTasks:'ទម្លាប់',maintenance:'របៀបថែទាំ',maintenanceHint:'ផ្អាកសកម្មភាព bot សម្រាប់អ្នកប្រើទូទៅ',on:'បើក',off:'បិទ',homeTab:'ដើម',todayTab:'ថ្ងៃនេះ',tasksTab:'ទម្លាប់',moreTab:'បន្ថែម',helpEyebrow:'ការណែនាំខ្លី',howToUse:'របៀបប្រើ',help1Title:'បន្ថែមទម្លាប់',help1:'ចុច + ហើយបញ្ចូលឈ្មោះទម្លាប់ខ្លីៗ។',help2Title:'កត់ត្រារាល់ថ្ងៃ',help2:'បើក ថ្ងៃនេះ ហើយចុចរង្វង់ពេលអ្នកធ្វើទម្លាប់រួច។',help3Title:'តាមដានសប្តាហ៍',help3:'ប្រើ គោលដៅ និង ស្ថិតិ ដើម្បីមើលវឌ្ឍនភាព។',help4Title:'កំណត់ការរំលឹក',help4:'ជ្រើសម៉ោងរំលឹកមួយ ឬច្រើននៅក្នុង បន្ថែម។',
      auth:'Telegram មិនអាចផ្ទៀងផ្ទាត់សម័យនេះបានទេ។ សូមបិទ ហើយបើក Mini App ពី Bot ម្តងទៀត។ បើនៅតែមានបញ្ហា ត្រូវកែការកំណត់ Bot។',serviceError:'មិនអាចផ្ទុកទម្លាប់បានទេ។ សូមបើកកម្មវិធីពី Telegram ម្តងទៀត។',adminError:'មិនអាចបើកឧបករណ៍ Admin បានទេ។',close:'បិទ',loading:'កំពុងផ្ទុកទម្លាប់…',noTasksForStats:'បន្ថែមទម្លាប់ ដើម្បីមើលស្ថិតិប្រចាំសប្តាហ៍។'
    }
  };

  let lang = 'en';
  let screenMode = (() => { try { return localStorage.getItem('habit-screen-mode') === 'windowed' ? 'windowed' : 'fullscreen'; } catch (_) { return 'fullscreen'; } })();
  let tasks = [];
  let weekly = [];
  let reminders = [];
  let isAdmin = false;
  let editingTask = null;
  const initData = tg?.initData || '';
  const $ = (id) => document.getElementById(id);

  function notify(message, type = 'success') {
    const toast = $('toast');
    toast.textContent = message;
    toast.classList.toggle('toast-error', type === 'error');
    toast.classList.add('show');
    window.clearTimeout(notify.timer);
    notify.timer = window.setTimeout(() => toast.classList.remove('show'), 2600);
    if (type === 'success') tg?.HapticFeedback?.notificationOccurred('success');
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

  function setText(id, value) { const el = $(id); if (el) el.textContent = value; }

  function persistScreenMode() {
    try { localStorage.setItem('habit-screen-mode', screenMode); } catch (_) {}
    setText('screenSizeToggle', copy[lang][screenMode === 'fullscreen' ? 'fullscreen' : 'windowed']);
  }

  function applyInitialScreenMode() {
    if (!tg) return;
    if (screenMode === 'fullscreen') {
      if (typeof tg.requestFullscreen === 'function') tg.requestFullscreen();
      else {
        screenMode = 'windowed';
        persistScreenMode();
        tg.expand?.();
      }
    } else if (tg.isFullscreen && typeof tg.exitFullscreen === 'function') {
      tg.exitFullscreen();
    }
  }

  function changeScreenMode() {
    if (!tg) { notify(copy[lang].fullscreenUnsupported,'error'); return; }
    const next = screenMode === 'fullscreen' ? 'windowed' : 'fullscreen';
    if (next === 'fullscreen') {
      if (typeof tg.requestFullscreen !== 'function') {
        screenMode = 'windowed'; persistScreenMode(); tg.expand?.();
        notify(copy[lang].fullscreenUnsupported,'error'); return;
      }
      screenMode = 'fullscreen'; persistScreenMode(); tg.requestFullscreen();
    } else {
      screenMode = 'windowed'; persistScreenMode();
      if (typeof tg.exitFullscreen === 'function') tg.exitFullscreen();
      else notify(copy[lang].fullscreenUnsupported,'error');
    }
  }

  tg?.onEvent?.('fullscreenFailed', (event) => {
    if (event?.error === 'ALREADY_FULLSCREEN') return;
    screenMode = 'windowed'; persistScreenMode(); tg.expand?.();
    notify(copy[lang].fullscreenUnsupported,'error');
  });

  // Keep the Settings control in sync if the user changes fullscreen mode
  // with Telegram's own window controls.
  tg?.onEvent?.('fullscreenChanged', () => {
    screenMode = tg.isFullscreen ? 'fullscreen' : 'windowed';
    persistScreenMode();
  });

  function applyLanguage() {
    const w = copy[lang];
    const values = {
      todayLabel:w.space, welcomeEyebrow:lang === 'en' ? 'WELCOME BACK' : 'សូមស្វាគមន៍មកវិញ',
      welcomeTitle:w.welcome, welcomeSub:w.welcomeSub, menuTitle:w.menu, menuTodayTitle:w.today,
      menuTodaySub:w.todaySub, menuTasksTitle:w.habits, menuTasksSub:w.habitsSub,
      menuGoalsTitle:w.goals, menuGoalsSub:w.goalsSub, menuStatsTitle:w.stats, menuStatsSub:w.statsSub,
      menuRemindersTitle:w.reminders, menuRemindersSub:w.remindersSub, menuExportTitle:w.export,
      menuExportSub:w.exportSub, menuCalendarTitle:w.calendar, menuCalendarSub:w.calendarSub,
      menuSettingsTitle:w.settings, menuSettingsSub:w.settingsSub, menuHelpTitle:w.help,
      menuHelpSub:w.helpSub, heroEyebrow:w.eyebrow, heroTitle:w.heroTitle, heroSub:w.heroSub,
      focusLabel:w.focus, habitsTitle:w.dailyHabits, todayProgressLabel:w.todayLabel,
      streakLabel:w.best, footerText:w.footer, tasksEyebrow:w.tasksEyebrow, tasksHeading:w.allHabits,
      weekLabel:w.week, weekTitle:w.weeklyGoals, goalHint:w.goalHint, statsEyebrow:w.statsEyebrow,
      statsHeading:w.lastSeven, weeklyDoneLabel:w.completedHabits, statsHint:w.statsHint,
      moreEyebrow:w.moreEyebrow, moreHeading:w.moreOptions, reminderEyebrow:w.reminderEyebrow,
      remindersHeading:w.reminderTimes, remindersHint:w.reminderHint, addReminderBtn:w.addTime,
      templatesEyebrow:w.templatesEyebrow, templatesHeading:w.templatesHeading, templatesHint:w.templatesHint,
      templateWater:w.templateWater, templateRead:w.templateRead, templateWalk:w.templateWalk,
      templateStretch:w.templateStretch, templateSleep:w.templateSleep, templateMeditate:w.templateMeditate,
      moreExportTitle:w.export, moreExportSub:w.exportSub, moreCalendarTitle:w.calendar,
      moreCalendarSub:w.calendarSub, moreSettingsTitle:w.settings, moreSettingsSub:w.settingsSub,
      moreHelpTitle:w.help, moreHelpSub:w.helpSub, settingsEyebrow:w.preferences,
      settingsHeading:w.settings, languageName:w.language, languageHint:w.languageHint,
      screenSizeName:w.screenSize, screenSizeHint:w.screenHint,
      adminEyebrow:w.adminOnly, adminHeading:w.admin, usersLabel:w.users, totalTasksLabel:w.totalTasks,
      maintenanceName:w.maintenance, maintenanceHint:w.maintenanceHint, helpEyebrow:w.helpEyebrow,
      helpHeading:w.howToUse, helpStep1Title:w.help1Title, helpStep1:w.help1,
      helpStep2Title:w.help2Title, helpStep2:w.help2, helpStep3Title:w.help3Title,
      helpStep3:w.help3, helpStep4Title:w.help4Title, helpStep4:w.help4,
      navHome:w.homeTab, navToday:w.todayTab, navTasks:w.tasksTab, navMore:w.moreTab,
      dialogEyebrow:w.focus, habitLabel:w.habitName, cancelEdit:w.cancel,
      deleteBtn:w.delete, closeDialog:w.close
    };
    Object.entries(values).forEach(([id,value]) => setText(id,value));
    setText('langBtn', lang === 'en' ? 'ខ្មែរ' : 'English');
    setText('langSetting', lang === 'en' ? 'English' : 'ខ្មែរ');
    setText('screenSizeToggle', screenMode === 'fullscreen' ? w.fullscreen : w.windowed);
    document.documentElement.lang = lang;
    $('editInput').placeholder = w.habitName;
    $('dialogTitle').textContent = editingTask ? w.edit : w.add;
    $('saveEdit').textContent = editingTask ? w.save : w.addAction;
    $('deleteBtn').hidden = !editingTask;
    render();
  }

  function makeHabitCard(task, editable = false) {
    const row = document.createElement('article');
    row.className = `task${task.done ? ' done' : ''}`;
    const check = document.createElement('button');
    check.type = 'button'; check.className = 'check'; check.textContent = task.done ? '✓' : '';
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
      edit.onclick=()=>openDialog(task); row.append(edit);
    }
    return row;
  }

  function makeGoalRow(task) {
    const row = document.createElement('div'); row.className='goal-row';
    const name = document.createElement('span'); name.className='goal-name'; name.textContent=task.name;
    const count = document.createElement('span'); count.className='goal-count';
    count.textContent=`${task.week_done || 0}/${task.goal || 7}`;
    const bar = document.createElement('div'); bar.className='bar';
    const fill = document.createElement('i'); fill.style.width=`${Math.min(100,(task.week_done || 0)/(task.goal || 7)*100)}%`;
    bar.append(fill);
    const controls = document.createElement('div'); controls.className='goal-controls';
    const minus = document.createElement('button'); minus.type='button'; minus.textContent='−';
    const goal = document.createElement('span'); goal.textContent=String(task.goal || 7);
    const plus = document.createElement('button'); plus.type='button'; plus.textContent='+';
    minus.setAttribute('aria-label','Decrease weekly target'); plus.setAttribute('aria-label','Increase weekly target');
    minus.disabled=(task.goal || 7)<=1; plus.disabled=(task.goal || 7)>=7;
    minus.onclick=()=>saveGoal(task,(task.goal || 7)-1); plus.onclick=()=>saveGoal(task,(task.goal || 7)+1);
    controls.append(minus,goal,plus); row.append(name,count,bar,controls);
    return row;
  }

  function renderStats() {
    const chart = $('weeklyChart'); chart.replaceChildren();
    const points = weekly || [];
    const totalDone = points.reduce((sum, point) => sum + Number(point.done || 0), 0);
    setText('weeklyDone', String(totalDone));
    if (!tasks.length) {
      const empty = document.createElement('div'); empty.className='empty';
      empty.textContent = copy[lang].noTasksForStats; chart.append(empty); return;
    }
    const max = Math.max(1, ...points.map(point => Number(point.total || tasks.length)));
    points.forEach(point => {
      const item = document.createElement('div'); item.className='chart-day';
      const value = document.createElement('small'); value.textContent=String(point.done || 0);
      const track = document.createElement('div'); track.className='chart-track';
      const bar = document.createElement('i'); bar.style.height=`${Math.max(4,(Number(point.done || 0)/max)*100)}%`;
      if (point.date === dataDate) bar.classList.add('today-bar');
      track.append(bar);
      const date = new Date(`${point.date}T12:00:00+07:00`);
      const label = document.createElement('small');
      label.textContent = new Intl.DateTimeFormat(lang === 'km' ? 'km-KH' : 'en-US',{weekday:'short',timeZone:'Asia/Phnom_Phn'}).format(date);
      item.append(value,track,label); chart.append(item);
    });
  }

  function renderReminders() {
    const list = $('reminderList'); list.replaceChildren();
    if (!reminders.length) {
      const empty = document.createElement('div'); empty.className='empty reminder-empty';
      empty.textContent = copy[lang].noReminders; list.append(empty); return;
    }
    reminders.forEach(reminder => {
      const row = document.createElement('div'); row.className='reminder-row';
      const time = document.createElement('strong'); time.textContent=reminder.time;
      const remove = document.createElement('button'); remove.type='button'; remove.className='reminder-remove';
      remove.textContent = lang === 'km' ? 'លុប' : 'Remove';
      remove.setAttribute('aria-label',`${copy[lang].delete} ${reminder.time}`);
      remove.onclick=()=>deleteReminder(reminder.id);
      row.append(time,remove); list.append(row);
    });
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
      const icon=document.createElement('span'); icon.textContent='🌱';
      const text=document.createElement('strong'); text.textContent=copy[lang].empty;
      empty.append(icon,text); todayList.append(empty);
      allList.append(empty.cloneNode(true)); goalList.append(empty.cloneNode(true));
    } else {
      tasks.forEach(task=>{ todayList.append(makeHabitCard(task)); allList.append(makeHabitCard(task,true)); goalList.append(makeGoalRow(task)); });
    }
    renderStats(); renderReminders();
  }

  let dataDate = '';
  async function load() {
    try {
      const data=await request('/api/miniapp/data');
      tasks=Array.isArray(data.tasks)?data.tasks:[];
      weekly=Array.isArray(data.weekly)?data.weekly:[];
      reminders=Array.isArray(data.reminders)?data.reminders:[];
      dataDate=data.date || '';
      lang=data.language==='km'?'km':'en';
      isAdmin=Boolean(data.is_admin);
      $('connectionError').hidden=true;
      applyLanguage();
      if (isAdmin) await loadAdmin();
    } catch (error) {
      const message=error.message.includes('Open this app') || error.message.includes('Unauthorized') ? copy[lang].auth : copy[lang].serviceError;
      $('connectionError').textContent=message;
      $('connectionError').hidden=false;
      $('taskList').replaceChildren();
      const box=document.createElement('div'); box.className='empty error-state'; box.textContent=message;
      $('taskList').append(box);
    }
  }

  async function toggleTask(task) {
    try {
      const result=await request('/api/miniapp/toggle','POST',{task_id:task.id});
      task.done=Boolean(result.done); await load();
      if (result.badges?.length) result.badges.forEach(message=>notify(message));
      else if (result.done) notify(copy[lang].done);
      tg?.HapticFeedback?.impactOccurred('light');
    } catch (error) { notify(error.message || copy[lang].oops,'error'); }
  }

  async function saveGoal(task, goal) {
    try { await request(`/api/miniapp/goal/${task.id}`,'POST',{goal}); await load(); }
    catch (error) { notify(error.message || copy[lang].oops,'error'); }
  }

  function openDialog(task = null) {
    editingTask=task; $('dialogError').textContent=''; $('editInput').value=task ? task.name : '';
    applyDialogLanguage(); $('editDialog').hidden=false;
    requestAnimationFrame(()=>$('editInput').focus());
  }

  function applyDialogLanguage() {
    const w=copy[lang]; $('dialogEyebrow').textContent=w.focus; $('habitLabel').textContent=w.habitName;
    $('cancelEdit').textContent=w.cancel; $('deleteBtn').textContent=w.delete; $('closeDialog').setAttribute('aria-label',w.close);
    $('editInput').placeholder=w.habitName; $('dialogTitle').textContent=editingTask?w.edit:w.add;
    $('saveEdit').textContent=editingTask?w.save:w.addAction; $('deleteBtn').hidden=!editingTask;
  }

  function closeDialog() { $('editDialog').hidden=true; editingTask=null; $('dialogError').textContent=''; }

  async function saveHabit() {
    const name=$('editInput').value.trim();
    if (!name || name.length>80) { $('dialogError').textContent=copy[lang].invalidName; return; }
    const wasEditing=Boolean(editingTask);
    try {
      if (editingTask) await request(`/api/miniapp/task/${editingTask.id}`,'PATCH',{name});
      else await request('/api/miniapp/task','POST',{name});
      closeDialog(); await load(); notify(wasEditing?copy[lang].updated:copy[lang].added);
    } catch (error) { $('dialogError').textContent=error.message.includes('already exists')?copy[lang].duplicate:error.message; }
  }

  async function deleteHabit() {
    if (!editingTask || !window.confirm(copy[lang].confirmDelete)) return;
    try { await request(`/api/miniapp/task/${editingTask.id}`,'DELETE'); closeDialog(); await load(); notify(copy[lang].deleted); }
    catch (_) { notify(copy[lang].oops,'error'); }
  }

  async function changeLanguage() {
    const next=lang==='en'?'km':'en';
    try { await request('/api/miniapp/language','POST',{language:next}); lang=next; applyLanguage(); }
    catch (error) { notify(error.message || copy[lang].oops,'error'); }
  }

  async function addReminder() {
    const time=$('reminderInput').value;
    if (!time) { notify(copy[lang].invalidTime,'error'); return; }
    try { await request('/api/miniapp/reminders','POST',{time}); $('reminderInput').value=''; await load(); notify(copy[lang].reminderAdded); }
    catch (error) { notify(error.message.includes('already exists')?copy[lang].duplicateTime:error.message || copy[lang].oops,'error'); }
  }

  async function deleteReminder(id) {
    try { await request('/api/miniapp/reminders','DELETE',{id}); await load(); notify(copy[lang].reminderRemoved); }
    catch (error) { notify(error.message || copy[lang].oops,'error'); }
  }

  async function addTemplate(key, button) {
    const name=copy[lang][`template${key[0].toUpperCase()}${key.slice(1)}`];
    if (!name || button.disabled) return;
    button.disabled=true;
    try {
      await request('/api/miniapp/task','POST',{name});
      await load(); notify(copy[lang].templateAdded);
      tg?.HapticFeedback?.notificationOccurred('success');
    } catch (error) {
      const message=error.message || '';
      if (message.includes('already exists') || message.includes('រួចហើយ')) notify(copy[lang].templateDuplicate,'error');
      else if (message.includes('Unauthorized') || message.includes('Open this app')) notify(copy[lang].auth,'error');
      else notify(message || copy[lang].oops,'error');
    } finally { button.disabled=false; }
  }

  async function exportData() {
    try {
      notify(copy[lang].exporting);
      const response=await fetch('/api/miniapp/export',{headers:{'X-Telegram-Init-Data':initData}});
      if (!response.ok) { const error=await response.json().catch(()=>({})); throw new Error(error.error || copy[lang].exportFailed); }
      const blob=await response.blob(); const url=URL.createObjectURL(blob);
      const anchor=document.createElement('a'); anchor.href=url; anchor.download='my-daily-habits.xlsx';
      document.body.append(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
      notify(copy[lang].exported);
    } catch (error) { notify(error.message || copy[lang].exportFailed,'error'); }
  }

  async function loadAdmin() {
    try {
      const data=await request('/api/miniapp/admin'); $('adminPanel').hidden=false;
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
      $('maintenanceToggle').classList.toggle('danger',Boolean(data.maintenance)); notify(copy[lang].updated);
    } catch (_) { notify(copy[lang].adminError,'error'); }
  }

  function openTab(tab) {
    document.querySelectorAll('.screen').forEach(screen=>screen.classList.toggle('active',screen.id===`screen-${tab}`));
    document.querySelectorAll('.nav-item').forEach(item=>item.classList.toggle('active',item.dataset.tab===tab));
    if (tab==='settings' && isAdmin) loadAdmin();
    window.scrollTo({top:0,behavior:'smooth'}); tg?.HapticFeedback?.selectionChanged();
  }

  function openCalendar() {
    const url='https://khmer-lunar-calendar.com/';
    if (tg?.openLink) tg.openLink(url); else window.open(url,'_blank','noopener');
  }

  document.querySelectorAll('.nav-item').forEach(button=>button.addEventListener('click',()=>openTab(button.dataset.tab)));
  document.querySelectorAll('[data-open]').forEach(button=>button.addEventListener('click',()=>openTab(button.dataset.open)));
  $('quickAdd').addEventListener('click',()=>openDialog());
  $('calendarLink').addEventListener('click',openCalendar); $('moreCalendarBtn').addEventListener('click',openCalendar);
  $('exportBtn').addEventListener('click',exportData); $('moreExportBtn').addEventListener('click',exportData);
  $('addReminderBtn').addEventListener('click',addReminder);
  $('reminderInput').addEventListener('keydown',event=>{if(event.key==='Enter')addReminder();});
  document.querySelectorAll('[data-template]').forEach(button=>button.addEventListener('click',()=>addTemplate(button.dataset.template,button)));
  $('addBtn').addEventListener('click',()=>openDialog()); $('addBtn2').addEventListener('click',()=>openDialog());
  $('langBtn').addEventListener('click',changeLanguage); $('langSetting').addEventListener('click',changeLanguage);
  $('screenSizeToggle').addEventListener('click',changeScreenMode);
  $('saveEdit').addEventListener('click',saveHabit); $('deleteBtn').addEventListener('click',deleteHabit);
  $('cancelEdit').addEventListener('click',closeDialog); $('closeDialog').addEventListener('click',closeDialog);
  $('maintenanceToggle').addEventListener('click',toggleMaintenance);
  $('editInput').addEventListener('keydown',event=>{if(event.key==='Enter')saveHabit();if(event.key==='Escape')closeDialog();});
  $('editDialog').addEventListener('click',event=>{if(event.target===$('editDialog'))closeDialog();});

  const requestedView=new URLSearchParams(window.location.search).get('view');
  if (requestedView==='more') openTab('more');
  persistScreenMode();
  applyInitialScreenMode();

  if (!initData) {
    $('connectionError').textContent=copy.en.auth; $('connectionError').hidden=false;
    const box=document.createElement('div'); box.className='empty error-state'; box.textContent=copy.en.auth;
    $('taskList').replaceChildren(box);
  } else load();
})();
