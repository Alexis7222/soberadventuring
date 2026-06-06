/**
 * SETUP INSTRUCTIONS (one-time, ~5 minutes, completely free)
 * ──────────────────────────────────────────────────────────
 * 1. Go to https://workers.cloudflare.com and sign in (free account)
 * 2. Click "Create Worker", paste this entire file, click "Deploy"
 * 3. Go to the Worker's Settings → Variables → KV Namespace Bindings
 *    - Click "Add binding", Variable name: LEADS, select or create a KV namespace named "LEADS"
 * 4. Go to Settings → Variables → Environment Variables
 *    - Add ADMIN_KEY = any password you want (keep it — you'll need it for the admin page)
 * 5. Copy the Worker URL (looks like https://your-worker.your-subdomain.workers.dev)
 * 6. Find the two lines marked TODO below in quiz/index.html and alexis7222/index.html
 *    and replace YOUR_CLOUDFLARE_WORKER_URL_HERE with that URL
 */

export default {
  async fetch(request, env) {
    const cors = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: cors });
    }

    if (request.method === 'POST') {
      try {
        const data = await request.json();
        const email = (data.email || '').trim();
        if (!email || !email.includes('@')) {
          return new Response(JSON.stringify({ ok: false, error: 'Invalid email' }), {
            status: 400, headers: { ...cors, 'Content-Type': 'application/json' }
          });
        }
        const lead = {
          email,
          name:   (data.name   || '').trim(),
          result: (data.result || '').trim(),
          ts:     new Date().toISOString()
        };
        const key = Date.now() + '-' + Math.random().toString(36).slice(2, 8);
        await env.LEADS.put(key, JSON.stringify(lead));
        return new Response(JSON.stringify({ ok: true }), {
          headers: { ...cors, 'Content-Type': 'application/json' }
        });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false }), {
          status: 500, headers: { ...cors, 'Content-Type': 'application/json' }
        });
      }
    }

    if (request.method === 'GET') {
      const auth = request.headers.get('Authorization') || '';
      if (!env.ADMIN_KEY || auth !== 'Bearer ' + env.ADMIN_KEY) {
        return new Response(JSON.stringify({ error: 'Unauthorized' }), {
          status: 401, headers: { ...cors, 'Content-Type': 'application/json' }
        });
      }
      const list = await env.LEADS.list({ limit: 1000 });
      const leads = await Promise.all(
        list.keys.map(k => env.LEADS.get(k.name).then(v => v ? JSON.parse(v) : null))
      );
      const valid = leads.filter(Boolean).sort((a, b) => b.ts.localeCompare(a.ts));
      return new Response(JSON.stringify(valid), {
        headers: { ...cors, 'Content-Type': 'application/json' }
      });
    }

    return new Response('Not found', { status: 404, headers: cors });
  }
};
