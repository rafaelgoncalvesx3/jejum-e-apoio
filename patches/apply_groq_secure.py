from pathlib import Path
import re, json
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else 'full-app')

pkg_path = root/'package.json'
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
for dep in ['@google/genai', '@capgo/capacitor-social-login']:
    pkg.get('dependencies', {}).pop(dep, None)
pkg['name'] = 'jejum-e-apoio'
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

(root/'scripts/patch-android.mjs').write_text(r'''import fs from 'fs';
import path from 'path';
const root = process.cwd();
const javaDir = path.join(root, 'android', 'app', 'src', 'main', 'java', 'br', 'com', 'rafaelgoncalves', 'jejumapoio');
fs.mkdirSync(javaDir, { recursive: true });
fs.writeFileSync(path.join(javaDir, 'MainActivity.java'), `package br.com.rafaelgoncalves.jejumapoio;\n\nimport com.getcapacitor.BridgeActivity;\n\npublic class MainActivity extends BridgeActivity {}\n`);
const manifestPath = path.join(root, 'android', 'app', 'src', 'main', 'AndroidManifest.xml');
if (fs.existsSync(manifestPath)) {
  let m = fs.readFileSync(manifestPath, 'utf8');
  if (!m.includes('android:usesCleartextTraffic')) m = m.replace('<application', '<application android:usesCleartextTraffic="true"');
  fs.writeFileSync(manifestPath, m);
}
console.log('Android ajustado para servidor seguro Groq/comunidade.');
''', encoding='utf-8')

services = root/'src/services'
services.mkdir(parents=True, exist_ok=True)
(services/'groq.ts').write_text(r'''const BACKEND_KEY = 'jejum_community_url_v1';
export function getBackendUrl(): string {
  return (localStorage.getItem(BACKEND_KEY) || import.meta.env.VITE_BACKEND_URL || '').trim().replace(/\/$/, '');
}
export async function checkGroqStatus(baseUrl?: string): Promise<{ configured: boolean; model?: string }> {
  const base = (baseUrl || getBackendUrl()).replace(/\/$/, '');
  if (!base) return { configured: false };
  const response = await fetch(`${base}/api/ai/status`);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body?.error || `Servidor IA indisponível (${response.status})`);
  return { configured: !!body.configured, model: body.model };
}
export async function groqGenerateText(prompt: string, systemInstruction?: string, baseUrl?: string): Promise<string> {
  const base = (baseUrl || getBackendUrl()).replace(/\/$/, '');
  if (!base) throw new Error('Configure o endereço do servidor seguro em Apoio & Comunidade.');
  const response = await fetch(`${base}/api/ai/chat`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt, systemInstruction }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body?.error || `Falha na IA (${response.status})`);
  const text = String(body?.text || '').trim();
  if (!text) throw new Error('A Groq não retornou uma resposta de texto.');
  return text;
}
''', encoding='utf-8')
try: (services/'gemini.ts').unlink()
except FileNotFoundError: pass

p = root/'src/components/SupportHub.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace('  LogIn, LogOut, MessageCircle, Plus, RefreshCw, Send, Settings, ShieldAlert,\n', '  MessageCircle, Plus, RefreshCw, Send, Settings, ShieldAlert,\n')
s = re.sub(r"import \{\n  GeminiSettings, getGeminiSession, getGeminiSettings, geminiGenerateText,\n  loginWithGoogleGemini, logoutGoogleGemini, saveGeminiSettings\n\} from '../services/gemini';", "import { checkGroqStatus, groqGenerateText } from '../services/groq';", s)
s = s.replace("  const [geminiSettings, setGeminiSettings] = useState<GeminiSettings>(() => getGeminiSettings());\n  const [geminiSession, setGeminiSession] = useState(() => getGeminiSession());\n", "  const [aiOnline, setAiOnline] = useState(false);\n  const [aiModel, setAiModel] = useState('');\n")
s = s.replace("  const aiConnected = !!geminiSession?.accessToken;", "  const aiConnected = aiOnline;")
s = s.replace("    } else if (aiConnected) {", "    } else if (communityUrl) {")
s = s.replace("reply = await geminiGenerateText(`Conversa recente:\\n${history}\\n\\nResponda à última mensagem do usuário.`, systemPrompt);", "reply = await groqGenerateText(`Conversa recente:\\n${history}\\n\\nResponda à última mensagem do usuário.`, systemPrompt, communityUrl);")
s = s.replace("reply = `${offlineReply(text)}\\n\\n(Modo local: ${e?.message || 'Gemini indisponível'})`;", "reply = `${offlineReply(text)}\\n\\n(Modo local: ${e?.message || 'Groq indisponível'})`;")
m = re.search(r"\n  const handleGoogleLogin = async \(\) => \{.*?\n  \};\n\n  const saveSettings = \(\) => \{.*?\n  \};", s, re.S)
if not m: raise SystemExit('SupportHub login/settings block not found')
replacement = r'''
  const testAiConnection = async (url = communityUrl) => {
    const clean = url.trim().replace(/\/$/, '');
    if (!clean) { setAiOnline(false); setAiModel(''); return; }
    try {
      const status = await checkGroqStatus(clean);
      setAiOnline(status.configured);
      setAiModel(status.model || '');
    } catch {
      setAiOnline(false);
      setAiModel('');
    }
  };
  useEffect(() => { if (communityUrl) testAiConnection(communityUrl); }, []);
  const saveSettings = async () => {
    const clean = communityUrl.trim().replace(/\/$/, '');
    localStorage.setItem(COMMUNITY_URL_KEY, clean);
    setCommunityUrl(clean);
    await testAiConnection(clean);
    setSettingsOpen(false);
  };'''
s = s[:m.start()] + '\n' + replacement + s[m.end():]
s = s.replace("{aiConnected?'● Gemini conectado':'○ IA em modo local'}", "{aiConnected?`● Groq conectada${aiModel ? ` • ${aiModel}` : ''}`:'○ IA em modo local'}")
s = s.replace('Conectar Gemini', 'Configurar IA')
s = s.replace('Gemini via Google e servidor da comunidade', 'Groq protegida no servidor e comunidade')
start_marker = '<div className="p-4 rounded-2xl bg-slate-950 border border-slate-800"><div className="flex items-center gap-2 mb-3"><Sparkles className="w-5 h-5 text-cyan-400"/><h3 className="font-bold text-white">Gemini com Conta Google</h3></div>'
next_marker = '<div className="p-4 rounded-2xl bg-slate-950 border border-slate-800"><div className="flex items-center gap-2 mb-3"><Cloud className="w-5 h-5 text-emerald-400"/><h3 className="font-bold text-white">Servidor da comunidade</h3></div>'
si = s.find(start_marker); ni = s.find(next_marker, si)
if si < 0 or ni < 0: raise SystemExit('SupportHub settings cards not found')
new_card = '''<div className="p-4 rounded-2xl bg-slate-950 border border-slate-800"><div className="flex items-center gap-2 mb-3"><Sparkles className="w-5 h-5 text-cyan-400"/><h3 className="font-bold text-white">Groq IA protegida</h3></div><p className="text-xs text-slate-400 leading-relaxed">A chave da Groq não fica no APK. Ela é guardada somente no servidor como <span className="font-mono text-emerald-300">GROQ_API_KEY</span>.</p><div className={`mt-3 text-xs flex items-center gap-2 ${aiConnected?'text-emerald-300':'text-amber-300'}`}><CheckCircle2 className="w-4 h-4"/>{aiConnected?`Groq pronta${aiModel?` • ${aiModel}`:''}`:'Servidor sem Groq configurada ou inacessível'}</div></div>\n        '''
s = s[:si] + new_card + s[ni:]
s = s.replace('Servidor da comunidade</h3>', 'Servidor seguro (IA + comunidade)</h3>')
s = s.replace('Para teste na mesma Wi‑Fi, use o IP do computador, por exemplo: http://192.168.0.10:3000', 'Use o endereço do servidor que guarda a chave Groq. Na mesma Wi‑Fi, por exemplo: http://192.168.0.10:3000')
p.write_text(s, encoding='utf-8')

p = root/'src/components/PantryAndDiet.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace("import { geminiGenerateText, getGeminiSession } from '../services/gemini';\n", "import { getBackendUrl } from '../services/groq';\n")
start = s.find('  const handleGenerateDiet = async () => {'); end = s.find('\n\n  const handleCopyPlan = () => {', start)
if start < 0 or end < 0: raise SystemExit('Pantry handleGenerateDiet not found')
new_func = r'''  const handleGenerateDiet = async () => {
    if (pantryItems.length === 0) { setErrorMessage('Adicione pelo menos 1 ou 2 alimentos que você tem em casa para montar o cardápio.'); return; }
    setErrorMessage(null); setIsLoading(true); playNotificationChime('click');
    const backendUrl = getBackendUrl();
    if (!backendUrl) {
      onSaveDietPlan(buildLocalPlan()); setErrorMessage('Servidor de IA não configurado: foi criado um cardápio local. Configure o servidor em Apoio & Comunidade.'); setIsLoading(false); return;
    }
    try {
      const response = await fetch(`${backendUrl}/api/diet/suggest`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients: pantryItems, profile: { weight: userProfile.weightKg, height: userProfile.heightCm, age: calculateAge(userProfile.birthDate), gender: userProfile.gender }, fastingProtocol: currentFastingProtocol, goal, dietaryPreference: preference, mealsPerDay: mealsCount }),
      });
      const data = await response.json();
      if (!response.ok || !data?.plan) throw new Error(data?.error || `Servidor respondeu ${response.status}`);
      onSaveDietPlan({ ...data.plan, generatedAt: new Date().toISOString() });
      if (data.source !== 'ai') setErrorMessage('A IA estava indisponível; foi usado o plano local seguro do servidor.');
      playNotificationChime('fast_complete');
    } catch (err: any) {
      onSaveDietPlan(buildLocalPlan()); setErrorMessage(`Groq indisponível (${err?.message || 'erro'}). Foi usado o modo local.`);
    } finally { setIsLoading(false); }
  };'''
s = s[:start] + new_func + s[end:]
p.write_text(s, encoding='utf-8')

p = root/'server.ts'
s = p.read_text(encoding='utf-8')
s = s.replace("import { GoogleGenAI, Type } from '@google/genai';\n", '')
insert_at = s.find('// Health check endpoint')
if insert_at < 0: raise SystemExit('Health marker not found')
server_helper = r'''const GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions';
const DEFAULT_GROQ_MODEL = process.env.GROQ_MODEL || 'llama-3.3-70b-versatile';
async function groqChat(messages: Array<{ role: 'system' | 'user' | 'assistant'; content: string }>, options: { temperature?: number; maxTokens?: number } = {}) {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) throw new Error('GROQ_API_KEY_NOT_CONFIGURED');
  const response = await fetch(GROQ_API_URL, {
    method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
    body: JSON.stringify({ model: DEFAULT_GROQ_MODEL, messages, temperature: options.temperature ?? 0.5, max_completion_tokens: options.maxTokens ?? 1400 }),
  });
  const body: any = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body?.error?.message || `Groq HTTP ${response.status}`);
  const text = String(body?.choices?.[0]?.message?.content || '').trim();
  if (!text) throw new Error('Groq retornou resposta vazia.');
  return text;
}
app.get('/api/ai/status', (_req, res) => { res.json({ success: true, provider: 'groq', configured: !!process.env.GROQ_API_KEY, model: DEFAULT_GROQ_MODEL }); });
app.post('/api/ai/chat', async (req, res) => {
  try {
    const prompt = String(req.body?.prompt || '').trim().slice(0, 12000);
    const systemInstruction = String(req.body?.systemInstruction || '').trim().slice(0, 8000);
    if (!prompt) return res.status(400).json({ error: 'Mensagem vazia.' });
    if (!process.env.GROQ_API_KEY) return res.status(503).json({ error: 'Groq não configurada no servidor.' });
    const messages: Array<{ role: 'system' | 'user'; content: string }> = [];
    if (systemInstruction) messages.push({ role: 'system', content: systemInstruction });
    messages.push({ role: 'user', content: prompt });
    const text = await groqChat(messages, { temperature: 0.55, maxTokens: 1000 });
    return res.json({ success: true, provider: 'groq', model: DEFAULT_GROQ_MODEL, text });
  } catch (error: any) { console.error('Groq chat error:', error); return res.status(502).json({ error: error?.message || 'Falha ao consultar Groq.' }); }
});

'''
s = s[:insert_at] + server_helper + s[insert_at:]
start_marker = "    const apiKey = process.env.GEMINI_API_KEY;"; end_marker = "    const parsedData = JSON.parse(resultText);"
si = s.find(start_marker); ei = s.find(end_marker, si)
if si < 0 or ei < 0: raise SystemExit('Gemini diet block markers not found')
ei += len(end_marker)
replacement = r'''    if (!process.env.GROQ_API_KEY) {
      return res.json({ success: true, source: 'fallback', plan: generateFallbackPlan(ingredients, profile, fastingProtocol, goal) });
    }
    const userMetrics = `\nPeso: ${profile.weight || 75} kg\nAltura: ${profile.height || 175} cm\nIdade: ${profile.age || 30} anos\nSexo: ${profile.gender || 'não especificado'}\nProtocolo de Jejum: ${fastingProtocol}\nObjetivo: ${goal}\nPreferência alimentar: ${dietaryPreference}\nNúmero de refeições: ${mealsPerDay}\nAlimentos disponíveis em casa: ${ingredients.join(', ')}\n`;
    const prompt = `Com base prioritariamente nos alimentos disponíveis, crie um plano alimentar geral e prático.\nDados do usuário:\n${userMetrics}\nRegras:\n- Não diagnostique nem prescreva tratamento.\n- Não incentive jejum prolongado, punição, compensação ou restrição extrema.\n- Responda SOMENTE JSON válido, sem markdown.\n- Use este formato exato:\n{"title":"","summary":"","estimatedDailyCalories":0,"macros":{"proteinsGrams":0,"carbsGrams":0,"fatsGrams":0},"meals":[{"mealName":"","recommendedTime":"","description":"","usedIngredients":[""],"optionalAdditions":[""],"instructions":""}],"fastingTips":[""],"hydrationRecommendationMl":0}`;
    const resultText = await groqChat([
      { role: 'system', content: 'Você é um assistente de organização alimentar e culinária prática. Fale em português do Brasil. Não diagnostique doenças, não prescreva tratamento e responda apenas JSON válido.' },
      { role: 'user', content: prompt },
    ], { temperature: 0.35, maxTokens: 2200 });
    const cleaned = resultText.replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/```$/i, '').trim();
    const parsedData = JSON.parse(cleaned);'''
s = s[:si] + replacement + s[ei:]
s = s.replace('// Gemini AI: Suggest Diet & Meal Plan based on available pantry items and user health metrics', '// Groq AI: Suggest Diet & Meal Plan via server-side secret')
s = s.replace("console.error('Error generating diet plan with AI:', error);", "console.error('Error generating diet plan with Groq:', error);")
p.write_text(s, encoding='utf-8')

(root/'.env.example').write_text('# Chave secreta SOMENTE no servidor. Nunca coloque no APK/frontend.\nGROQ_API_KEY=gsk_COLE_SUA_CHAVE_AQUI\nGROQ_MODEL=llama-3.3-70b-versatile\nPORT=3000\n', encoding='utf-8')
(root/'CONFIGURAR_GROQ_SERVIDOR.bat').write_text(r'''@echo off
cd /d "%~dp0"
title Configurar Groq - Jejum & Apoio
set /p GROQKEY=COLE SUA CHAVE GROQ (ela ficara somente neste computador): 
if "%GROQKEY%"=="" (
  echo Chave vazia. Nada foi alterado.
  pause
  exit /b 1
)
(
  echo GROQ_API_KEY=%GROQKEY%
  echo GROQ_MODEL=llama-3.3-70b-versatile
  echo PORT=3000
)> .env
echo.
echo Chave salva no .env local. NAO envie esse arquivo ao GitHub.
echo Agora execute INICIAR_SERVIDOR_COMUNIDADE.bat.
pause
''', encoding='utf-8')
p = root/'INICIAR_SERVIDOR_COMUNIDADE.bat'
if p.exists():
    t = p.read_text(encoding='utf-8', errors='ignore').replace('Rede de Apoio - Servidor Local', 'Jejum & Apoio - Servidor Groq + Comunidade').replace('Iniciando servidor na porta 3000...', 'Iniciando servidor Groq + comunidade na porta 3000...')
    p.write_text(t, encoding='utf-8')
p = root/'.gitignore'; gi = p.read_text(encoding='utf-8') if p.exists() else ''
if '.env' not in gi.splitlines(): gi += '\n.env\n'
p.write_text(gi, encoding='utf-8')
print('OK: Groq secure backend patch applied')
