# Jejum & Apoio

Aplicativo para Android/Web focado em organização de hábitos: jejum, hidratação, alimentação, atividade física, acompanhamento de progresso e uma área de apoio para momentos de ansiedade ou desmotivação.

## Principais recursos

- Controle de jejum e hidratação.
- Registro de peso, IMC, atividades e medicamentos.
- Cardápio e receitas com fallback local.
- **Companheiro de Apoio** com modo offline e integração opcional ao Gemini.
- Check-in de humor e diário emocional local.
- **Rede de Apoio** local ou compartilhada por um servidor Express.
- Login Google/OAuth preparado para a Google Generative Language API.
- Projeto Android com Capacitor 8.

## APK automático pelo GitHub

O workflow `.github/workflows/build-apk.yml` compila um APK debug. Em **Actions**, abra **Build APK - Jejum e Apoio** e baixe o artefato `Jejum-e-Apoio-TESTE`. O artefato inclui:

- `app-debug.apk`
- `android-signing-report.txt` com o SHA-1 da assinatura de teste
- `apk-sha256.txt`

O SHA-1 é necessário para cadastrar o OAuth Client ID Android no Google Cloud para o pacote `br.com.rafaelgoncalves.jejumapoio`.

## Google / Gemini

O app funciona sem Gemini em modo local. Para ativar **Entrar com Google** + Gemini:

1. Habilite a **Google Generative Language API** no Google Cloud.
2. Configure a tela de consentimento OAuth e adicione os usuários de teste.
3. Crie um **OAuth Client ID Web** e informe-o nas configurações do app.
4. Crie um **OAuth Client ID Android** com o package name `br.com.rafaelgoncalves.jejumapoio` e o SHA-1 do APK instalado.
5. Informe o **Google Cloud Project ID** nas configurações do app.

O modelo padrão atual configurado é `gemini-3.8-flash`.

## Desenvolvimento local

Requisitos: Node.js 22+.

```bash
npm install
npm run dev
```

Para gerar apenas a interface web:

```bash
npm run build:web
```

Para Android, veja `GERAR_APK_GITHUB.txt` ou execute `CRIAR_APK.bat` em um Windows com Android SDK instalado.

## Observação sobre saúde e apoio

O Companheiro de Apoio oferece suporte motivacional e organização de hábitos, não substitui atendimento médico ou psicológico. Mensagens que indiquem risco imediato recebem orientação para procurar apoio humano e serviços de emergência.
