import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import mysql.connector
import io
import os

class VisitanteCRUD:
    def __init__(self, root):
        self.root = root
        self.root.title("CRUD de Visitantes")

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
        self.foto_var = tk.StringVar()
        self.nome_completo_var = tk.StringVar()
        self.cpf_var = tk.StringVar()
        self.rg_var = tk.StringVar()
        self.telefone_var = tk.StringVar()

        # Variável para a imagem exibida
        self.img_tk = None

        # Widgets da interface
        self.create_widgets()
        self.carregar_visitantes()

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

    def carregar_visitantes(self):
        self.tree.delete(*self.tree.get_children())
        if self.conectar_db():
            try:
                self.cursor.execute("SELECT id, foto, nome_completo, cpf, rg, telefone FROM visitante")
                visitantes = self.cursor.fetchall()
                for visitante in visitantes:
                    self.tree.insert("", tk.END, values=visitante)
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao carregar visitantes: {err}")
            finally:
                self.desconectar_db()

    def adicionar_visitante(self):
        nome_completo = self.nome_completo_entry.get()
        cpf = self.cpf_entry.get()
        rg = self.rg_entry.get()
        telefone = self.telefone_entry.get()
        foto_path = self.foto_var.get()

        if not nome_completo or not cpf or not telefone:
            messagebox.showerror("Erro", "Nome Completo, CPF e Telefone são obrigatórios.")
            return

        foto_blob = None
        if foto_path:
            try:
                with open(foto_path, 'rb') as file:
                    foto_blob = file.read()
            except FileNotFoundError:
                messagebox.showerror("Erro", "Arquivo de foto não encontrado.")
                return

        if self.conectar_db():
            try:
                sql = "INSERT INTO visitante (foto, nome_completo, cpf, rg, telefone) VALUES (%s, %s, %s, %s, %s)"
                val = (foto_blob, nome_completo, cpf, rg if rg else None, telefone)
                self.cursor.execute(sql, val)
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Visitante adicionado com sucesso.")
                self.carregar_visitantes()
                self.limpar_campos()
                self.exibir_imagem(None)
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao adicionar visitante: {err}")
            finally:
                self.desconectar_db()

    def selecionar_visitante(self, event):
        item = self.tree.selection()[0]
        id_visitante, foto_blob, nome_completo, cpf, rg, telefone = self.tree.item(item, 'values')
        self.id_var.set(id_visitante)
        self.nome_completo_entry.delete(0, tk.END)
        self.nome_completo_entry.insert(0, nome_completo)
        self.cpf_entry.delete(0, tk.END)
        self.cpf_entry.insert(0, cpf)
        self.rg_entry.delete(0, tk.END)
        self.rg_entry.insert(0, rg if rg else "")
        self.telefone_entry.delete(0, tk.END)
        self.telefone_entry.insert(0, telefone)
        self.foto_var.set("")  # Limpa o caminho do arquivo selecionado

        self.exibir_imagem(foto_blob)

    def atualizar_visitante(self):
        id_visitante = self.id_var.get()
        nome_completo = self.nome_completo_entry.get()
        cpf = self.cpf_entry.get()
        rg = self.rg_entry.get()
        telefone = self.telefone_entry.get()
        foto_path = self.foto_var.get()
        foto_blob = None

        if not id_visitante:
            messagebox.showerror("Erro", "Selecione um visitante para atualizar.")
            return
        if not nome_completo or not cpf or not telefone:
            messagebox.showerror("Erro", "Nome Completo, CPF e Telefone são obrigatórios.")
            return

        if foto_path:
            try:
                with open(foto_path, 'rb') as file:
                    foto_blob = file.read()
            except FileNotFoundError:
                messagebox.showerror("Erro", "Arquivo de foto não encontrado.")
                return

        if self.conectar_db():
            try:
                sql = "UPDATE visitante SET nome_completo=%s, cpf=%s, rg=%s, telefone=%s"
                val = (nome_completo, cpf, rg if rg else None, telefone)
                if foto_blob:
                    sql += ", foto=%s"
                    val += (foto_blob,)
                sql += " WHERE id=%s"
                val += (id_visitante,)

                self.cursor.execute(sql, val)
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Visitante atualizado com sucesso.")
                self.carregar_visitantes()
                self.limpar_campos()
                self.exibir_imagem(None)
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar visitante: {err}")
            finally:
                self.desconectar_db()

    def deletar_visitante(self):
        id_visitante = self.id_var.get()

        if not id_visitante:
            messagebox.showerror("Erro", "Selecione um visitante para deletar.")
            return

        if messagebox.askyesno("Confirmação", "Tem certeza que deseja deletar este visitante?"):
            if self.conectar_db():
                try:
                    sql = "DELETE FROM visitante WHERE id=%s"
                    val = (id_visitante,)
                    self.cursor.execute(sql, val)
                    self.conn.commit()
                    messagebox.showinfo("Sucesso", "Visitante deletado com sucesso.")
                    self.carregar_visitantes()
                    self.limpar_campos()
                    self.exibir_imagem(None)
                except mysql.connector.Error as err:
                    messagebox.showerror("Erro", f"Erro ao deletar visitante: {err}")
                finally:
                    self.desconectar_db()

    def limpar_campos(self):
        self.id_var.set(0)
        self.foto_var.set("")
        self.nome_completo_entry.delete(0, tk.END)
        self.cpf_entry.delete(0, tk.END)
        self.rg_entry.delete(0, tk.END)
        self.telefone_entry.delete(0, tk.END)
        self.exibir_imagem(None)

    def selecionar_foto(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar Foto",
            filetypes=[("Arquivos de Imagem", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            self.foto_var.set(file_path)
            self.exibir_imagem_local(file_path)

    def exibir_imagem(self, foto_blob):
        try:
            if foto_blob:
                image = Image.open(io.BytesIO(foto_blob))
                image.thumbnail((100, 100))  # Redimensiona para exibição
                self.img_tk = ImageTk.PhotoImage(image)
                self.foto_label.config(image=self.img_tk)
            else:
                # Exibe uma imagem padrão ou limpa o label
                self.foto_label.config(image="")
                self.img_tk = None
        except Exception as e:
            print(f"Erro ao exibir imagem: {e}")
            self.foto_label.config(image="")
            self.img_tk = None

    def exibir_imagem_local(self, file_path):
        try:
            image = Image.open(file_path)
            image.thumbnail((100, 100))
            self.img_tk = ImageTk.PhotoImage(image)
            self.foto_label.config(image=self.img_tk)
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo de imagem não encontrado.")
        except Exception as e:
            print(f"Erro ao exibir imagem local: {e}")
            self.foto_label.config(image="")
            self.img_tk = None

    def create_widgets(self):
        # Frame para os campos de entrada
        input_frame = ttk.LabelFrame(self.root, text="Detalhes do Visitante")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Foto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.foto_label = ttk.Label(input_frame)
        self.foto_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew", rowspan=2)
        ttk.Button(input_frame, text="Selecionar Foto", command=self.selecionar_foto).grid(row=1, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Nome Completo:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.nome_completo_entry = ttk.Entry(input_frame, textvariable=self.nome_completo_var)
        self.nome_completo_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="CPF:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.cpf_entry = ttk.Entry(input_frame, textvariable=self.cpf_var)
        self.cpf_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="RG:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.rg_entry = ttk.Entry(input_frame, textvariable=self.rg_var)
        self.rg_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Telefone:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.telefone_entry = ttk.Entry(input_frame, textvariable=self.telefone_var)
        self.telefone_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        # Frame para os botões
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="Adicionar", command=self.adicionar_visitante).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Atualizar", command=self.atualizar_visitante).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deletar", command=self.deletar_visitante).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar", command=self.limpar_campos).pack(side=tk.LEFT, padx=5)

        # Frame para a lista de visitantes
        list_frame = ttk.LabelFrame(self.root, text="Lista de Visitantes")
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Foto", "Nome Completo", "CPF", "RG", "Telefone"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Foto", text="Foto")
        self.tree.heading("Nome Completo", text="Nome Completo")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("RG", text="RG")
        self.tree.heading("Telefone", text="Telefone")
        self.tree.column("Foto", width=100) # Ajusta a largura da coluna da foto
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.selecionar_visitante)

if __name__ == "__main__":
    root = tk.Tk()
    app = VisitanteCRUD(root)
    root.mainloop()
