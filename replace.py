import json

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 1: CDN
content = content.replace('</body>', '<script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js"></script>\n<script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-database.js"></script>\n</body>')

# Replace 2: sync-bar
sync_bar_old = '''        <div class="sync-bar">
          <div class="sync-status" id="sync-status">
            <span class="sync-dot" id="sync-dot"></span>
            <span id="sync-label">Nicht verbunden</span>
          </div>
          <button class="sync-btn" onclick="openSyncSettings()" title="GitHub Sync">&#9881;&#65039; Sync</button>
        </div>'''
sync_bar_new = '''        <div class="sync-bar">
          <div class="sync-status" id="sync-status">
            <span class="sync-dot" id="sync-dot"></span>
            <span id="sync-label">Offline</span>
          </div>
          <button class="sync-btn" onclick="openFirebaseSettings()" title="Firebase Sync">&#128293; Live Sync</button>
        </div>'''
content = content.replace(sync_bar_old, sync_bar_new)

# Replace 3: init hook
content = content.replace('            loadGHConfig();', '            loadFirebaseConfig();')

# Replace 4: saveState hook
content = content.replace('            debouncedGHPush();', '            if(typeof debouncedFirebasePush === \'function\') debouncedFirebasePush();')

# Replace 5: GITHUB SYNC
start_idx = content.find('        // === GITHUB SYNC ===')
end_idx = content.find('        // Start', start_idx)
if start_idx != -1 and end_idx != -1:
    fb_js = '''        // === FIREBASE SYNC ===
        let firebaseConfig = null;
        let fbApp = null;
        let fbDb = null;
        let isSyncingFromFirebase = false;

        function loadFirebaseConfig() {
          const saved = localStorage.getItem('japanquest_firebase_config');
          if (saved) {
            try { 
              firebaseConfig = JSON.parse(saved); 
              initFirebase();
            } catch(e) { firebaseConfig = null; }
          }
          updateSyncUI();
        }

        function saveFirebaseConfig(cfgStr) {
          try {
            // Basic sanitization to convert string to JSON (in case user pasted JS object)
            let jsonStr = cfgStr.replace(/(['"])?([a-zA-Z0-9_]+)(['"])?:/g, '"$2": ').replace(/'/g, '"');
            firebaseConfig = JSON.parse(jsonStr);
            localStorage.setItem('japanquest_firebase_config', JSON.stringify(firebaseConfig));
            initFirebase();
            updateSyncUI();
            showToast('Firebase verbunden!', 'success');
          } catch(e) {
            showToast('Ungültiges Format!', 'error');
          }
        }

        function initFirebase() {
          if (!firebaseConfig || !firebaseConfig.databaseURL) return;
          
          try {
            if (!firebase.apps.length) {
              fbApp = firebase.initializeApp(firebaseConfig);
            } else {
              fbApp = firebase.app();
            }
            fbDb = firebase.database();
            
            setSyncStatus('syncing', 'Verbinde...');
            
            const stateRef = fbDb.ref('japanQuest/state');
            
            // Listen for real-time changes
            stateRef.on('value', (snapshot) => {
              const data = snapshot.val();
              if (data) {
                isSyncingFromFirebase = true;
                appState = data;
                
                // Ensure structure exists
                DAY_CONFIG.forEach(d => {
                  if (!appState.days[d.date]) appState.days[d.date] = { activities: [] };
                });
                if (!appState.tickets) appState.tickets = {};
                
                saveState(); // Save locally
                
                // Render UI
                renderDashboard();
                renderReiseplanSidebar();
                renderReiseplanRight();
                renderBudget();
                if(window.renderTickets) window.renderTickets();
                applyTheme();
                
                setSyncStatus('connected', 'Live (Verbunden)');
                
                setTimeout(() => { isSyncingFromFirebase = false; }, 500);
              } else {
                setSyncStatus('connected', 'Live (Neu)');
                debouncedFirebasePush(true); // First time setup
              }
            });
            
          } catch(e) {
            console.error(e);
            setSyncStatus('error', 'Fehler');
          }
        }

        function updateSyncUI() {
          const dot = document.getElementById('sync-dot');
          const label = document.getElementById('sync-label');
          if (!dot || !label) return;
          if (firebaseConfig && firebaseConfig.databaseURL) {
            dot.className = 'sync-dot connected';
            label.textContent = 'Live (Verbunden)';
          } else {
            dot.className = 'sync-dot';
            label.textContent = 'Offline';
          }
        }

        function setSyncStatus(status, text) {
          const dot = document.getElementById('sync-dot');
          const label = document.getElementById('sync-label');
          if (!dot || !label) return;
          dot.className = 'sync-dot ' + status;
          label.textContent = text;
        }

        function openFirebaseSettings() {
          const cfgStr = firebaseConfig ? JSON.stringify(firebaseConfig, null, 2) : '';
          showModal(`
            <div class="modal-header">
              <div class="modal-title">&#128293; Firebase Live Sync</div>
              <div class="modal-close" onclick="closeModal()">&times;</div>
            </div>
            <p style="font-size:13px; color:var(--text-secondary); margin-bottom:16px;">
              Füge hier deine Firebase-Konfiguration (als JSON) ein, um die App in Echtzeit mit deinem Kollegen zu teilen.
            </p>
            <div class="form-group">
              <label class="form-label">Firebase Config (JSON)</label>
              <textarea class="form-input" id="fb-config-input" rows="8" placeholder='{\\n  "apiKey": "...",\\n  "authDomain": "...",\\n  "databaseURL": "...",\\n  "projectId": "...",\\n  "storageBucket": "...",\\n  "messagingSenderId": "...",\\n  "appId": "..."\\n}'>${cfgStr}</textarea>
            </div>
            <div style="display:flex; gap:10px; margin-top:20px;">
              <button class="btn btn-secondary" style="flex:1;" onclick="closeModal()">Abbrechen</button>
              <button class="btn btn-primary" style="flex:1;" onclick="submitFirebaseConfig()">Speichern & Verbinden</button>
            </div>
          `);
        }

        function submitFirebaseConfig() {
          const val = document.getElementById('fb-config-input').value.trim();
          if (val) {
            saveFirebaseConfig(val);
            closeModal();
          }
        }

        let fbPushTimer = null;
        function debouncedFirebasePush(force = false) {
          if (!fbDb || isSyncingFromFirebase) return;
          clearTimeout(fbPushTimer);
          fbPushTimer = setTimeout(() => {
            if (!isSyncingFromFirebase) {
              fbDb.ref('japanQuest/state').set(appState)
                .then(() => console.log('Saved to Firebase'))
                .catch(e => console.error('Firebase save error', e));
            }
          }, force ? 0 : 500);
        }

'''
    content = content[:start_idx] + fb_js + content[end_idx:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
