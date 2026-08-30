# Connecting this UI to the real backend

The frontend in this project remains usable as a polished demo even before integration.
The backend is served on the same origin, so frontend JavaScript can call routes with `fetch()`.

Example authenticated check:

```js
const result = await fetch(`/api/projects/${projectId}/check`, {
  method: 'POST',
  credentials: 'include'
}).then(r => r.json());
```

ZIP upload:

```js
const fd = new FormData();
fd.append('project_zip', file);
const project = await fetch('/api/projects/upload', {
  method: 'POST', body: fd, credentials: 'include'
}).then(r => r.json());
```

For the SIH demo, you can first use the existing visual demo flow, then connect upload/check/verify one screen at a time.
