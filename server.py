import socket
import yaml
import sys

def carica_configurazione(percorso_file):
    try:
        with open(percorso_file, 'r') as file:
            config = yaml.safe_load(file)
        
        # Estraiamo i dati dal dizionario YAML
        host = config['server']['host']
        porta = config['server']['port']
        return host, porta

    except FileNotFoundError:
        print(f"ERRORE CRITICO: Il file {percorso_file} non è stato trovato!")
        sys.exit(1)
    except Exception as e:
        print(f"Errore durante la lettura dello YAML: {e}")
        sys.exit(1)


HOST_CONFIG, PORT_CONFIG = carica_configurazione('server_config.yaml')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST_CONFIG, PORT_CONFIG))
server_socket.listen(5)

print(f"Server in ascolto su http://{HOST_CONFIG}:{PORT_CONFIG}")

# Questo TRY protegge tutto il ciclo di vita del server
try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Nuova connessione da: {client_address}")
        
        request = client_socket.recv(1024).decode('utf-8')
        
        # Sotto-blocco per la gestione dei file HTML
        try:
            with open('index.html', 'rb') as file:
                html_body = file.read() 

            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(html_body)}\r\n"
                "\r\n" 
            )
            client_socket.sendall(headers.encode('utf-8') + html_body)

        except FileNotFoundError:
            errore_body = "<html><body><h1>Errore 404: File index.html non trovato!</h1></body></html>".encode('utf-8')
            headers_errore = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(errore_body)}\r\n"
                "\r\n"
            )
            client_socket.sendall(headers_errore.encode('utf-8') + errore_body)
        
        
        client_socket.close()

except KeyboardInterrupt:
    print("\nSpegnimento del server in corso...")
finally:
    server_socket.close()