import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector 
from db_config import DB_CONFIG


class AppBD:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Base de Datos")
        self.root.geometry("800x500")

        self.conn = None
        self.cursor = None

        self.crear_widgets()
        self.conectar()

    def conectar(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
            self.estado_label.config(text=" Conectado", fg="green")
        except mysql.connector.Error as err:
            self.estado_label.config(text=" Sin conexión", fg="red")
            messagebox.showerror("Error de conexión", str(err))

    def desconectar(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.estado_label.config(text=" Desconectado", fg="gray")

    def crear_widgets(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=5)

        tk.Label(top, text="Tabla:").pack(side="left")
        self.tabla_entry = tk.Entry(top, width=20)
        self.tabla_entry.pack(side="left", padx=5)
        self.tabla_entry.insert(0, "Productos")

        tk.Button(top, text="Cargar", command=self.cargar_datos).pack(side="left", padx=5)
        tk.Button(top, text="Reconectar", command=self.conectar).pack(side="left", padx=5)

        self.estado_label = tk.Label(top, text="Conectando...", fg="orange")
        self.estado_label.pack(side="right")

        frame_tabla = tk.Frame(self.root)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(frame_tabla, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll_y.set)

        bottom = tk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=5)

        tk.Label(bottom, text="SQL:").pack(side="left")
        self.sql_entry = tk.Entry(bottom)
        self.sql_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.sql_entry.insert(0, "SELECT * FROM clientes LIMIT 100")
        tk.Button(bottom, text="Ejecutar", command=self.ejecutar_sql).pack(side="left")

    def cargar_datos(self):
        tabla = self.tabla_entry.get().strip()
        if not tabla:
            messagebox.showwarning("Aviso", "Escribe el nombre de una tabla")
            return
        try:
            self.cursor.execute(f"SELECT * FROM {tabla} LIMIT 500")
            filas = self.cursor.fetchall()
            self.mostrar_filas(filas)
        except mysql.connector.Error as err:
            messagebox.showerror("Error SQL", str(err))

    def ejecutar_sql(self):
        sql = self.sql_entry.get().strip()
        if not sql:
            return
        try:
            self.cursor.execute(sql)
            if self.cursor.with_rows:
                filas = self.cursor.fetchall()
                self.mostrar_filas(filas)
            else:
                self.conn.commit()
                messagebox.showinfo("OK", f"Filas afectadas: {self.cursor.rowcount}")
        except mysql.connector.Error as err:
            messagebox.showerror("Error SQL", str(err))

    def mostrar_filas(self, filas):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()

        if not filas:
            return

        columnas = list(filas[0].keys())
        self.tree["columns"] = columnas
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        for fila in filas:
            self.tree.insert("", "end", values=[fila[c] for c in columnas])

    def on_close(self):
        self.desconectar()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AppBD(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()