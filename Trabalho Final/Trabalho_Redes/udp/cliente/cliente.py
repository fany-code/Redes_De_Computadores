import socket
import os

# Solicita o IP e porta do servidor
HOST = input("Digite o IP do servidor: ")
PORT = int(input("Digite a porta do servidor: "))


# Cria o soquete UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Cliente iniciado com sucesso!')

while True:
    # Solicita ao usuário que digite o comando
    cmd = input('Digite o comando (ls, pwd, cd, scp): ')
    # Envia o comando para o servidor
    sock.sendto(cmd.encode('utf-8'), (HOST, PORT))

    if cmd.startswith('ls') or cmd.startswith('pwd'):
        # Recebe a resposta do servidor e imprime na tela
        data, addr = sock.recvfrom(1024)
        print(data.decode('utf-8'))

    elif cmd.startswith('cd'):
        # Recebe a resposta do servidor e imprime na tela
        data, addr = sock.recvfrom(1024)
        print(data.decode('utf-8'))

    elif cmd.startswith('scp'):
        # Recebe a resposta do servidor
        data, addr = sock.recvfrom(1024)
        response = data.decode('utf-8')
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
                    data, addr = sock.recvfrom(1024)
                    f.write(data)
                    received_bytes += len(data)

            print('Arquivo recebido com sucesso!')


sock.close()
