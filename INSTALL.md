# Guia de Instalação e Pré-requisitos

Para que o **IA-IaC Governor** e seus testes (incluindo o pre-commit) funcionem perfeitamente no seu ambiente local, você precisa ter as ferramentas abaixo instaladas no seu sistema operacional e mapeadas no seu `PATH`.

---

## 1. Terraform (Obrigatório)
O Terraform é usado ativamente pela nossa engine (`GovernanceManagerTool`) para converter o código HCL em arquivos JSON estruturados antes de enviar para o Agente analisar.

### 🪟 Windows
Se você usa o **Winget** (Gerenciador de Pacotes nativo do Windows 10/11 - *Recomendado*):
```powershell
winget install Hashicorp.Terraform
```

*(Se preferir o Chocolatey)*: 
Caso você não tenha o `choco` instalado ou não tenha privilégios de Administrador, instale o Chocolatey de forma local no seu usuário com o comando abaixo:
```powershell
$env:ChocolateyInstall="$env:USERPROFILE\AppData\Local\chocoportable"; Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
Após instalar, feche e abra o terminal novamente e instale o Terraform:
```powershell
choco install terraform -y
```

*(Se preferir o Scoop)*:
```powershell
scoop install terraform
```
*(Alternativa Manual):* Baixe o executável em [terraform.io](https://developer.hashicorp.com/terraform/downloads), extraia o arquivo `terraform.exe` e adicione a pasta nas Variáveis de Ambiente (`PATH`).

### 🍎 macOS (via Homebrew)
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

### 🐧 Linux (Ubuntu/Debian)
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

---

## 2. OPA - Open Policy Agent (Recomendado)
O OPA é o motor determinístico utilizado na plataforma para barrar "Hard Policies".

### 🪟 Windows
```powershell
# Via Scoop
scoop install opa

# Via Download Manual (PowerShell Admin)
Invoke-WebRequest -Uri "https://openpolicyagent.org/downloads/v0.61.0/opa_windows_amd64.exe" -OutFile "opa.exe"
# Mova o opa.exe para alguma pasta que esteja no seu PATH
```

### 🍎 macOS
```bash
brew install opa
```

### 🐧 Linux
```bash
curl -L -o opa https://openpolicyagent.org/downloads/v0.61.0/opa_linux_amd64_static
chmod +x opa
sudo mv opa /usr/local/bin/
```

---

## 3. Python 3.10+ (Obrigatório)
O projeto é baseado em Python. Você precisa da versão 3.10 ou superior.

* **Windows:** Baixe o instalador no [python.org](https://www.python.org/downloads/windows/). Certifique-se de marcar a opção **"Add python.exe to PATH"** durante a instalação.
* **macOS:** `brew install python`
* **Linux:** `sudo apt install python3 python3-pip`

---

## 4. Configuração Final do Repositório

Após instalar os executáveis acima, instale as bibliotecas Python do projeto e ative os githooks:

```bash
# 1. Instalar as dependências do projeto (CrewAI, Langchain, etc)
pip install -r requirements.txt

# 2. Habilitar o hook de segurança (evita commits de infra vulnerável)
pre-commit install
```

Para validar se tudo está funcionando corretamente na sua máquina, tente rodar a esteira de validação:

```bash
# Deve rodar e passar pelos exemplos sem pular (SKIPPED) o Terraform
python test_examples.py
```
