# Pedrollo_Roberto_webserver_YAML
1) L'utilizzo della libreria yaml permette di fare il parsing del file server_config.yaml ed estrarre i parametri host e port dal dizionario risultante.
2) La funzione carica_configurazione protegge l'apertura del file YAML tramite un blocco try-except.
3) In caso di assenza del file (FileNotFoundError) o di errori di sintassi YAML (Exception), il server stampa un messaggio e interrompe immediatamente l'esecuzione usando sys.exit(1)
4) Il server inizializza un socket TCP standard (AF_INET, SOCK_STREAM)
5) È stata applicata l'opzione SO_REUSEADDR al socket prima del bind(), permette al sistema operativo di rilasciare immediatamente la porta quando il server viene spento, prevenendo il fastidioso errore "Address already in use" durante i riavvii rapidi
6) All'interno del loop di ascolto, il tentativo di aprire e leggere index.html è isolato in un sotto-blocco try-except
7) Se il file è presente, il server calcola dinamicamente la lunghezza del contenuto (Content-Length: {len(html_body)}) e restituisce una risposta HTTP/1.1 200 OK codificata in UTF-8.
8) Il loop principale di accettazione delle connessioni (while True) è racchiuso in un try globale che intercetta KeyboardInterrupt
   
