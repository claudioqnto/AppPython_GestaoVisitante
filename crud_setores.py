import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class SetorCRUD:
    def __init__(self, root):
        self.root = root
        self.root.title("CRUD de Setores")

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
        self.id_var = tk.IntVar()
        self.nome_var = tk.StringVar()
        self.descricao_var = tk.StringVar()

        # Widgets da interface
        self.create_widgets()
        self.carregar_setores()

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

    def carregar_setores(self):
        self.tree.delete(*self.tree.get_children())
        if self.conectar_db():
            try:
                self.cursor.execute("SELECT id, nome, descricao FROM setor")
                setores = self.cursor.fetchall()
                for setor in setores:
                    self.tree.insert("", tk.END, values=setor)
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao carregar setores: {err}")
            finally:
                self.desconectar_db()

    def adicionar_setor(self):
        nome = self.nome_entry.get()
        descricao = self.descricao_entry.get()

        if not nome or not descricao:
            messagebox.showerror("Erro", "Nome e Descrição são obrigatórios.")
            return

        if self.conectar_db():
            try:
                sql = "INSERT INTO setor (nome, descricao) VALUES (%s, %s)"
                val = (nome, descricao)
                self.cursor.execute(sql, val)
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Setor adicionado com sucesso.")
                self.carregar_setores()
                self.limpar_campos()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao adicionar setor: {err}")
            finally:
                self.desconectar_db()

    def selecionar_setor(self, event):
        item = self.tree.selection()[0]
        data = self.tree.item(item, 'values')
        if data:
            id_setor, nome, descricao = data
            self.id_var.set(id_setor)
            self.nome_entry.delete(0, tk.END)
            self.nome_entry.insert(0, nome)
            self.descricao_entry.delete(0, tk.END)
            self.descricao_entry.insert(0, descricao)

    def atualizar_setor(self):
        id_setor = self.id_var.get()
        nome = self.nome_entry.get()
        descricao = self.descricao_entry.get()

        if not nome or not descricao:
            messagebox.showerror("Erro", "Nome e Descrição são obrigatórios.")
            return

        if self.conectar_db():
            try:
                sql = "UPDATE setor SET nome=%s, descricao=%s WHERE id=%s"
                val = (nome, descricao, id_setor)
                self.cursor.execute(sql, val)
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Setor atualizado com sucesso.")
                self.carregar_setores()
                self.limpar_campos()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar setor: {err}")
            finally:
                self.desconectar_db()

    def deletar_setor(self):
        id_setor = self.id_var.get()

        if not id_setor:
            messagebox.showerror("Erro", "Selecione um setor para deletar.")
            return

        if messagebox.askyesno("Confirmação", "Tem certeza que deseja deletar este setor?"):
            if self.conectar_db():
                try:
                    sql = "DELETE FROM setor WHERE id=%s"
                    val = (id_setor,)
                    self.cursor.execute(sql, val)
                    self.conn.commit()
                    messagebox.showinfo("Sucesso", "Setor deletado com sucesso.")
                    self.carregar_setores()
                    self.limpar_campos()
                except mysql.connector.Error as err:
                    messagebox.showerror("Erro", f"Erro ao deletar setor: {err}")
                finally:
                    self.desconectar_db()

    def limpar_campos(self):
        self.id_var.set(0)
        self.nome_entry.delete(0, tk.END)
        self.descricao_entry.delete(0, tk.END)

    def create_widgets(self):
        # Frame para os campos de entrada
        input_frame = ttk.LabelFrame(self.root, text="Detalhes do Setor")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nome_entry = ttk.Entry(input_frame, textvariable=self.nome_var)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Descrição:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.descricao_entry = ttk.Entry(input_frame, textvariable=self.descricao_var)
        self.descricao_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Frame para os botões
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="Adicionar", command=self.adicionar_setor).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Atualizar", command=self.atualizar_setor).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deletar", command=self.deletar_setor).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar", command=self.limpar_campos).pack(side=tk.LEFT, padx=5)

        # Frame para a lista de setores
        list_frame = ttk.LabelFrame(self.root, text="Lista de Setores")
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Nome", "Descrição"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.selecionar_setor)

if __name__ == "__main__":
    root = tk.Tk()
    app = SetorCRUD(root)
    root.mainloop()