import socket
import yaml
import sys

def carica_configurazione(percorso_file):
    """
    Legge il file YAML di configurazione e ne estrae i parametri di avvio.
    Se il file non esiste, blocca l'avvio del server.
    """
    try:
        # Apriamo il file in modalità lettura ('r')
        with open(percorso_file, 'r') as file:
            config = yaml.safe_load(file)
        
        # Estraiamo i dati di host e porta dal dizionario generato dal parsing YAML
        host = config['server']['host']
        porta = config['server']['port']
        return host, porta

    except FileNotFoundError:
        # Gestione dell'errore se il file YAML manca: avvisa e chiude il programma (exit code 1)
        print(f"ERRORE CRITICO: Il file {percorso_file} non è stato trovato!")
        sys.exit(1)
    except Exception as e:
        # Intercetta altri errori (es. sintassi YAML errata)
        print(f"Errore durante la lettura dello YAML: {e}")
        sys.exit(1)

# 1. CARICAMENTO CONFIGURAZIONE
# Chiamiamo la funzione e salviamo i valori restituiti
HOST_CONFIG, PORT_CONFIG = carica_configurazione('server_config.yaml')

# 2. INIZIALIZZAZIONE DEL SOCKET SERVER
# AF_INET specifica l'uso di IPv4, SOCK_STREAM specifica l'uso del protocollo TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_REUSEADDR permette di riutilizzare la porta immediatamente dopo lo spegnimento del server, 
# evitando l'errore "Address already in use" durante i riavvii ravvicinati
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Associamo il socket all'indirizzo e alla porta letti dal file YAML
server_socket.bind((HOST_CONFIG, PORT_CONFIG))

# Mettiamo il server in ascolto, consentendo fino a 5 connessioni in coda
server_socket.listen(5)

print(f"Server in ascolto su http://{HOST_CONFIG}:{PORT_CONFIG}")

# Questo TRY esterno protegge tutto il ciclo di vita del server e gestisce lo spegnimento
try:
    # Loop infinito: il server continua ad accettare richieste finché non viene fermato
    while True:
        # accept() blocca l'esecuzione finché non arriva una richiesta da un client
        client_socket, client_address = server_socket.accept()
        print(f"Nuova connessione da: {client_address}")
        
        # Riceviamo i dati della richiesta HTTP (fino a 1024 byte) e li decodifichiamo
        request = client_socket.recv(1024).decode('utf-8')
        
        # Sotto-blocco per la gestione dei file HTML richiesti
        try:
            # Apriamo index.html in modalità lettura binaria ('rb')
            with open('index.html', 'rb') as file:
                html_body = file.read() 

            # Prepariamo gli header HTTP per una risposta di successo (200 OK)
            # Calcoliamo la lunghezza esatta del body per il Content-Length
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(html_body)}\r\n"
                "\r\n" 
            )
            
            # Inviamo prima gli header (codificati in byte) e poi il contenuto del file
            client_socket.sendall(headers.encode('utf-8') + html_body)

        except FileNotFoundError:
            # Se index.html non esiste, prepariamo una pagina di errore 404 hardcoded
            errore_body = "<html><body><h1>Errore 404: File index.html non trovato!</h1></body></html>".encode('utf-8')
            
            headers_errore = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(errore_body)}\r\n"
                "\r\n"
            )
            client_socket.sendall(headers_errore.encode('utf-8') + errore_body)
        
        # Chiudiamo sempre il socket del client al termine della risposta
        client_socket.close()

except KeyboardInterrupt:
    # Gestione dell'interruzione manuale da terminale (es. CTRL+C)
    print("\nSpegnimento del server in corso...")
finally:
    # Il blocco finally garantisce che il socket del server venga chiuso
    # liberando le risorse di rete, indipendentemente da come si è interrotto il programma
    server_socket.close()