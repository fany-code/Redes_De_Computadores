# SERVIDOR TCP

import socket
import os

# Solicita a porta ao usuário
while True:
    try:
        PORT = int(input("Digite a porta do servidor: "))
        break
    except ValueError:
        print("Por favor, digite um número inteiro válido.")

# Cria o soquete TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Liga o soquete à porta especificada
sock.bind(("", PORT))
# Define o limite máximo de conexões pendentes na fila
sock.listen(5)

print('Servidor iniciado na porta', PORT)
print('Aguardando conexões de clientes')

while True:
    # Aguarda uma conexão
    conn, addr = sock.accept()
    print('Conexão estabelecida com', addr)

    # Define o timeout para receber comandos do cliente
    conn.settimeout(60)  # Defina o valor desejado para o timeout (em segundos)

    while True:
        # Recebe o comando do cliente
        data = conn.recv(1024).decode('utf-8')

        if not data:
            print('Conexão encerrada pelo cliente.')
            break
        
        print('Comando recebido:', data)

        if data == 'exit':
            print('Conexão encerrada pelo cliente.')
            # Envia uma mensagem de encerramento para o cliente
            conn.sendall('exit'.encode('utf-8'))
            break

        if data.startswith('ls'):
            # Lista arquivos e envia a lista de volta ao cliente
            files = os.listdir('.')
            conn.sendall(str(files).encode('utf-8'))

        elif data.startswith('pwd'):
            # Obtém o diretório atual e envia para o cliente
            pwd = os.getcwd()
            conn.sendall(pwd.encode('utf-8'))

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
                    new_dir = os.path.join(current_dir, path)
                    os.chdir(new_dir)
                conn.sendall('Diretório alterado'.encode('utf-8'))
            except FileNotFoundError:
                conn.sendall('Caminho não encontrado'.encode('utf-8'))
            except NotADirectoryError:
                conn.sendall('O caminho não é um diretório'.encode('utf-8'))
            except PermissionError:
                conn.sendall('Permissão negada para acessar o diretório'.encode('utf-8'))
            except Exception as e:
                conn.sendall('Erro ao alterar o diretório: {}'.format(e).encode('utf-8'))

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
                conn.sendall('Arquivo não encontrado!'.encode('utf-8'))
            else:
                # Envia o tamanho do arquivo para o cliente
                filesize = os.path.getsize(full_path)  # obtém o tamanho do arquivo
                conn.sendall(str(filesize).encode('utf-8'))  # codificando string em UTF-8

                # Abre o arquivo em modo binário
                with open(full_path, 'rb') as f:
                    # Utiliza sendfile para transferir diretamente os dados do arquivo
                    sent_bytes = 0
                    while sent_bytes < filesize:
                        # Transfere os dados do arquivo para o cliente
                        sent_bytes += conn.sendfile(f, sent_bytes, filesize - sent_bytes)

                # Indica o fim da transferência do arquivo
                conn.sendall(b'')

                # Aguarda o ACK do cliente
                ack = conn.recv(1024).decode('utf-8')
                if ack == 'ACK':
                    print('Arquivo enviado com sucesso!') 
                else:
                    print('Erro ao enviar o arquivo.')

    # Encerra a conexão com o cliente atual
    conn.close()

