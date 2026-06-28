import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';

/* ───────────────────── types ───────────────────── */
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tools?: string[];
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  lastActive: Date;
}

/* ───────────────────── keyframes injected once ───────────────────── */
const STYLE_ID = 'eka-keyframes';
function injectKeyframes() {
  if (document.getElementById(STYLE_ID)) return;
  const style = document.createElement('style');
  style.id = STYLE_ID;
  style.textContent = `
    @keyframes eka-slideLeft  { from { opacity:0; transform:translateX(40px);  } to { opacity:1; transform:translateX(0); } }
    @keyframes eka-slideRight { from { opacity:0; transform:translateX(-40px); } to { opacity:1; transform:translateX(0); } }
    @keyframes eka-fadeUp     { from { opacity:0; transform:translateY(16px);  } to { opacity:1; transform:translateY(0); } }
    @keyframes eka-fadeIn     { from { opacity:0; } to { opacity:1; } }
    @keyframes eka-pulse      { 0%,100% { opacity:1; box-shadow:0 0 0 0 rgba(34,197,94,.5); } 50% { opacity:.7; box-shadow:0 0 0 6px rgba(34,197,94,0); } }
    @keyframes eka-gradientX  { 0% { background-position:0% 50%; } 50% { background-position:100% 50%; } 100% { background-position:0% 50%; } }
    @keyframes eka-bounce     { 0%,80%,100% { transform:scale(.5); opacity:.4; } 40% { transform:scale(1); opacity:1; } }
    @keyframes eka-spin       { to { transform:rotate(360deg); } }
    @keyframes eka-shimmer    { 0% { background-position:-200% 0; } 100% { background-position:200% 0; } }
    @keyframes eka-glow       { 0%,100% { filter:drop-shadow(0 0 6px rgba(59,130,246,.4)); } 50% { filter:drop-shadow(0 0 14px rgba(59,130,246,.7)); } }
    @keyframes eka-badgePop   { from { opacity:0; transform:scale(.7) translateY(4px); } to { opacity:1; transform:scale(1) translateY(0); } }
    @keyframes eka-cardFloat  { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-6px); } }
    *::-webkit-scrollbar { width:6px; }
    *::-webkit-scrollbar-track { background:transparent; }
    *::-webkit-scrollbar-thumb { background:#2a2a3a; border-radius:3px; }
    *::-webkit-scrollbar-thumb:hover { background:#3b82f6; }
    * { scrollbar-width:thin; scrollbar-color:#2a2a3a transparent; }
  `;
  document.head.appendChild(style);
}

/* ───────────────────── SVG icon components ───────────────────── */
const HexLogo: React.FC<{ size?: number }> = ({ size = 44 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{ animation: 'eka-glow 3s ease-in-out infinite' }}>
    <defs>
      <linearGradient id="hex-g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#3b82f6" />
        <stop offset="100%" stopColor="#06b6d4" />
      </linearGradient>
    </defs>
    <polygon points="50,2 93,27 93,73 50,98 7,73 7,27" fill="none" stroke="url(#hex-g)" strokeWidth="3" />
    <polygon points="50,12 83,32 83,68 50,88 17,68 17,32" fill="rgba(59,130,246,0.08)" stroke="url(#hex-g)" strokeWidth="1.5" />
    <text x="50" y="58" textAnchor="middle" fill="url(#hex-g)" fontSize="26" fontWeight="800" fontFamily="'Inter','Segoe UI',system-ui,sans-serif" letterSpacing="2">EKA</text>
  </svg>
);

const IconSend: React.FC = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m22 2-7 20-4-9-9-4z" /><path d="M22 2 11 13" />
  </svg>
);

const IconPlus: React.FC = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M12 5v14M5 12h14" /></svg>
);

const IconChat: React.FC = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

const IconDB: React.FC<{ size?: number }> = ({ size = 28 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
    <ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" /><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3" />
  </svg>
);

const IconFile: React.FC<{ size?: number }> = ({ size = 28 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <circle cx="11" cy="14" r="3" /><path d="m14 17 2 2" />
  </svg>
);

const IconMail: React.FC<{ size?: number }> = ({ size = 28 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="16" x="2" y="4" rx="2" /><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
  </svg>
);

const IconUser: React.FC = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="8" r="4" /><path d="M20 21a8 8 0 0 0-16 0" />
  </svg>
);

/* ───────────────────── constants ───────────────────── */
const COLORS = {
  bg: '#0a0a0f',
  card: '#12121a',
  border: '#1e1e2e',
  borderLight: '#2a2a3e',
  accent: '#3b82f6',
  accentDark: '#2563eb',
  cyan: '#06b6d4',
  textPrimary: '#f0f0f5',
  textSecondary: '#8888a0',
  textMuted: '#55556a',
  userBubbleFrom: '#2563eb',
  userBubbleTo: '#3b82f6',
  assistantBubble: '#1e1e2e',
  green: '#22c55e',
} as const;

const SUGGESTED_QUESTIONS = [
  'Quels projets avons-nous en cours pour Airbus ?',
  'Quelle est la procédure de validation AS9100 ?',
  'Prépare la réunion avec Airbus',
  "Rédige un email pour l'équipe qualité",
];

const SAMPLE_HISTORY: { title: string; time: string }[] = [
  { title: 'Analyse contrainte aile A320', time: '10:42' },
  { title: 'Audit fournisseur titane', time: '09:15' },
  { title: 'Procédure validation AS9100', time: 'Hier' },
  { title: 'Planning maintenance Q3', time: 'Hier' },
  { title: 'RFQ pièces moteur CFM56', time: 'Lun.' },
  { title: 'Rapport qualité composites', time: 'Lun.' },
];

const TOOL_BADGE_STYLES: Record<string, { bg: string; label: string; emoji: string }> = {
  sql:   { bg: '#166534', label: 'SQL',   emoji: '🗄️' },
  rag:   { bg: '#581c87', label: 'RAG',   emoji: '🔍' },
  email: { bg: '#92400e', label: 'Email', emoji: '✉️' },
};

function badgeFor(tool: string) {
  const key = tool.toLowerCase();
  if (key.includes('sql') || key.includes('database')) return TOOL_BADGE_STYLES.sql;
  if (key.includes('rag') || key.includes('retriev') || key.includes('document')) return TOOL_BADGE_STYLES.rag;
  if (key.includes('email') || key.includes('mail')) return TOOL_BADGE_STYLES.email;
  return { bg: '#333346', label: tool, emoji: '⚙️' };
}

function uid() { return Math.random().toString(36).slice(2) + Date.now().toString(36); }
function fmtTime(d: Date) { return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }

/* ================================================================ */
/*  APP                                                             */
/* ================================================================ */
const App: React.FC = () => {
  useEffect(injectKeyframes, []);

  /* ── state ── */
  const [conversations, setConversations] = useState<Conversation[]>([
    { id: uid(), title: 'Nouvelle conversation', messages: [], lastActive: new Date() },
  ]);
  const [activeId, setActiveId] = useState(conversations[0].id);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarHover, setSidebarHover] = useState<string | null>(null);

  const endRef = useRef<HTMLDivElement>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);

  const active = useMemo(() => conversations.find(c => c.id === activeId) ?? conversations[0], [conversations, activeId]);

  /* ── helpers ── */
  const scrollBottom = useCallback(() => {
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: 'smooth' }), 60);
  }, []);

  useEffect(scrollBottom, [active.messages, loading, scrollBottom]);

  useEffect(() => {
    const ta = taRef.current;
    if (ta) { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'; }
  }, [input]);

  function patchConv(id: string, fn: (c: Conversation) => Conversation) {
    setConversations(prev => prev.map(c => c.id === id ? fn(c) : c));
  }

  async function send(text?: string) {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;

    const userMsg: Message = { id: uid(), role: 'user', content: msg, timestamp: new Date() };
    patchConv(activeId, c => ({
      ...c,
      title: c.messages.length === 0 ? msg.slice(0, 50) : c.title,
      messages: [...c.messages, userMsg],
      lastActive: new Date(),
    }));
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/v1/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, session_id: 'default' }),
      });
      if (!res.ok) throw new Error(`${res.status}`);
      const data = await res.json();
      const aMsg: Message = {
        id: uid(), role: 'assistant',
        content: data.response ?? 'No response.',
        tools: data.tools_used ?? [],
        timestamp: new Date(),
      };
      patchConv(activeId, c => ({ ...c, messages: [...c.messages, aMsg], lastActive: new Date() }));
    } catch (e: any) {
      patchConv(activeId, c => ({
        ...c,
        messages: [...c.messages, {
          id: uid(), role: 'assistant',
          content: `⚠️ Connexion impossible au serveur. (${e.message})`,
          tools: [], timestamp: new Date(),
        }],
      }));
    } finally {
      setLoading(false);
      taRef.current?.focus();
    }
  }

  function newChat() {
    const c: Conversation = { id: uid(), title: 'Nouvelle conversation', messages: [], lastActive: new Date() };
    setConversations(prev => [c, ...prev]);
    setActiveId(c.id);
  }

  /* ================================================================ */
  /*  RENDER                                                          */
  /* ================================================================ */
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw',
      background: COLORS.bg, color: COLORS.textPrimary,
      fontFamily: "'Inter','Segoe UI',system-ui,-apple-system,sans-serif",
      overflow: 'hidden',
    }}>

      {/* ════════════ HEADER ════════════ */}
      <header style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 28px', height: 64, minHeight: 64,
        background: 'rgba(18,18,26,0.85)', backdropFilter: 'blur(16px)',
        borderBottom: 'none', position: 'relative', zIndex: 20,
      }}>
        {/* gradient line at bottom */}
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: 2,
          background: 'linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4, #3b82f6)',
          backgroundSize: '200% 100%',
          animation: 'eka-gradientX 4s linear infinite',
        }} />

        {/* left – logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <HexLogo size={42} />
        </div>

        {/* center – title */}
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 17, fontWeight: 700, letterSpacing: '-0.01em', color: '#fff' }}>
            Enterprise Knowledge Agent
          </div>
          <div style={{ fontSize: 11, color: COLORS.textSecondary, letterSpacing: '0.06em', marginTop: 1 }}>
            DCM Aeronautics — AI Division
          </div>
        </div>

        {/* right – status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 9, fontSize: 12, color: COLORS.textSecondary }}>
          <div style={{
            width: 9, height: 9, borderRadius: '50%', background: COLORS.green,
            animation: 'eka-pulse 2s ease-in-out infinite',
          }} />
          System Online
        </div>
      </header>

      {/* ════════════ BODY ════════════ */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* ──────── SIDEBAR ──────── */}
        <aside style={{
          width: 280, minWidth: 280, display: 'flex', flexDirection: 'column',
          background: 'rgba(18,18,26,0.7)', backdropFilter: 'blur(12px)',
          borderRight: `1px solid ${COLORS.border}`,
        }}>
          {/* new‑chat btn */}
          <div style={{ padding: 16 }}>
            <button onClick={newChat} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              width: '100%', padding: '11px 0',
              background: `linear-gradient(135deg, ${COLORS.accentDark}, ${COLORS.accent})`,
              color: '#fff', border: 'none', borderRadius: 10,
              fontSize: 13, fontWeight: 600, cursor: 'pointer',
              fontFamily: 'inherit',
              boxShadow: '0 2px 16px rgba(59,130,246,0.25)',
              transition: 'transform .12s, box-shadow .2s',
            }}
            onMouseEnter={e => { (e.currentTarget as HTMLElement).style.transform = 'scale(1.02)'; }}
            onMouseLeave={e => { (e.currentTarget as HTMLElement).style.transform = 'scale(1)'; }}
            >
              <IconPlus /> Nouvelle conversation
            </button>
          </div>

          {/* conversation list */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '0 8px' }}>
            {/* real conversations */}
            <div style={{ padding: '6px 10px 4px', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: COLORS.textMuted }}>Conversations</div>
            {conversations.map(c => {
              const isActive = c.id === activeId;
              const isHover = sidebarHover === c.id;
              return (
                <div key={c.id}
                  onClick={() => setActiveId(c.id)}
                  onMouseEnter={() => setSidebarHover(c.id)}
                  onMouseLeave={() => setSidebarHover(null)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '10px 12px', borderRadius: 8, cursor: 'pointer',
                    fontSize: 13, transition: 'all .15s',
                    background: isActive ? 'rgba(59,130,246,0.12)' : isHover ? 'rgba(255,255,255,0.03)' : 'transparent',
                    color: isActive ? COLORS.accent : COLORS.textSecondary,
                  }}
                >
                  <span style={{ opacity: isActive ? 1 : 0.5, flexShrink: 0 }}><IconChat /></span>
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>{c.title}</span>
                </div>
              );
            })}

            {/* sample history */}
            <div style={{ padding: '14px 10px 4px', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: COLORS.textMuted }}>Récent</div>
            {SAMPLE_HISTORY.map((h, i) => {
              const hov = sidebarHover === `s${i}`;
              return (
                <div key={i}
                  onMouseEnter={() => setSidebarHover(`s${i}`)}
                  onMouseLeave={() => setSidebarHover(null)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '10px 12px', borderRadius: 8, cursor: 'default',
                    fontSize: 13, transition: 'background .15s',
                    background: hov ? 'rgba(255,255,255,0.03)' : 'transparent',
                    color: COLORS.textMuted,
                  }}
                >
                  <span style={{ opacity: 0.4, flexShrink: 0 }}><IconChat /></span>
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>{h.title}</span>
                  <span style={{ fontSize: 10, flexShrink: 0 }}>{h.time}</span>
                </div>
              );
            })}
          </div>

          {/* user footer */}
          <div style={{
            padding: '14px 16px', borderTop: `1px solid ${COLORS.border}`,
            display: 'flex', alignItems: 'center', gap: 12,
          }}>
            <div style={{
              width: 36, height: 36, borderRadius: '50%',
              background: `linear-gradient(135deg, ${COLORS.accentDark}, ${COLORS.cyan})`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#fff', flexShrink: 0,
            }}>
              <IconUser />
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600, color: COLORS.textPrimary }}>DCM Employee</div>
              <div style={{ fontSize: 11, color: COLORS.textMuted }}>Aeronautics Div.</div>
            </div>
          </div>
        </aside>

        {/* ──────── CHAT AREA ──────── */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

          {active.messages.length === 0 && !loading ? (
            /* ── WELCOME SCREEN ── */
            <div style={{
              flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              padding: 32, gap: 20, animation: 'eka-fadeIn .6s ease',
            }}>
              <HexLogo size={72} />
              <h2 style={{ fontSize: 24, fontWeight: 700, margin: 0, color: '#fff', letterSpacing: '-0.02em' }}>
                Enterprise Knowledge Agent
              </h2>
              <p style={{ fontSize: 14, color: COLORS.textSecondary, maxWidth: 440, textAlign: 'center', lineHeight: 1.7, margin: 0 }}>
                Ask anything about your projects, documents, or draft emails.
              </p>

              {/* feature cards */}
              <div style={{ display: 'flex', gap: 16, marginTop: 8, flexWrap: 'wrap', justifyContent: 'center' }}>
                {[
                  { icon: <IconDB size={30} />, title: 'SQL Database', desc: 'Query structured data', color: '#22c55e' },
                  { icon: <IconFile size={30} />, title: 'Documents RAG', desc: 'Search knowledge base', color: '#a855f7' },
                  { icon: <IconMail size={30} />, title: 'Email Draft', desc: 'Compose messages', color: '#f59e0b' },
                ].map((f, i) => (
                  <div key={i} style={{
                    width: 170, padding: '24px 20px', borderRadius: 16,
                    background: 'rgba(30,30,46,0.55)', border: `1px solid ${COLORS.border}`,
                    backdropFilter: 'blur(12px)',
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10,
                    textAlign: 'center', transition: 'transform .25s, border-color .25s',
                    cursor: 'default',
                    animation: `eka-fadeUp .5s ease ${i * 0.1}s both`,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.borderColor = f.color; }}
                  onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.borderColor = COLORS.border; }}
                  >
                    <div style={{ color: f.color }}>{f.icon}</div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: '#fff' }}>{f.title}</div>
                    <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.4 }}>{f.desc}</div>
                  </div>
                ))}
              </div>

              {/* suggested questions */}
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center', marginTop: 16, maxWidth: 640 }}>
                {SUGGESTED_QUESTIONS.map((q, i) => (
                  <button key={i}
                    onClick={() => send(q)}
                    style={{
                      padding: '9px 18px', borderRadius: 100,
                      background: 'rgba(30,30,46,0.6)', border: `1px solid ${COLORS.border}`,
                      color: COLORS.textSecondary, fontSize: 12.5, cursor: 'pointer',
                      fontFamily: 'inherit', transition: 'all .2s',
                      backdropFilter: 'blur(8px)',
                      animation: `eka-fadeUp .5s ease ${0.3 + i * 0.07}s both`,
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = COLORS.accent; e.currentTarget.style.color = '#fff'; e.currentTarget.style.background = 'rgba(59,130,246,0.1)'; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = COLORS.border; e.currentTarget.style.color = COLORS.textSecondary; e.currentTarget.style.background = 'rgba(30,30,46,0.6)'; }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* ── MESSAGES ── */
            <div style={{ flex: 1, overflowY: 'auto', padding: '28px 28px 12px' }}>
              {active.messages.map((m, idx) => (
                <div key={m.id} style={{
                  display: 'flex', marginBottom: 22,
                  justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
                  animation: m.role === 'user' ? 'eka-slideLeft .35s ease' : 'eka-slideRight .35s ease',
                }}>
                  {/* assistant avatar */}
                  {m.role === 'assistant' && (
                    <div style={{
                      width: 36, height: 36, borderRadius: '50%', marginRight: 12, flexShrink: 0,
                      background: 'rgba(59,130,246,0.1)', border: `1px solid ${COLORS.border}`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <HexLogo size={22} />
                    </div>
                  )}

                  <div style={{ maxWidth: 640, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {/* bubble */}
                    <div style={{
                      padding: '14px 18px', borderRadius: 16,
                      fontSize: 14, lineHeight: 1.7, whiteSpace: 'pre-wrap',
                      ...(m.role === 'user' ? {
                        background: `linear-gradient(135deg, ${COLORS.userBubbleFrom}, ${COLORS.userBubbleTo})`,
                        color: '#fff',
                        borderBottomRightRadius: 4,
                        boxShadow: '0 4px 20px rgba(37,99,235,0.25)',
                      } : {
                        background: 'rgba(30,30,46,0.65)',
                        backdropFilter: 'blur(12px)',
                        border: `1px solid ${COLORS.border}`,
                        borderLeft: `3px solid rgba(59,130,246,0.5)`,
                        borderBottomLeftRadius: 4,
                        color: COLORS.textPrimary,
                      }),
                    }}>
                      <ReactMarkdown>{m.content}</ReactMarkdown>
                    </div>

                    {/* tool badges */}
                    {m.tools && m.tools.length > 0 && (
                      <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap', paddingLeft: 2 }}>
                        {m.tools.map((t, j) => {
                          const b = badgeFor(t);
                          return (
                            <span key={j} style={{
                              display: 'inline-flex', alignItems: 'center', gap: 5,
                              padding: '4px 12px', borderRadius: 100,
                              background: b.bg, color: '#fff',
                              fontSize: 11, fontWeight: 600, letterSpacing: '0.03em',
                              animation: `eka-badgePop .35s ease ${j * 0.1}s both`,
                              boxShadow: `0 2px 8px ${b.bg}88`,
                            }}>
                              <span style={{ fontSize: 13 }}>{b.emoji}</span> {b.label}
                            </span>
                          );
                        })}
                      </div>
                    )}

                    {/* timestamp */}
                    <div style={{
                      fontSize: 10, color: COLORS.textMuted,
                      textAlign: m.role === 'user' ? 'right' : 'left',
                      paddingLeft: m.role === 'user' ? 0 : 2,
                      paddingRight: m.role === 'user' ? 2 : 0,
                    }}>
                      {fmtTime(m.timestamp)}
                    </div>
                  </div>

                  {/* user avatar */}
                  {m.role === 'user' && (
                    <div style={{
                      width: 36, height: 36, borderRadius: '50%', marginLeft: 12, flexShrink: 0,
                      background: `linear-gradient(135deg, ${COLORS.accentDark}, ${COLORS.accent})`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: '#fff', fontSize: 14, fontWeight: 700,
                    }}>
                      U
                    </div>
                  )}
                </div>
              ))}

              {/* loading indicator */}
              {loading && (
                <div style={{
                  display: 'flex', justifyContent: 'flex-start', marginBottom: 22,
                  animation: 'eka-slideRight .35s ease',
                }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: '50%', marginRight: 12, flexShrink: 0,
                    background: 'rgba(59,130,246,0.1)', border: `1px solid ${COLORS.border}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <HexLogo size={22} />
                  </div>
                  <div style={{
                    padding: '16px 24px', borderRadius: 16,
                    background: 'rgba(30,30,46,0.65)', backdropFilter: 'blur(12px)',
                    border: `1px solid ${COLORS.border}`,
                    borderLeft: `3px solid rgba(59,130,246,0.5)`,
                    display: 'flex', alignItems: 'center', gap: 12,
                  }}>
                    {/* spinner */}
                    <div style={{
                      width: 18, height: 18, borderRadius: '50%',
                      border: `2px solid ${COLORS.border}`,
                      borderTopColor: COLORS.accent,
                      animation: 'eka-spin .8s linear infinite',
                    }} />
                    {/* dots */}
                    <span style={{ fontSize: 13, color: COLORS.textSecondary, display: 'flex', alignItems: 'center', gap: 3 }}>
                      Thinking
                      {[0, 1, 2].map(i => (
                        <span key={i} style={{
                          display: 'inline-block', width: 5, height: 5, borderRadius: '50%',
                          background: COLORS.accent,
                          animation: `eka-bounce 1.4s infinite ease-in-out ${-0.32 + i * 0.16}s`,
                        }} />
                      ))}
                    </span>
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>
          )}

          {/* ── INPUT BAR ── */}
          <div style={{
            padding: '14px 28px 22px',
            borderTop: `1px solid ${COLORS.border}`,
            background: 'rgba(18,18,26,0.8)', backdropFilter: 'blur(16px)',
          }}>
            <div style={{
              display: 'flex', alignItems: 'flex-end', gap: 12,
              maxWidth: 760, margin: '0 auto',
              background: COLORS.assistantBubble,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 14, padding: '5px 5px 5px 18px',
              transition: 'border-color .2s, box-shadow .2s',
            }}
            onFocus={e => { e.currentTarget.style.borderColor = COLORS.accent; e.currentTarget.style.boxShadow = `0 0 0 3px rgba(59,130,246,0.15), 0 0 20px rgba(59,130,246,0.1)`; }}
            onBlur={e => { e.currentTarget.style.borderColor = COLORS.border; e.currentTarget.style.boxShadow = 'none'; }}
            >
              <textarea
                ref={taRef}
                rows={1}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
                disabled={loading}
                placeholder="Ask about projects, procedures, or draft an email..."
                style={{
                  flex: 1, background: 'transparent', border: 'none', outline: 'none',
                  color: COLORS.textPrimary, fontSize: 14, fontFamily: 'inherit',
                  lineHeight: 1.55, resize: 'none', maxHeight: 140, padding: '9px 0',
                }}
              />
              <button
                onClick={() => send()}
                disabled={!input.trim() || loading}
                style={{
                  width: 40, height: 40, borderRadius: 10, border: 'none',
                  background: input.trim() && !loading
                    ? `linear-gradient(135deg, ${COLORS.accentDark}, ${COLORS.accent})`
                    : COLORS.border,
                  color: '#fff', cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'all .2s', flexShrink: 0,
                  boxShadow: input.trim() && !loading ? '0 2px 12px rgba(59,130,246,0.3)' : 'none',
                }}
                onMouseEnter={e => { if (input.trim() && !loading) e.currentTarget.style.transform = 'scale(1.08)'; }}
                onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; }}
              >
                <IconSend />
              </button>
            </div>
            <div style={{ textAlign: 'center', marginTop: 8, fontSize: 11, color: COLORS.textMuted }}>
              Entrée pour envoyer · Shift+Entrée pour un saut de ligne
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;