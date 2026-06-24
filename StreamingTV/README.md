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
```bash
# No terminal, na pasta tizen-app/:
cd streaming-server/tizen-app

# Instale a CLI do Tizen (inclusa no Tizen Studio):
# Windows: C:\tizen-studio\tools\ide\bin\tizen.bat

tizen package -t wgt -s MeuCertificado -- .
# Isso gera: Streaming.wgt
```

**Alternativa sem terminal:** No Tizen Studio, importe a pasta como "Tizen Web Project" e use Project → Build Signed Package.

### Passo 4: Instalar na TV
```bash
tizen install -n Streaming.wgt -t TizenTV
```
Ou pelo Device Manager: clique com botão direito na TV conectada → Install App → selecione o .wgt

### Passo 5: Usar o app
1. O app abre uma tela pedindo o **endereço do servidor**
2. Digite o IP do PC onde o servidor roda (ex: `192.168.1.100` ou `192.168.1.100:80`)
3. Clique Conectar — o endereço fica salvo automaticamente
4. Da próxima vez o app conecta direto, sem pedir novamente

### Para resetar o endereço salvo
Pressione o botão **Voltar** na tela principal do app.

## Observações
- O servidor de streaming precisa estar rodando no PC
- TV e PC devem estar na mesma rede
- Se mudar de rede/IP, basta abrir o app e pressionar Voltar para reconfigurar
