import socket
import os

# Solicita o IP e porta do servidor
#HOST = input("Digite o IP do servidor: ")

# Solicita a porta ao usuário
PORT = int(input("Digite a porta do servidor: "))


# Cria o soquete UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Ouve em todas as interfaces de rede
sock.bind(("", PORT))  

print('Servidor iniciado na porta', PORT)
print('Aguardando comandos de clientes')

while True:
    # Recebe dados e endereço do cliente
    data, address = sock.recvfrom(1024)
    data = data.decode('utf-8')
    print('Comando recebido:', data)

    if data.startswith('ls'):
        # Lista arquivos e envia a lista de volta ao cliente
        files = os.listdir('.')
        sock.sendto(str(files).encode('utf-8'), address)

    elif data.startswith('pwd'):
        # Obtém o diretório atual e envia para o cliente
        pwd = os.getcwd()
        sock.sendto(pwd.encode('utf-8'), address)

    elif data.startswith('cd'):
        # Altera o diretório de trabalho atual com base no caminho especificado
        path = data.split(' ')[1]
        try:
            if os.path.isabs(path):
                # Se o caminho é absoluto, altera diretamente para o novo diretório
                os.chdir(path)
            else:
                # Se o caminho é relativo, constrói o novo caminho baseado no diretório atual
                current_dir = os.getcwd() 
                new_dir = os.path.join(current_dir, path)           # junta o diretório atual com o caminho relativo  
                os.chdir(new_dir)                                   # altera para o novo diretório
            sock.sendto('Diretório alterado'.encode('utf-8'), address)
        except FileNotFoundError:
            # Envia mensagem de erro se o caminho não for encontrado
            sock.sendto('Caminho não encontrado'.encode('utf-8'), address)
        except NotADirectoryError:
            # Envia mensagem de erro se o caminho não for um diretório
            sock.sendto('O caminho não é um diretório'.encode('utf-8'), address)
        except PermissionError:
            # Envia mensagem de erro se houver permissão negada para acessar o diretório
            sock.sendto('Permissão negada para acessar o diretório'.encode('utf-8'), address)
        except Exception as e:
            # Envia mensagem de erro genérico se ocorrer outro tipo de exceção
            sock.sendto('Erro ao alterar o diretório: {}'.format(e).encode('utf-8'), address)

    elif data.startswith('scp'):
        # Envia um arquivo para o cliente
        filename = data.split(' ')[1]
        directory, file = os.path.split(filename)

        if not os.path.isabs(directory):
            # Se o caminho do diretório for relativo, constrói o novo caminho baseado no diretório atual
            current_dir = os.getcwd()
            directory = os.path.join(current_dir, directory)

        # Verifica se o arquivo existe no diretório especificado (relativo ou absoluto)
        full_path = os.path.join(directory, file)
        if not os.path.exists(full_path):
            # Envia mensagem de erro se o arquivo não existir
            sock.sendto('Arquivo não encontrado!'.encode('utf-8'), address)
        else:
            # Envia o tamanho do arquivo para o cliente
            filesize = os.path.getsize(full_path)  # obtém o tamanho do arquivo
            sock.sendto(str(filesize).encode('utf-8'), address)  # codificando string em UTF-8

            with open(full_path, 'rb') as f:
                while True:
                    # Lê blocos de dados do arquivo
                    filedata = f.read(1024)
                    # Se não houver mais dados no arquivo, sai do loop
                    if not filedata:
                        break
                    # Envia blocos de dados do arquivo para o cliente
                    sock.sendto(filedata, address)

            # Indica o fim da transferência do arquivo
            sock.sendto(b'', address)


sock.close()
