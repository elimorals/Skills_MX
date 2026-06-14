/**
 * POST /api/lead-demo
 *
 * Recibe el form de "Agendar demo" del landing y reenvía el lead por email
 * a elimoralsmendox@gmail.com usando Resend.
 *
 * Requiere variable de entorno en Vercel:
 *   RESEND_API_KEY=re_xxx...   (https://resend.com/api-keys)
 *
 * Resend tier gratuito: 100 emails/día. Usando `onboarding@resend.dev` como
 * remitente, los emails solo pueden enviarse al email verificado de la cuenta
 * Resend — en este caso, el mismo elimoralsmendox@gmail.com (perfecto).
 *
 * Anti-spam:
 *   - Honeypot field "website" (debe venir vacío)
 *   - Validación de longitud y formato de email
 *   - Limita el largo total del payload
 */

const TO_EMAIL = 'elimoralsmendox@gmail.com';
const FROM = 'Plugins MX <onboarding@resend.dev>';
const MAX_FIELD_LEN = 500;
const MAX_PAYLOAD_BYTES = 4000;

const escape = (s) =>
  String(s == null ? '' : s).replace(/[<>&"']/g, (c) => ({
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    '"': '&quot;',
    "'": '&#39;',
  }[c]));

const isValidEmail = (e) =>
  typeof e === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e) && e.length <= 200;

const json = (res, status, body) => {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.status(status).send(JSON.stringify(body));
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return json(res, 405, { error: 'method_not_allowed' });
  }

  let data = req.body;
  if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch { data = null; }
  }
  if (!data || typeof data !== 'object') {
    return json(res, 400, { error: 'invalid_body' });
  }

  // Anti-spam honeypot — si trae "website" lleno, lo trataríamos como spam.
  if (data.website && String(data.website).trim() !== '') {
    return json(res, 200, { success: true });
  }

  const { nombre, empresa, email, tel, interes } = data;

  if (!nombre || !empresa || !email || !interes) {
    return json(res, 400, { error: 'missing_required_fields' });
  }

  const overlong = [nombre, empresa, email, tel || '', interes]
    .some((v) => String(v || '').length > MAX_FIELD_LEN);
  if (overlong) return json(res, 400, { error: 'field_too_long' });

  if (!isValidEmail(email)) {
    return json(res, 400, { error: 'invalid_email' });
  }

  const totalBytes = JSON.stringify({ nombre, empresa, email, tel, interes }).length;
  if (totalBytes > MAX_PAYLOAD_BYTES) {
    return json(res, 400, { error: 'payload_too_large' });
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.error('[lead-demo] RESEND_API_KEY no configurada');
    return json(res, 503, { error: 'service_unavailable', detail: 'email_not_configured' });
  }

  const receivedAt = new Date().toISOString();
  const subject = `Demo Plugins MX · ${nombre} de ${empresa}`;

  const html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>${escape(subject)}</title></head>
<body style="margin:0;padding:0;background:#F4EEE2;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#161313;">
  <div style="max-width:600px;margin:0 auto;background:#fff;padding:32px 28px;border:1px solid rgba(22,19,19,0.08);">
    <p style="margin:0 0 4px;font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:2px;color:#C2410C;">PLUGINS·MX  ·  NUEVO LEAD</p>
    <h1 style="font-family:Georgia,serif;font-size:24px;margin:8px 0 24px;line-height:1.2;">
      ${escape(nombre)} <span style="color:rgba(22,19,19,0.5);">de</span> ${escape(empresa)}
    </h1>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <tr>
        <td style="padding:10px 0;border-bottom:1px solid rgba(22,19,19,0.06);width:120px;color:rgba(22,19,19,0.5);font-size:12px;text-transform:uppercase;letter-spacing:1px;">Interés</td>
        <td style="padding:10px 0;border-bottom:1px solid rgba(22,19,19,0.06);font-weight:600;">${escape(interes)}</td>
      </tr>
      <tr>
        <td style="padding:10px 0;border-bottom:1px solid rgba(22,19,19,0.06);color:rgba(22,19,19,0.5);font-size:12px;text-transform:uppercase;letter-spacing:1px;">Email</td>
        <td style="padding:10px 0;border-bottom:1px solid rgba(22,19,19,0.06);"><a href="mailto:${escape(email)}" style="color:#C2410C;text-decoration:none;">${escape(email)}</a></td>
      </tr>
      ${tel ? `<tr>
        <td style="padding:10px 0;border-bottom:1px solid rgba(22,19,19,0.06);color:rgba(22,19,19,0.5);font-size:12px;text-transform:uppercase;letter-spacing:1px;">WhatsApp</td>
        <td style="padding:10px 0;border-bottom:1px solid rgba(22,19,19,0.06);"><a href="https://wa.me/${escape(String(tel).replace(/[^0-9]/g,''))}" style="color:#C2410C;text-decoration:none;">${escape(tel)}</a></td>
      </tr>` : ''}
      <tr>
        <td style="padding:10px 0;color:rgba(22,19,19,0.5);font-size:12px;text-transform:uppercase;letter-spacing:1px;">Recibido</td>
        <td style="padding:10px 0;font-family:'JetBrains Mono',monospace;font-size:12px;">${escape(receivedAt)}</td>
      </tr>
    </table>
    <div style="margin-top:28px;padding:16px;background:#F4EEE2;border-left:3px solid #C2410C;">
      <p style="margin:0;font-size:13px;line-height:1.55;color:rgba(22,19,19,0.75);">
        Responde directo a este correo y le llegará a <strong>${escape(email)}</strong>.
      </p>
    </div>
    <p style="margin:24px 0 0;font-size:11px;color:rgba(22,19,19,0.45);">
      skills-mexico.vercel.app · formulario "Agendar demo"
    </p>
  </div>
</body></html>`;

  const text = `Nuevo lead — Plugins MX

Nombre:    ${nombre}
Empresa:   ${empresa}
Email:     ${email}
${tel ? `WhatsApp:  ${tel}\n` : ''}Interés:   ${interes}

Recibido:  ${receivedAt}
Fuente:    skills-mexico.vercel.app
`;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: FROM,
        to: TO_EMAIL,
        reply_to: email,
        subject,
        html,
        text,
      }),
    });

    if (!r.ok) {
      const errText = await r.text();
      console.error('[lead-demo] Resend error', r.status, errText);
      return json(res, 502, { error: 'email_send_failed', status: r.status });
    }

    return json(res, 200, { success: true });
  } catch (e) {
    console.error('[lead-demo] uncaught', e);
    return json(res, 500, { error: 'internal_error' });
  }
}
