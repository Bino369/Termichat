// Global in-memory storage for serverless runtime
let messages = [];

/**
 * Serverless HTTP Handler for TermiChat messages API.
 * Supports GET (fetch message history) and POST (send new message).
 * 
 * @param {import('http').IncomingMessage} req 
 * @param {import('http').ServerResponse} res 
 */
export default function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try { 
        body = JSON.parse(body); 
      } catch (e) {
        return res.status(400).json({ error: 'Malformed JSON payload' });
      }
    }

    const text = body ? (body.text || body.message) : null;
    const sender = (body && body.sender && typeof body.sender === 'string') 
      ? body.sender.trim().slice(0, 25) 
      : 'Anonymous';

    if (text && typeof text === 'string' && text.trim().length > 0) {
      const now = Date.now();
      const newMsg = {
        id: now + '-' + Math.random().toString(36).substring(2, 7),
        timestamp: now,
        sender: sender,
        text: text.trim()
      };
      messages.push(newMsg);

      // Keep recent 100 messages in buffer
      if (messages.length > 100) {
        messages.shift();
      }
      return res.status(200).json({ success: true, message: newMsg });
    }
    return res.status(400).json({ error: 'Message text cannot be empty' });
  }

  return res.status(200).json({ messages });
}
