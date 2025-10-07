async function fetchMessages() {
  const res = await fetch('/api/messages');
  const msgs = await res.json();
  const container = document.getElementById('messages');
  container.innerHTML = msgs.map(m => `
    <div class="msg">
      <div class="meta"><strong>${escapeHtml(m.name)}</strong> · ${new Date(m.created_at).toLocaleString()}</div>
      <div class="body">${escapeHtml(m.body)}</div>
      <div class="actions">
        <button onclick="deleteMsg(${m.id})">Delete</button>
      </div>
    </div>
  `).join('');
}

function escapeHtml(s){ return String(s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

document.getElementById('msgForm').addEventListener('submit', async e=>{
  e.preventDefault();
  const name = document.getElementById('name').value;
  const body = document.getElementById('body').value;
  await fetch('/api/messages', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({name, body})
  });
  document.getElementById('body').value = '';
  await fetchMessages();
});

async function deleteMsg(id){
  if(!confirm('Delete message?')) return;
  await fetch('/api/messages/' + id, {method:'DELETE'});
  await fetchMessages();
}

fetchMessages();
