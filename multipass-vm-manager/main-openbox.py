import subprocess
import json
import os

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def listar_vms():
    try:
        resultado = subprocess.check_output(["multipass", "list", "--format", "json"])
        vms_dict = json.loads(resultado.decode("utf-8"))
        return vms_dict.get("list", [])
    except subprocess.CalledProcessError as e:
        print(f"Erro ao listar VMs: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return []

def mostrar_vms(vms):
    limpar_tela()
    if not vms:
        print("Nenhuma VM encontrada.")
        return
    print("Lista de VMs:")
    for i, vm in enumerate(vms):
        name = vm.get("name")
        state = vm.get("state")
        ips = vm.get("ipv4", [])
        ip_str = ", ".join(ips) if ips else "sem IP"
        print(f"{i} - {name}: Estado: {state}, IP(s): {ip_str}")
    print()

def conectar_rdp(comando):
    print(f"Iniciando conexão RDP com: {comando}")
    subprocess.Popen(comando.split())

def menu_conectar(vms):
    mostrar_vms(vms)
    if not vms:
        input("Pressione Enter para voltar ao menu...")
        return None

    try:
        escolha = int(input("Escolha a VM (número): "))
        vm = vms.pop(escolha)
    except (ValueError, IndexError):
        print("Escolha inválida!")
        input("Pressione Enter para voltar ao menu...")
        return None

    print(f"Você escolheu: {vm['name']}")

    ips = vm.get("ipv4", [])
    if not ips:
        print("A VM está desligada ou sem IP.")
        input("Pressione Enter para voltar ao menu...")
        return None

    full_screen = input("Tela cheia? (S/n): ").strip().lower()
    if full_screen == 's' or full_screen == '':
        comando = f"xfreerdp3 /u:ubuntu /p:0731 /v:{ips[0]} /f"
    else:
        comando = f"xfreerdp3 /u:ubuntu /p:0731 /v:{ips[0]}"

    return comando

def iniciar_vm(vms):
    mostrar_vms(vms)
    try:
        escolha = int(input("Escolha a VM para iniciar (número): "))
        vm = vms[escolha]
    except (ValueError, IndexError):
        print("Escolha inválida!")
        input("Pressione Enter para voltar ao menu...")
        return

    if vm["state"].lower() == "running":
        print("A VM já está em execução.")
    else:
        print(f"Iniciando VM {vm['name']}...")
        subprocess.run(["multipass", "start", vm["name"]])
        print("VM iniciada.")

    input("Pressione Enter para voltar ao menu...")

def parar_vm(vms):
    mostrar_vms(vms)
    try:
        escolha = int(input("Escolha a VM para parar (número): "))
        vm = vms[escolha]
    except (ValueError, IndexError):
        print("Escolha inválida!")
        input("Pressione Enter para voltar ao menu...")
        return

    if vm["state"].lower() == "stopped":
        print("A VM já está parada.")
    else:
        print(f"Parando VM {vm['name']}...")
        subprocess.run(["multipass", "stop", vm["name"]])
        print("VM parada.")

    input("Pressione Enter para voltar ao menu...")

def reiniciar_vm(vms):
    mostrar_vms(vms)
    try:
        escolha = int(input("Escolha a VM para reiniciar (número): "))
        vm = vms[escolha]
    except (ValueError, IndexError):
        print("Escolha inválida!")
        input("Pressione Enter para voltar ao menu...")
        return

    print(f"Reiniciando VM {vm['name']}...")
    subprocess.run(["multipass", "restart", vm["name"]])
    print("VM reiniciada.")
    input("Pressione Enter para voltar ao menu...")

def detalhes_vm(vms):
    mostrar_vms(vms)
    try:
        escolha = int(input("Escolha a VM para ver detalhes (número): "))
        vm = vms[escolha]
    except (ValueError, IndexError):
        print("Escolha inválida!")
        input("Pressione Enter para voltar ao menu...")
        return

    print(json.dumps(vm, indent=4))
    input("Pressione Enter para voltar ao menu...")

def criar_vm():
    limpar_tela()
    print("Listando VMs existentes:\n")
    subprocess.run(["multipass", "list"])
    print()

    name = input("Qual o nome do servidor? ").strip()

    # Verificar se já existe VM com esse nome
    resultado = subprocess.run(["multipass", "info", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if resultado.returncode == 0:
        resposta = input(f"⚠️ Já existe uma VM chamada '{name}'. Deseja usar essa VM existente? (s/n): ").strip().lower()
        if resposta != 's':
            print("Cancelado.")
            input("Pressione Enter para voltar ao menu...")
            return
    else:
        version = input("Qual a versão do Ubuntu (ex: 22.04)? ").strip()
        memory = input("Qual o tamanho da memória (em GB, ex: 3)? ").strip()
        disk = input("Qual o tamanho do disco (em GB, ex: 25)? ").strip()

        print(f"\nCriando o servidor '{name}' com Ubuntu {version}, {memory} GB de memória e {disk} GB de disco...\n")
        subprocess.run(["multipass", "launch", version, "--name", name, "--memory", f"{memory}G", "--disk", f"{disk}G"])

    print("\nInstalando XRDP + Openbox + xterm...")
    subprocess.run(["multipass", "exec", name, "--", "sudo", "apt", "update", "-y"])
    subprocess.run(["multipass", "exec", name, "--", "sudo", "apt", "install", "-y", "xrdp", "openbox", "xterm", "x11-xserver-utils", "firefox"])

    print("\nConfigurando sessão gráfica com Openbox...")
    #subprocess.run(["multipass", "exec", name, "--", "bash", "-c", 'echo "exec openbox-session" > /home/ubuntu/.xsession'])
    subprocess.run(["multipass", "exec", name, "--", "bash", "-c", 'echo -e "setxkbmap br\\nexec openbox-session" > /home/ubuntu/.xsession'])
    subprocess.run(["multipass", "exec", name, "--", "bash", "-c", "chown ubuntu:ubuntu /home/ubuntu/.xsession"])

    print("\nHabilitando e iniciando o XRDP...")
    subprocess.run(["multipass", "exec", name, "--", "sudo", "systemctl", "enable", "xrdp"])
    subprocess.run(["multipass", "exec", name, "--", "sudo", "systemctl", "restart", "xrdp"])

    print("\nAlterando senha do usuário ubuntu...")
    subprocess.run(["multipass", "exec", name, "--", "bash", "-c", 'echo "ubuntu:0731" | sudo chpasswd'])

    print("\nTransferindo o AppImage do Cursor para a instância...")
    subprocess.run(["multipass", "transfer", "Cursor-0.49.6-x86_64.AppImage", f"{name}:/home/ubuntu/"])

    print("\n✅ Tudo pronto! Acesse a instância com:")
    print(f"multipass shell {name}")
    print("Ou conecte via RDP ao IP da instância (use `multipass info` para ver o IP).")
    input("\nPressione Enter para voltar ao menu...")

def menu():
    while True:
        limpar_tela()
        print("""
==== GERENCIAR INSTANCIAS (Multipass + RDP) ====

1 - Listar Instâncias
2 - Conectar via RDP
3 - Iniciar VM
4 - Parar VM
5 - Reiniciar VM
6 - Detalhes da VM
7 - Criar VM
0 - Sair
""")
        escolha = input("Escolha a opção: ").strip()

        vms = listar_vms()

        if escolha == '1':
            mostrar_vms(vms)
            input("Pressione Enter para voltar ao menu...")

        elif escolha == '2':
            comando = menu_conectar(vms)
            if comando:
                conectar_rdp(comando)
                print("Conexão iniciada.")
                input("Pressione Enter para voltar ao menu...")

        elif escolha == '3':
            iniciar_vm(vms)

        elif escolha == '4':
            parar_vm(vms)

        elif escolha == '5':
            reiniciar_vm(vms)

        elif escolha == '6':
            detalhes_vm(vms)

        elif escolha == '7':
            criar_vm()

        elif escolha == '0':
            print("Saindo...")
            break

        else:
            print("Opção inválida!")
            input("Pressione Enter para tentar novamente...")

if __name__ == "__main__":
    menu()
