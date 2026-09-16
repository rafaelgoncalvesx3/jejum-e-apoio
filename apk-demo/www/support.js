const riskRx=/(quero morrer|me matar|vou me matar|suicid|acabar com minha vida|não quero viver|me machucar|ferir a mim)/i;
function supportReply(text){
  const t=text.toLowerCase();
  if(riskRx.test(text)) return 'Sinto muito que isso esteja tão pesado agora. Eu posso continuar aqui com você, mas este é um momento para envolver uma pessoa de verdade também. Procure alguém de confiança agora e, se houver risco imediato, acione o atendimento de emergência. No Brasil, o CVV atende pelo 188 para apoio emocional.';
  if(/ansios|ansiedade|nervos|agoni/.test(t)) return 'Vamos reduzir o tamanho do problema por alguns minutos. Tente notar 5 coisas que você vê, 4 que pode tocar, 3 que ouve, 2 cheiros e 1 sabor. Depois escolha uma ação pequena e concreta: beber água, sentar um pouco ou falar com alguém. O que parece mais possível agora?';
  if(/desmot|desist|sem vontade|cansad/.test(t)) return 'Você não precisa recuperar toda a motivação de uma vez. Escolha uma ação de 5 minutos que ajude o “você de amanhã”. Pode ser beber água, preparar uma refeição simples, caminhar um pouco ou apenas registrar como está se sentindo.';
  if(/saí|sai |falhei|errei|comi|exagerei|rotina/.test(t)) return 'Uma refeição ou um dia fora da rotina não define seu progresso. Evite compensações extremas. O próximo passo pode ser simplesmente retomar a próxima refeição, hidratação ou horário habitual.';
  if(/vitória|vitoria|consegui|orgulh|bom dia|melhorei/.test(t)) return 'Isso merece ser reconhecido. ⭐ Registre o que você fez e, principalmente, o que tornou essa vitória possível. Repetir o processo costuma ser mais útil do que buscar perfeição.';
  return 'Obrigado por contar isso. Tente separar o que você está sentindo do que precisa resolver agora. Qual seria o menor próximo passo que deixaria os próximos 10 minutos um pouco melhores?';
}
function addChat(role,text){state.chat.push({role,text,ts:Date.now()});state.chat=state.chat.slice(-40);saveState();renderChat()}
function renderChat(){const c=document.getElementById('chat');if(!state.chat.length){state.chat=[{role:'bot',text:'Oi. Eu sou o Companheiro de Apoio. Posso te ajudar a reorganizar o próximo passo sem julgamentos. Como você está agora?',ts:Date.now()}];saveState()}c.innerHTML=state.chat.map(m=>`<div class="bubble ${m.role}">${escapeHtml(m.text)}</div>`).join('');c.scrollTop=c.scrollHeight}
function sendSupport(text){text=text.trim();if(!text)return;addChat('user',text);if(riskRx.test(text))document.getElementById('helpCard').classList.remove('hidden');setTimeout(()=>addChat('bot',supportReply(text)),180)}
