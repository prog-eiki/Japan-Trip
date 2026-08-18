import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# CSS
content = re.sub(r'\n\s*/\* Challenges \*/.*?\.challenge-card\.done \.checkmark \{ display: flex; \}', '', content, flags=re.DOTALL)
content = re.sub(r'\n\s*/\* Leaderboard \*/.*?\.stat-comp \{ display: flex; justify-content: space-between; padding: 15px; border-bottom: 1px solid var\(--border\); \}', '', content, flags=re.DOTALL)
content = re.sub(r'\n\s*\.xp-card \{ display: flex; align-items: center; gap: 20px; margin-bottom: 20px; \}\n\s*\.xp-card \.avatar \{ font-size: 3rem; \}\n\s*\.xp-card \.info \{ flex: 1; \}', '', content)
content = re.sub(r'\n\s*\.progress-bar\.gold \{ background-color: var\(--gold\); \}\n\s*\.progress-bar\.green \{ background-color: var\(--green\); \}', '', content)
content = re.sub(r'\n\s*\.toast-xp \{ border-left: 4px solid var\(--gold\); \}', '', content)

# Sidebar Traveler Info
content = re.sub(r'<div class="level-badge">.*?</div>\n\s*<div class="progress.*?</div>\n\s*<div class="text-sm text-muted">.*?</div>', '', content, flags=re.DOTALL)

# Nav Links
content = re.sub(r'\n\s*<a href="#challenges".*?</a>', '', content)
content = re.sub(r'\n\s*<a href="#leaderboard".*?</a>', '', content)

# Dashboard Stats Grid & Challenges
dash_stats_old = r'''<div class="stats-grid animate-fade-in">
                <div class="card xp-card">
                    <div class="avatar">🧑</div>
                    <div class="info">
                        <h4>Alex</h4>
                        <div class="level-badge">Lvl <span id="dash-t1-lvl"></span></div>
                        <div class="progress"><div class="progress-bar gold" id="dash-t1-prog"></div></div>
                    </div>
                </div>
                <div class="card xp-card">
                    <div class="avatar">👩</div>
                    <div class="info">
                        <h4>Mika</h4>
                        <div class="level-badge">Lvl <span id="dash-t2-lvl"></span></div>
                        <div class="progress"><div class="progress-bar gold" id="dash-t2-prog"></div></div>
                    </div>
                </div>
            </div>

            <h2>Offene Challenges</h2>
            <div class="challenge-grid animate-fade-in" id="dash-challenges">
                <!-- Populated by JS -->
            </div>'''
dash_stats_new = r'''<div class="stats-grid animate-fade-in">
                <div class="card text-center">
                    <h4>Besuchte Orte</h4>
                    <h2 id="dash-stat-places">0</h2>
                </div>
                <div class="card text-center">
                    <h4>Aktivitäten</h4>
                    <h2 id="dash-stat-activities">0</h2>
                </div>
            </div>'''
content = content.replace(dash_stats_old, dash_stats_new)

# Pages
# We will use simple replace for the HTML sections, making sure they match or regex:
content = re.sub(r'\s*<!-- Challenges Page -->\n\s*<div id="page-challenges"(.*?)(?=<!-- Food Page -->)', '\n\n        ', content, flags=re.DOTALL)
content = re.sub(r'\s*<!-- Leaderboard Page -->\n\s*<div id="page-leaderboard"(.*?)(?=<!-- Complete Page -->)', '\n\n        ', content, flags=re.DOTALL)

# Bottom Nav
content = re.sub(r'\n\s*<a href="#challenges" class="bottom-nav-item".*?</a>', '', content, flags=re.DOTALL)

# JS Constants
content = re.sub(r'const XP_PER_LEVEL = 200;\n\s*', '', content)

# JS Default Data
content = re.sub(r"traveler1: \{ name: 'Alex', emoji: '🧑', xp: 1240 \}", "traveler1: { name: 'Alex', emoji: '🧑' }", content)
content = re.sub(r"traveler2: \{ name: 'Mika', emoji: '👩', xp: 1080 \}", "traveler2: { name: 'Mika', emoji: '👩' }", content)
content = re.sub(r',\n\s*challenges: \[(.*?)\]', '', content, flags=re.DOTALL)

# JS State
content = re.sub(r"let currentChallengeView = 'traveler1';\n\s*", '', content)

# JS Functions to remove
content = re.sub(r'function getLevel\(xp\).*?function addXP\(traveler, amount, reason\).*?\}', '', content, flags=re.DOTALL)

# Navigate cases
content = re.sub(r"else if \(page === 'challenges'\) renderChallenges\(\);\n\s*", '', content)
content = re.sub(r"else if \(page === 'leaderboard'\) renderLeaderboard\(\);\n\s*", '', content)

# updateSidebarTraveler
sb_old = r'''const t = appState.travelers[currentTraveler];
        document.getElementById('sb-name').innerText = t.name;
        document.querySelector('#sidebar-info .avatar').innerText = t.emoji;
        document.getElementById('sb-lvl').innerText = getLevel(t.xp);
        document.getElementById('sb-xp').innerText = t.xp;
        document.getElementById('sb-progress').style.width = `${getLevelProgress(t.xp)}%`;
        
        const firstName = t.name.split(' ')[0];'''
sb_new = r'''const t = appState.travelers[currentTraveler];
        document.getElementById('sb-name').innerText = t.name;
        document.querySelector('#sidebar-info .avatar').innerText = t.emoji;
        
        const firstName = t.name.split(' ')[0];'''
content = content.replace(sb_old, sb_new)

# renderDashboard
rd_old = r'''function renderDashboard() {
        clearInterval(countdownInterval);
        renderCountdown();
        countdownInterval = setInterval(renderCountdown, 1000);

        ['traveler1', 'traveler2'].forEach((tKey, idx) => {
            const t = appState.travelers[tKey];
            const pfx = idx === 0 ? 't1' : 't2';
            document.getElementById(`dash-${pfx}-lvl`).innerText = getLevel(t.xp);
            document.getElementById(`dash-${pfx}-prog`).style.width = `${getLevelProgress(t.xp)}%`;
        });

        const chDiv = document.getElementById('dash-challenges');
        chDiv.innerHTML = '';
        const openCh = appState.challenges.filter(c => !c.completed[currentTraveler]).slice(0, 3);
        openCh.forEach(c => {
            chDiv.innerHTML += `
                <div class="card challenge-card" onclick="navigate('challenges')">
                    <div class="header">
                        <span class="emoji">${c.emoji}</span>
                        <span class="xp-reward">+${c.xp} XP</span>
                    </div>
                    <h4>${c.title}</h4>
                    <p class="text-sm text-muted">${c.desc}</p>
                </div>
            `;
        });
    }'''
rd_new = r'''function renderDashboard() {
        clearInterval(countdownInterval);
        renderCountdown();
        countdownInterval = setInterval(renderCountdown, 1000);

        let totalActivities = 0;
        let totalDone = 0;
        Object.values(appState.days).forEach(d => {
            totalActivities += d.activities.length;
            totalDone += d.activities.filter(a => a.done).length;
        });
        
        document.getElementById('dash-stat-places').innerText = Object.keys(CITIES).length;
        document.getElementById('dash-stat-activities').innerText = `${totalDone} / ${totalActivities}`;
    }'''
content = content.replace(rd_old, rd_new)

# toggleActivityDone
td_old = r'''function toggleActivityDone(id) {
        const act = appState.days[currentDay].activities.find(a => a.id === id);
        act.done = !act.done;
        if(act.done) addXP(currentTraveler, 50, 'Aktivität erledigt!');
        saveState();
        renderDayPage();
    }'''
td_new = r'''function toggleActivityDone(id) {
        const act = appState.days[currentDay].activities.find(a => a.id === id);
        act.done = !act.done;
        if(act.done) showToast('Aktivität erledigt!', 'success');
        saveState();
        renderDayPage();
    }'''
content = content.replace(td_old, td_new)

# submitFood
sf_old = r'''addXP(currentTraveler, 50, 'Essen dokumentiert!');'''
sf_new = r'''showToast('Essen dokumentiert!', 'success');'''
content = content.replace(sf_old, sf_new)

# Modals Food
fm_old = r'''Speichern (+50 XP)'''
fm_new = r'''Speichern'''
content = content.replace(fm_old, fm_new)

# JS Functions Challenges and Leaderboard removal
content = re.sub(r'// --- CHALLENGES ---.*?// --- FOOD ---', '// --- FOOD ---', content, flags=re.DOTALL)
content = re.sub(r'// --- LEADERBOARD ---.*?// --- COMPLETE ---', '// --- COMPLETE ---', content, flags=re.DOTALL)

# renderComplete
rc_old = r'''<div class="card"><div class="text-sm">Total XP</div><h2>${appState.travelers.traveler1.xp + appState.travelers.traveler2.xp}</h2></div>'''
rc_new = r'''<div class="card"><div class="text-sm">Erledigte Aktivitäten</div><h2>${Object.values(appState.days).reduce((sum, d) => sum + d.activities.filter(a => a.done).length, 0)}</h2></div>'''
content = content.replace(rc_old, rc_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
