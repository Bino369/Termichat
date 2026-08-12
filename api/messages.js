let messages = [];

export default function handler(req, res) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch(e) {}
    }
    const text = body ? (body.text || body.message) : null;
    const sender = (body && body.sender) ? body.sender.trim() : 'Anonymous';

    if (text) {
      const now = Date.now();
      const newMsg = {
        id: now + '-' + Math.random().toString(36).substr(2, 5),
        timestamp: now,
        sender: sender,
        text: text
      };
      messages.push(newMsg);
      if (messages.length > 100) {
        messages.shift();
      }
      return res.status(200).json({ success: true, message: newMsg });
    }
    return res.status(400).json({ error: 'Missing message text' });
  }

  return res.status(200).json({ messages });
}
