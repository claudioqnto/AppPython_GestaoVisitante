import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib  # Para hash da senha

class UsuarioCRUD:
    def __init__(self, root):
        self.root = root
        self.root.title("CRUD de Usuários")

        # Configurações do Banco de Dados
        self.db_config = {
            'host': 'localhost',
            'user': 'root',  # Substitua pelo seu usuário MySQL
            'password': '',  # Substitua pela sua senha MySQL
            'database': 'controle_acesso'
        }
        self.conn = None
        self.cursor = None

        # Variáveis para os campos
        self.nip_var = tk.IntVar()
        self.cpf_var = tk.StringVar()
        self.nome_completo_var = tk.StringVar()
        self.nome_guerra_var = tk.StringVar()
        self.senha_var = tk.StringVar()
        self.grad_var = tk.StringVar()
        self.esp_var = tk.StringVar()

        # Widgets da interface
        self.create_widgets()
        self.carregar_usuarios()

    def conectar_db(self):
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {err}")
            return False
        return True

    def desconectar_db(self):
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    def carregar_usuarios(self):
        self.tree.delete(*self.tree.get_children())
        if self.conectar_db():
            try:
                self.cursor.execute("SELECT nip, cpf, nome_completo, nome_guerra, grad, esp FROM usuario")
                usuarios = self.cursor.fetchall()
                for usuario in usuarios:
                    self.tree.insert("", tk.END, values=usuario)
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao carregar usuários: {err}")
            finally:
                self.desconectar_db()

    def adicionar_usuario(self):
        nip = self.nip_entry.get()
        cpf = self.cpf_entry.get()
        nome_completo = self.nome_completo_entry.get()
        nome_guerra = self.nome_guerra_entry.get()
        senha = self.senha_entry.get()
        grad = self.grad_entry.get()
        esp = self.esp_entry.get()

        if not nome_completo or not senha or not grad or not esp:
            messagebox.showerror("Erro", "Nome Completo, Senha, Graduação e Especialidade são obrigatórios.")
            return

        # Hash da senha antes de salvar
        hashed_senha = hashlib.sha256(senha.encode()).hexdigest()

        if self.conectar_db():
            try:
                sql = "INSERT INTO usuario (nip, cpf, nome_completo, nome_guerra, senha, grad, esp) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                val = (nip if nip else None, cpf if cpf else None, nome_completo, nome_guerra if nome_guerra else None, hashed_senha, grad, esp)
                self.cursor.execute(sql, val)
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Usuário adicionado com sucesso.")
                self.carregar_usuarios()
                self.limpar_campos()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao adicionar usuário: {err}")
            finally:
                self.desconectar_db()

    def selecionar_usuario(self, event):
        item = self.tree.selection()[0]
        nip, cpf, nome_completo, nome_guerra, grad, esp = self.tree.item(item, 'values')
        self.nip_var.set(nip)
        self.cpf_var.set(cpf if cpf else "")
        self.nome_completo_entry.delete(0, tk.END)
        self.nome_completo_entry.insert(0, nome_completo)
        self.nome_guerra_entry.delete(0, tk.END)
        self.nome_guerra_entry.insert(0, nome_guerra if nome_guerra else "")
        self.senha_entry.delete(0, tk.END)
        self.senha_entry.insert(0, "") # Não exibir a senha hash
        self.grad_entry.delete(0, tk.END)
        self.grad_entry.insert(0, grad)
        self.esp_entry.delete(0, tk.END)
        self.esp_entry.insert(0, esp)

    def atualizar_usuario(self):
        nip_original = self.nip_var.get()
        cpf = self.cpf_entry.get()
        nome_completo = self.nome_completo_entry.get()
        nome_guerra = self.nome_guerra_entry.get()
        senha = self.senha_entry.get()
        grad = self.grad_entry.get()
        esp = self.esp_entry.get()

        if not nome_completo or not grad or not esp:
            messagebox.showerror("Erro", "Nome Completo, Graduação e Especialidade são obrigatórios.")
            return

        if self.conectar_db():
            try:
                sql = "UPDATE usuario SET cpf=%s, nome_completo=%s, nome_guerra=%s, grad=%s, esp=%s WHERE nip=%s"
                val = (cpf if cpf else None, nome_completo, nome_guerra if nome_guerra else None, grad, esp, nip_original)
                if senha:
                    hashed_senha = hashlib.sha256(senha.encode()).hexdigest()
                    sql = "UPDATE usuario SET cpf=%s, nome_completo=%s, nome_guerra=%s, senha=%s, grad=%s, esp=%s WHERE nip=%s"
                    val = (cpf if cpf else None, nome_completo, nome_guerra if nome_guerra else None, hashed_senha, grad, esp, nip_original)

                self.cursor.execute(sql, val)
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso.")
                self.carregar_usuarios()
                self.limpar_campos()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar usuário: {err}")
            finally:
                self.desconectar_db()

    def deletar_usuario(self):
        nip = self.nip_var.get()

        if not nip:
            messagebox.showerror("Erro", "Selecione um usuário para deletar.")
            return

        if messagebox.askyesno("Confirmação", "Tem certeza que deseja deletar este usuário?"):
            if self.conectar_db():
                try:
                    sql = "DELETE FROM usuario WHERE nip=%s"
                    val = (nip,)
                    self.cursor.execute(sql, val)
                    self.conn.commit()
                    messagebox.showinfo("Sucesso", "Usuário deletado com sucesso.")
                    self.carregar_usuarios()
                    self.limpar_campos()
                except mysql.connector.Error as err:
                    messagebox.showerror("Erro", f"Erro ao deletar usuário: {err}")
                finally:
                    self.desconectar_db()

    def limpar_campos(self):
        self.nip_var.set(0)
        self.cpf_var.set("")
        self.nome_completo_entry.delete(0, tk.END)
        self.nome_guerra_entry.delete(0, tk.END)
        self.senha_entry.delete(0, tk.END)
        self.grad_entry.delete(0, tk.END)
        self.esp_entry.delete(0, tk.END)

    def create_widgets(self):
        # Frame para os campos de entrada
        input_frame = ttk.LabelFrame(self.root, text="Detalhes do Usuário")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="NIP:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nip_entry = ttk.Entry(input_frame, textvariable=self.nip_var)
        self.nip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="CPF:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.cpf_entry = ttk.Entry(input_frame, textvariable=self.cpf_var)
        self.cpf_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Nome Completo:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.nome_completo_entry = ttk.Entry(input_frame, textvariable=self.nome_completo_var)
        self.nome_completo_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Nome de Guerra:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.nome_guerra_entry = ttk.Entry(input_frame, textvariable=self.nome_guerra_var)
        self.nome_guerra_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Senha:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.senha_entry = ttk.Entry(input_frame, textvariable=self.senha_var, show="*") # Oculta a senha
        self.senha_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Graduação:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.grad_entry = ttk.Entry(input_frame, textvariable=self.grad_var)
        self.grad_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Especialidade:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.esp_entry = ttk.Entry(input_frame, textvariable=self.esp_var)
        self.esp_entry.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        # Frame para os botões
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="Adicionar", command=self.adicionar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Atualizar", command=self.atualizar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deletar", command=self.deletar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar", command=self.limpar_campos).pack(side=tk.LEFT, padx=5)

        # Frame para a lista de usuários
        list_frame = ttk.LabelFrame(self.root, text="Lista de Usuários")
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("NIP", "CPF", "Nome Completo", "Nome de Guerra", "Graduação", "Especialidade"), show="headings")
        self.tree.heading("NIP", text="NIP")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("Nome Completo", text="Nome Completo")
        self.tree.heading("Nome de Guerra", text="Nome de Guerra")
        self.tree.heading("Graduação", text="Graduação")
        self.tree.heading("Especialidade", text="Especialidade")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.selecionar_usuario)

if __name__ == "__main__":
    root = tk.Tk()
    app = UsuarioCRUD(root)
    root.mainloop()