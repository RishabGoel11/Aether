document.addEventListener('DOMContentLoaded', () => {
  // Navigation Tabs
  const navItems = document.querySelectorAll('.nav-item');
  const tabPanes = document.querySelectorAll('.tab-pane');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetTab = item.getAttribute('data-tab');
      navItems.forEach(n => n.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      item.classList.add('active');
      const pane = document.getElementById(targetTab);
      if (pane) pane.classList.add('active');

      // Auto-load tab data if applicable
      if (targetTab === 'rag-tab') loadRagChunks();
      if (targetTab === 'memory-tab') loadMemories();
      if (targetTab === 'voice-tab') loadVoiceDevices();
      if (targetTab === 'doctor-tab') loadDiagnostics();
    });
  });

  // Chat Subsystem
  const chatMessages = document.getElementById('chat-messages');
  const chatInput = document.getElementById('chat-input');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const clearChatBtn = document.getElementById('clear-chat-btn');

  function appendChatMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;
    msgDiv.appendChild(bubble);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function sendChatMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    appendChatMessage('user', text);
    chatInput.value = '';
    chatSendBtn.disabled = true;

    // Show temporary thinking bubble
    const thinkingMsg = document.createElement('div');
    thinkingMsg.className = 'message assistant thinking';
    thinkingMsg.innerHTML = '<div class="message-bubble"><em>Thinking...</em></div>';
    chatMessages.appendChild(thinkingMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      thinkingMsg.remove();

      if (res.ok) {
        if (!data.success) {
          appendChatMessage('assistant', `⚠️ ${data.response || data.error || 'Failed to process message.'}`);
        } else {
          appendChatMessage('assistant', data.response || 'No response.');
        }
      } else {
        appendChatMessage('assistant', `⚠️ Error: ${data.detail || 'Failed to get response'}`);
      }
    } catch (err) {
      thinkingMsg.remove();
      appendChatMessage('assistant', `⚠️ Network error: ${err.message}`);
    } finally {
      chatSendBtn.disabled = false;
      chatInput.focus();
    }
  }

  chatSendBtn?.addEventListener('click', sendChatMessage);
  chatInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  });

  clearChatBtn?.addEventListener('click', async () => {
    try {
      await fetch('/api/chat/clear', { method: 'POST' });
      chatMessages.innerHTML = `
        <div class="message assistant">
          <div class="message-bubble">Session cleared. Ready for a new topic!</div>
        </div>
      `;
    } catch (err) {
      alert(`Could not clear session: ${err.message}`);
    }
  });

  // Multi-Agent Team Subsystem
  const teamGoalInput = document.getElementById('team-goal-input');
  const teamRunBtn = document.getElementById('team-run-btn');
  const teamLoading = document.getElementById('team-loading');
  const teamResultContainer = document.getElementById('team-result-container');
  const teamSubtasksList = document.getElementById('team-subtasks-list');
  const teamFinalAnswer = document.getElementById('team-final-answer');

  teamRunBtn?.addEventListener('click', async () => {
    const goal = teamGoalInput.value.trim();
    if (!goal) return;

    teamLoading.classList.remove('hidden');
    teamResultContainer.classList.add('hidden');
    teamRunBtn.disabled = true;

    try {
      const res = await fetch('/api/team', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: goal, plan: true })
      });
      const data = await res.json();

      teamSubtasksList.innerHTML = '';
      if (data.subtasks && data.subtasks.length > 0) {
        data.subtasks.forEach(task => {
          const card = document.createElement('div');
          card.className = 'subtask-item';
          card.innerHTML = `
            <div class="subtask-header">
              <span class="role-badge">${task.role}</span>
              <span class="status-badge">${task.status}</span>
            </div>
            <div class="subtask-desc">${task.description}</div>
            ${task.output ? `<div class="subtask-output">${escapeHtml(task.output)}</div>` : ''}
          `;
          teamSubtasksList.appendChild(card);
        });
      } else {
        teamSubtasksList.innerHTML = '<p class="empty-state">No subtasks generated.</p>';
      }

      teamFinalAnswer.textContent = data.final_answer || 'No final answer produced.';
      teamResultContainer.classList.remove('hidden');
    } catch (err) {
      alert(`Team execution failed: ${err.message}`);
    } finally {
      teamLoading.classList.add('hidden');
      teamRunBtn.disabled = false;
    }
  });

  // Autonomous ReAct Agent Subsystem
  const agentGoalInput = document.getElementById('agent-goal-input');
  const agentRunBtn = document.getElementById('agent-run-btn');
  const agentLoading = document.getElementById('agent-loading');
  const agentResultContainer = document.getElementById('agent-result-container');
  const agentFinalAnswer = document.getElementById('agent-final-answer');
  const agentTraceList = document.getElementById('agent-trace-list');

  agentRunBtn?.addEventListener('click', async () => {
    const goal = agentGoalInput.value.trim();
    if (!goal) return;

    agentLoading.classList.remove('hidden');
    agentResultContainer.classList.add('hidden');
    agentRunBtn.disabled = true;

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: goal, max_steps: 8 })
      });
      const data = await res.json();

      agentFinalAnswer.textContent = data.final_answer || 'Done.';
      agentTraceList.innerHTML = '';

      if (data.steps && data.steps.length > 0) {
        data.steps.forEach(step => {
          const item = document.createElement('div');
          item.className = 'timeline-step';
          item.innerHTML = `
            <div class="timeline-step-num">#${step.step_number}</div>
            <div class="timeline-step-content">
              <strong>Thought:</strong> <span>${escapeHtml(step.thought || 'N/A')}</span>
              ${step.action ? `<div><strong>Action:</strong> <code>${escapeHtml(step.action)}</code></div>` : ''}
              ${step.observation ? `<div><strong>Observation:</strong> <code>${escapeHtml(step.observation)}</code></div>` : ''}
            </div>
          `;
          agentTraceList.appendChild(item);
        });
      } else {
        agentTraceList.innerHTML = '<p class="empty-state">No steps recorded.</p>';
      }

      agentResultContainer.classList.remove('hidden');
    } catch (err) {
      alert(`Agent execution failed: ${err.message}`);
    } finally {
      agentLoading.classList.add('hidden');
      agentRunBtn.disabled = false;
    }
  });

  // Knowledge Base (RAG) Subsystem
  const ragPathInput = document.getElementById('rag-path-input');
  const ragIndexBtn = document.getElementById('rag-index-btn');
  const ragStatusMsg = document.getElementById('rag-status-msg');
  const ragChunksList = document.getElementById('rag-chunks-list');

  async function loadRagChunks() {
    try {
      const res = await fetch('/api/rag/chunks');
      const data = await res.json();
      ragChunksList.innerHTML = '';
      const chunkList = Array.isArray(data) ? data : (data.chunks || []);
      if (chunkList && chunkList.length > 0) {
        chunkList.forEach(chunk => {
          const div = document.createElement('div');
          div.className = 'chunk-item';
          div.innerHTML = `
            <div class="chunk-source">📄 ${escapeHtml(chunk.source || 'Unknown')}</div>
            <div>${escapeHtml(chunk.text || chunk.content || '')}</div>
          `;
          ragChunksList.appendChild(div);
        });
      } else {
        ragChunksList.innerHTML = '<p class="empty-state">No chunks currently indexed. Enter a path above to index documents.</p>';
      }
    } catch (err) {
      ragChunksList.innerHTML = `<p class="empty-state">Error loading chunks: ${err.message}</p>`;
    }
  }

  ragIndexBtn?.addEventListener('click', async () => {
    const path = ragPathInput.value.trim();
    if (!path) return;

    ragStatusMsg.textContent = 'Indexing files...';
    ragIndexBtn.disabled = true;

    try {
      const res = await fetch('/api/rag/index', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        ragStatusMsg.textContent = `✅ ${data.message || 'Successfully indexed ' + (data.indexed_chunks || 0) + ' chunk(s).'}`;
        loadRagChunks();
      } else {
        ragStatusMsg.textContent = `⚠️ Error: ${data.detail || data.message || 'Indexing failed'}`;
      }
    } catch (err) {
      ragStatusMsg.textContent = `⚠️ Network error: ${err.message}`;
    } finally {
      ragIndexBtn.disabled = false;
    }
  });

  // Long-Term Memory Subsystem
  const memoryList = document.getElementById('memory-list');
  const refreshMemoryBtn = document.getElementById('refresh-memory-btn');

  async function loadMemories() {
    memoryList.innerHTML = '<p class="empty-state">Loading memories...</p>';
    try {
      const res = await fetch('/api/memory');
      const data = await res.json();
      memoryList.innerHTML = '';
      if (data.memories && data.memories.length > 0) {
        data.memories.forEach(mem => {
          const card = document.createElement('div');
          card.className = 'memory-card';
          card.innerHTML = `
            <div class="memory-text">${escapeHtml(mem.content)}</div>
            <div class="memory-footer">
              <span>Importance: ${mem.importance || 1}</span>
              <button class="btn btn-secondary delete-mem-btn" data-id="${mem.id}" style="padding: 4px 8px; font-size: 0.75rem;">Delete</button>
            </div>
          `;
          memoryList.appendChild(card);
        });

        document.querySelectorAll('.delete-mem-btn').forEach(btn => {
          btn.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            await fetch(`/api/memory/${id}`, { method: 'DELETE' });
            loadMemories();
          });
        });
      } else {
        memoryList.innerHTML = '<p class="empty-state">No long-term memories stored yet. Converse with Aether to establish context!</p>';
      }
    } catch (err) {
      memoryList.innerHTML = `<p class="empty-state">Error loading memory: ${err.message}</p>`;
    }
  }

  refreshMemoryBtn?.addEventListener('click', loadMemories);

  // Voice Subsystem
  const voiceSpeakInput = document.getElementById('voice-speak-input');
  const voiceSpeakBtn = document.getElementById('voice-speak-btn');
  const voiceSpeakStatus = document.getElementById('voice-speak-status');
  const voiceDeviceList = document.getElementById('voice-device-list');

  voiceSpeakBtn?.addEventListener('click', async () => {
    const text = voiceSpeakInput.value.trim();
    if (!text) return;

    voiceSpeakStatus.textContent = 'Speaking aloud...';
    voiceSpeakBtn.disabled = true;

    try {
      const res = await fetch('/api/voice/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
      });
      const data = await res.json();
      if (res.ok) {
        voiceSpeakStatus.textContent = '✅ Synthesized successfully!';
      } else {
        voiceSpeakStatus.textContent = `⚠️ Error: ${data.detail || 'TTS error'}`;
      }
    } catch (err) {
      voiceSpeakStatus.textContent = `⚠️ Error: ${err.message}`;
    } finally {
      voiceSpeakBtn.disabled = false;
    }
  });

  async function loadVoiceDevices() {
    voiceDeviceList.innerHTML = '<p class="empty-state">Querying audio devices...</p>';
    try {
      const res = await fetch('/api/voice/devices');
      const data = await res.json();
      voiceDeviceList.innerHTML = '';
      if (data.devices && data.devices.length > 0) {
        data.devices.forEach(dev => {
          const div = document.createElement('div');
          div.className = 'check-row';
          div.innerHTML = `
            <div class="check-label"><span>🎙️</span> ${escapeHtml(dev.name || 'Audio Device')}</div>
            <span class="role-badge">Ch: ${dev.max_input_channels || 1}</span>
          `;
          voiceDeviceList.appendChild(div);
        });
      } else {
        voiceDeviceList.innerHTML = '<p class="empty-state">No microphone input devices found or sounddevice unavailable.</p>';
      }
    } catch (err) {
      voiceDeviceList.innerHTML = `<p class="empty-state">Error querying audio devices: ${err.message}</p>`;
    }
  }

  // Diagnostics & Doctor
  const runDoctorBtn = document.getElementById('run-doctor-btn');
  const healthSummaryCard = document.getElementById('health-summary-card');
  const doctorChecksList = document.getElementById('doctor-checks-list');

  async function loadDiagnostics() {
    healthSummaryCard.innerHTML = '<div class="spinner"></div><p>Checking platform health...</p>';
    doctorChecksList.innerHTML = '';

    try {
      const [healthRes, docRes] = await Promise.all([
        fetch('/api/health'),
        fetch('/api/doctor')
      ]);
      const healthData = await healthRes.json();
      const docData = await docRes.json();

      healthSummaryCard.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <h3>Overall Status: <span style="color: ${healthData.status === 'healthy' ? '#10b981' : '#f59e0b'}">${healthData.status.toUpperCase()}</span></h3>
            <p class="subtitle">Platform: Aether v${healthData.version || '0.11.0'}</p>
          </div>
          <span class="dot online"></span>
        </div>
      `;

      if (docData.checks && docData.checks.length > 0) {
        doctorChecksList.innerHTML = '';
        docData.checks.forEach(check => {
          const row = document.createElement('div');
          row.className = 'check-row';
          row.innerHTML = `
            <div class="check-label">
              <span>${check.status === 'ok' ? '✅' : '⚠️'}</span>
              <span>${escapeHtml(check.name)}</span>
            </div>
            <span class="status-badge" style="background: ${check.status === 'ok' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)'}; color: ${check.status === 'ok' ? '#34d399' : '#fbbf24'}">
              ${check.status.toUpperCase()}
            </span>
          `;
          doctorChecksList.appendChild(row);
        });
      }
    } catch (err) {
      healthSummaryCard.innerHTML = `<p class="empty-state">Diagnostics check failed: ${err.message}</p>`;
    }
  }

  runDoctorBtn?.addEventListener('click', loadDiagnostics);

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
