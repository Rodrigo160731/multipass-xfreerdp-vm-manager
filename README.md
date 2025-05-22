# Multipass VM Manager

Utilitário CLI para gerenciamento de VMs Ubuntu usando Multipass, com suporte à criação, inicialização, parada e conexão via RDP (Remote Desktop Protocol).

## Funcionalidades

- 📋 Listar VMs
- 🔌 Conectar via RDP (senha solicitada dinamicamente)
- ▶️ Iniciar, ⏹️ Parar, 🔁 Reiniciar VMs
- 🔍 Ver detalhes da VM
- 🆕 Criar VMs com interface gráfica e XRDP automaticamente

## Requisitos

- **Sistema Operacional:** Linux
- **Pacotes necessários:**
  - `multipass`
  - `freerdp2-x11`
  - `python3` (>= 3.7)

Instale com:

```bash
sudo apt update
sudo apt install -y freerdp2-x11 python3
```

## Como usar

Clone este repositório e execute o script principal:

```bash
git clone https://github.com/Rodrigo160731/multipass-xfreerdp-vm-manager.git
cd multipass-vm-manager
python3 main.py
```

## Segurança

- A senha do usuário `ubuntu` **não é armazenada** em nenhum momento.
- Toda operação que envolve autenticação (como acesso via RDP ou criação de VM) solicita a senha **dinamicamente** no terminal.
- Isso evita exposição de credenciais sensíveis no código-fonte.

## Observações

- As VMs são criadas com Ubuntu Desktop + XRDP já instalados.
- Durante a criação, será solicitado:
  - Nome da VM
  - Versão do Ubuntu
  - Tamanho de memória e disco
  - Senha para o usuário `ubuntu`

## Licença

Este projeto está licenciado sob a [The Unlicense](https://unlicense.org/).

Você é livre para usar, modificar e distribuir este software sem restrições.

---
