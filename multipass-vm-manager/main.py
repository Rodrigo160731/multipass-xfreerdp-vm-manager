import subprocess
import json
import os
import getpass

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

def conectar_rdp(ip):
    senha = getpass.getpass("Digite a senha do usuário 'ubuntu': ")
    comando = f"xfreerdp /u:ubuntu /p:{senha} /v:{ip}"
    try:
        subprocess.Popen(comando.split())
        print("Conexão RDP iniciada.")
    except Exception as e:
        print(f"Erro ao iniciar RDP: {e}")
    input("Pressione Enter para voltar ao menu...")

def menu_conectar(vms):
    mostrar_vms(vms)
    if not vms:
        input("Pressione Enter para voltar ao menu...")
        return

    try:
        escolha = int(input("Escolha a VM (número): "))
        vm = vms[escolha]
    except (ValueError, IndexError):
        print("Escolha inválida!")
        input("Pressione Enter para voltar ao menu...")
        return

    ips = vm.get("ipv4", [])
    if not ips:
        print("A VM está desligada ou sem IP.")
        input("Pressione Enter para voltar ao menu...")
        return

    conectar_rdp(ips[0])

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

    name = input("Nome do servidor: ").strip()
    if not name:
        print("Nome inválido.")
        input("Pressione Enter para voltar ao menu...")
        return

    # Verificar se a VM já existe
    resultado = subprocess.run(["multipass", "info", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if resultado.returncode == 0:
        resposta = input(f"⚠️ Já existe uma VM chamada '{name}'. Deseja usar essa VM existente? (s/n): ").strip().lower()
        if resposta != 's':
            print("Cancelado.")
            input("Pressione Enter para voltar ao menu...")
            return
    else:
        version = input("Versão do Ubuntu (ex: 22.04): ").strip()
        memory = input("Memória em GB (ex: 3): ").strip()
        disk = input("Tamanho do disco em GB (ex: 25): ").strip()

        print(f"\nCriando o servidor '{name}' com Ubuntu {version}, {memory} GB RAM, {disk} GB de disco...\n")

        cmd_launch = ["multipass", "launch", version, "--name", name, "--memory", f"{memory}G", "--disk", f"{disk}G"]
        subprocess.run(cmd_launch)

    print("\nInstalando interface gráfica e XRDP...")
    subprocess.run(["multipass", "exec", name, "--", "sudo", "apt", "update", "-y"])
    subprocess.run(["multipass", "exec", name, "--", "sudo", "apt", "install", "ubuntu-desktop", "xrdp", "-y"])

    senha = getpass.getpass("Defina a senha do usuário 'ubuntu': ")
    subprocess.run(["multipass", "exec", name, "--", "bash", "-c", f'echo "ubuntu:{senha}" | sudo chpasswd'])

    print("\n✅ VM pronta para uso com XRDP.")
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
            menu_conectar(vms)

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
