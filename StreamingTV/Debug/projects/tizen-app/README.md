# App Tizen para Samsung TV

Este é o app instalável para Samsung Smart TV (Tizen OS, modelos 2017+).

## Como instalar (Modo Desenvolvedor — sem loja)

### Pré-requisitos
- Tizen Studio instalado no PC: https://developer.tizen.org/development/tizen-studio/download
- TV Samsung e PC na **mesma rede Wi-Fi**
- Descobrir o **IP do PC** no servidor: `ipconfig` → IPv4 da rede local (ex: 192.168.1.100)

### Passo 1: Ativar Modo Desenvolvedor na TV
1. Na TV, abra **Smart Hub → Apps**
2. No teclado numérico do controle, digite **12345** — abre a tela de Dev Mode
3. Ligue **Developer Mode** e insira o **IP do PC**
4. Reinicie a TV quando solicitado

### Passo 2: Conectar pelo Tizen Studio
1. No Tizen Studio, abra **Device Manager**
2. Clique **Remote Device Manager** → **Scan** → selecione sua TV → Connect
3. A TV pedirá confirmação na tela — aceite

### Passo 3: Empacotar o app
**Alternativa sem terminal:** No Tizen Studio, importe a pasta como "Tizen Web Project" e use Project → Build Signed Package.

Ou via CLI (`tz.exe` incluso no Tizen Extension, não no Tizen Studio clássico):
```bash
tz package -t wgt -s MeuCertificado -- .
# Gera: StreamingTV.wgt
```

### Passo 4: Instalar na TV
Use o script `deploy.ps1` — ele usa `tz install-chain`, que atualiza o app sem tentar desinstalá-lo primeiro:
```powershell
powershell -File "streaming-server\StreamingTV\deploy.ps1"
```

> **Não use** `tz install` diretamente — veja armadilhas abaixo.

### Passo 5: Usar o app
1. O app abre uma tela pedindo o **endereço do servidor**
2. Digite o IP do PC onde o servidor roda (ex: `192.168.1.100` ou `192.168.1.100:8080`)
3. Clique Conectar — o endereço fica salvo automaticamente
4. Da próxima vez o app conecta direto, sem pedir novamente

### Para resetar o endereço salvo
Pressione o botão **Voltar** na tela principal do app.

## Observações
- O servidor de streaming precisa estar rodando no PC
- TV e PC devem estar na mesma rede
- Se mudar de rede/IP, basta abrir o app e pressionar Voltar para reconfigurar

---

## ⚠️ Armadilhas conhecidas (aprendidas na prática)

### `install failed[118, -19] Parsing error` — package ID com tamanho errado

O atributo `package=` no `config.xml` exige **exatamente 10 caracteres alfanuméricos**. A TV rejeita qualquer outro tamanho com `Parsing error` — sem indicar o motivo. Passamos horas depurando esse erro antes de descobrir que o package estava com 8 caracteres.

**Regra:** nunca altere o `package=` no `config.xml`. O valor atual (`PedroStrmX`) tem exatamente 10 chars e funciona.

---

### `tz install` falha silenciosamente — use `tz install-chain`

`tz install` tenta desinstalar o app via `vd_appuninstall` antes de instalar. Essa operação está **bloqueada** na TV (acesso SDB restrito), então o comando falha sem mensagem clara.

`tz install-chain` pula o uninstall e atualiza o app diretamente — use sempre esse. O `deploy.ps1` já faz isso.

---

### URLs externas saem do app e abrem o browser da TV

O `config.xml` precisa ter:
```xml
<access origin="*" subdomains="true"/>
```
Sem isso, qualquer `window.location.href` para URL externa abandona o app e abre o browser nativo da Samsung. Descobrimos isso ao tentar navegar para o servidor de streaming dentro do app.

---

### `<iframe>` não recebe eventos do controle remoto

Tentamos carregar o servidor via `<iframe>` dentro do app Tizen. Funciona para exibir conteúdo, mas os eventos de teclado do controle remoto (navegação, Enter, Voltar) não são repassados ao iframe por restrição cross-origin.

A solução foi abandonar o iframe e usar `window.location.href` com `<access origin="*"/>` — o app navega diretamente para a URL do servidor.
