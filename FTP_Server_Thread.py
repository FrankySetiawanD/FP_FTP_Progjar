import select
import socket
import sys
import threading
import os

#Class untuk Server
class Server:
    #spesifikasi dari socket ftp server
    def __init__(self):
        self.host = 'localhost'
        self.port = 2728
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []
  
    #inisialisasi socket ftp server    
    def open_socket(self):        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host,self.port))
        self.server.listen(5)
        print 'Server FTP Siap'
        
    #menu yang akan dijalankan pertama kali saat server dimulai
    def run(self):
        self.open_socket()
        #input = [self.server, sys.stdin]
        input = [self.server]
        #running = 1
        while True:
            #select untuk socket
            inputready,outputready,exceptready = select.select(input,[],[])
            for s in inputready:
                if s == self.server:
                    # handle the server socket - menjalankan client dengan multithreading
                    #self.client_socket, self.client_address = self.server.accept()
                    #self.input.append(self.client_socket)
                    c = Client((self.server.accept()))
                    c.start()
                    self.threads.append(c)
                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    break

        # close all threads
        self.server.close()
        for c in self.threads:
            c.join()

currdir=os.path.abspath('.')
#Class untuk Client
class Client(threading.Thread):
    #Spesifikasi untuk socket client yang berhasil terhubung
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 4096
        self.id_exit = True
        self.basewd=currdir
        self.cwd=self.basewd

    #menu yang akan jalan pertama kali saat client berhasil terhubung    
    def run(self):
        self.welcome_msg = '220-FTP Server Versi 1.0\r\nRespon: 220-Ditulis oleh Kelompok XXX\r\n'
        print 'Respon: ' + self.welcome_msg.strip(), self.client.getpeername()
        self.client.send(self.welcome_msg)
        
        while self.id_exit:
            self.data = self.client.recv(self.size)
            cmd = self.data
            if self.data :
                self.cek_user()
            else:
                self.message = '500 Perintah tidak diketahui\r\n'
                self.login_msg = '530 Silahkan masuk terlebih dahulu\r\n'
                print 'Respon: ' + self.message.strip, self.client.getpeername()
                print 'Respon: '+ self.login_msg, self.client.getpeername()
                self.client.sendall(self.message + self.login_msg)

    #menu untuk pengecekan user           
    def cek_user(self):
        self.command = self.data
        print 'Perintah: ' + self.command.strip()
        if 'USER Adian\r\n' in self.command:
            self.nama_user = self.command.split(' ')
            self.login_msg = '331 Silahkan masukan password untuk ' + self.nama_user[1] + '\r\n'
            print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
            self.client.send(self.login_msg)

            self.command = self.client.recv(self.size)

            if self.command == 'PASS 1234\r\n':
                self.login_msg = '230 Anda masuk\r\n'
                self.client.send(self.login_msg)
                print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
                self.menu_log_in()
                          
            else:
                self.login_msg = 'Username atau password salah\r\n'
                self.client.send(self.login_msg)
                print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
                #print 'E'
                        
        else:
            self.message = '500 Perintah tidak diketahui\r\n'
            self.login_msg = '530 Silahkan masuk terlebih dahulu'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
            self.client.sendall(self.message + self.login_msg)

    #menu untuk masuk ke mode pasif    
    def passive_mode(self):
        self.command = self.client.recv(self.size)
        print 'Perintah: ' + self.command.strip(), self.client.getpeername()
        
        if 'TYPE' in self.command:
            self.code_type = self.command.split(' ')[-1].split('\r\n')
            self.message = '220 TYPE diubah ke ', self.code_type
            self.message += '\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            self.passive_mode()

        if self.command == 'QUIT\r\n':
            self.login_msg = '221 Anda keluar\r\n'
            self.client.send(self.login_msg)
            print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
            self.stop()
            
        if self.command == 'SYST\r\n':
            self.syst()
            
        if self.command == 'PWD\r\n':
            self.pwd()

        if 'CWD' in self.command:
            self.code_type = self.command.split(' ')[-1].split('\r\n')
            print self.code_type
            self.cwd()
      
    #menu untuk user yang apabila telah berhasil login
    def menu_log_in(self):
        self.command = self.client.recv(self.size)
        print 'Perintah: ' + self.command.strip(), self.client.getpeername()

        if self.command == 'PASV\r\n':
            self.message = '227 Masuk ke mode pasif\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            self.passive_mode()
                                                                                                 
        if self.command == 'QUIT\r\n':
            self.login_msg = '221 Anda keluar\r\n'
            self.client.send(self.login_msg)
            print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
            self.stop()
            #self.input_socket.remove(self.sock)

        else:
            self.message = '500 perintah tidak diketahui\r\n'
            print 'Respon: ' + self.massage.strip(), self.client.getpeername()
            self.client.send(self.message)
            self.menu_log_in()
            
    def stop(self):
        self.id_exit = False
        self.client.close()

    def syst(self):
        self.SYST_msg = ('215 UNIX Type: L8\r\n')
        self.client.send(self.SYST_msg)
        print 'Respon: ' + self.SYST_msg.strip(), self.client.getpeername()
        self.passive_mode()

    def pwd(self):
        cwd=os.path.relpath(self.cwd,self.basewd)
        if cwd=='.':
            cwd='/'
        else:
            cwd='/'+cwd
        self.client.send('257 \"%s\"\r\n' % cwd)
        self.passive_mode()

    def cwd(self):
        cmd  = self.data
        chwd = cmd[4:-1]
        if chwd=='/':
         #   self.client.send('1')
            self.cwd=self.basewd
        elif chwd[0]=='/':
         #   self.client.send('2')
            self.cwd=os.path.join(self.basewd,chwd[1:])
        else:
         #   self.client.send('3')
            self.cwd=os.path.join(self.cwd,chwd)
        self.client.send('250 OK.\r\n')
        self.passive_mode()
        
if __name__ == "__main__":
    s = Server()
    s.run()



