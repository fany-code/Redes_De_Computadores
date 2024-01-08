# CLIENTE TCP

import socket
import os

# Solicita o IP e porta do servidor
HOST = input("Digite o IP do servidor: ")

# Solicita a porta ao usuário
while True:
    try:
        PORT = int(input("Digite a porta do servidor: "))
        break
    except ValueError:
        print("Por favor, digite um número inteiro válido.")

# Define o timeout em segundos
TIMEOUT = 100000

print('Cliente iniciado com sucesso!')

# Cria o soquete TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Define o timeout para o soquete
sock.settimeout(TIMEOUT)

try:
    # Estabelece conexão com o servidor
    sock.connect((HOST, PORT))

    while True:
        # Solicita ao usuário que digite o comando
        cmd = input('Digite o comando (ls, pwd, cd, scp, exit): ')

        if cmd == 'exit':
            print('Encerrando conexão com o servidor...')
            # Envia o comando para o servidor
            sock.sendall(cmd.encode('utf-8'))
            break

        # Envia o comando para o servidor
        sock.sendall(cmd.encode('utf-8'))

        try:
            response = sock.recv(1024).decode('utf-8')
        except socket.timeout:
            print('Tempo limite excedido. O servidor não respondeu dentro do tempo esperado.')
        else:
            if response == 'exit':
                print('Conexão encerrada pelo servidor.')
                break

            if cmd.startswith('ls') or cmd.startswith('pwd') or cmd.startswith('cd'):
                # Recebe a resposta do servidor e imprime na tela
                print(response)

            elif cmd.startswith('scp'):
                if response.startswith('Arquivo não encontrado!'):
                    # Se o arquivo não for encontrado, imprime a mensagem de erro e continua para o próximo comando
                    print(response)
                else:
                    # Se o arquivo existir, extrai o tamanho do arquivo da resposta
                    filesize = int(response)
                    # Obtém o nome do arquivo a ser recebido
                    filename = os.path.basename(cmd.split(' ')[1])

                    with open(filename, 'wb') as f:
                        received_bytes = 0
                        # Recebe os dados do arquivo em blocos de 1024 bytes e escreve no arquivo
                        while received_bytes < filesize:
                            data = sock.recv(1024)
                            if not data:
                                break
                            f.write(data)
                            received_bytes += len(data)

                    # Envia ACK do cliente para o servidor
                    sock.sendall('ACK'.encode('utf-8'))

                    # Aguarda a confirmação do servidor
                    ack = sock.recv(1024).decode('utf-8')

                    print('Arquivo recebido com sucesso!')

finally:
    sock.close()
