const STORE_KEY='jejumApoioDemoV1';
const defaults={water:0,fastStart:null,lastMood:'',moods:[],chat:[],posts:[],journal:[],group:'Geral',dark:false,nickname:'',wins:0};
function loadState(){try{return {...defaults,...JSON.parse(localStorage.getItem(STORE_KEY)||'{}')}}catch{return {...defaults}}}
let state=loadState();
function saveState(){localStorage.setItem(STORE_KEY,JSON.stringify(state))}
function nowLabel(ts=Date.now()){return new Date(ts).toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})}
function escapeHtml(v=''){return String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
function toast(msg){const el=document.getElementById('toast');el.textContent=msg;el.classList.add('show');clearTimeout(window._tt);window._tt=setTimeout(()=>el.classList.remove('show'),2200)}
