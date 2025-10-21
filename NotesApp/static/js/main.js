// Initialize quill editor if editor-container exists
window.addEventListener('DOMContentLoaded', () => {
  const editorEl = document.getElementById('editor-container');
  if (editorEl) {
    const quill = new Quill('#editor-container', { theme: 'snow' });

    // INITIAL_CONTENT and NOTE_ID set by template if editing
    if (typeof INITIAL_CONTENT !== 'undefined' && INITIAL_CONTENT) {
      try { quill.root.innerHTML = INITIAL_CONTENT; } catch (e) { console.warn(e); }
    }

    const saveBtn = document.getElementById('save-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const titleInput = document.getElementById('note-title');

    saveBtn.addEventListener('click', async () => {
      saveBtn.disabled = true;
      const originalText = saveBtn.textContent;
      saveBtn.textContent = 'Saving...';
      const payload = { title: titleInput.value || 'Untitled', content: quill.root.innerHTML };
      try {
        if (typeof NOTE_ID !== 'undefined' && NOTE_ID) {
          await fetch(`/api/note/${NOTE_ID}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          saveBtn.textContent = 'Saved';
          setTimeout(() => { saveBtn.textContent = originalText; saveBtn.disabled = false; }, 800);
        } else {
          const res = await fetch('/api/note', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (data.id) {
            location.href = `/note/${data.id}`;
            return;
          }
          saveBtn.textContent = 'Saved';
          setTimeout(() => { saveBtn.textContent = originalText; saveBtn.disabled = false; }, 800);
        }
      } catch (err) {
        console.error(err);
        saveBtn.textContent = 'Error';
        saveBtn.disabled = false;
        setTimeout(() => { saveBtn.textContent = originalText; }, 1200);
      }
    });

    if (deleteBtn) {
      deleteBtn.addEventListener('click', async () => {
        if (!confirm('Delete this note?')) return;
        try {
          await fetch(`/api/note/${NOTE_ID}`, { method: 'DELETE' });
          location.href = '/dashboard';
        } catch (e) { console.error(e); alert('Delete failed'); }
      });
    }
  }
});
