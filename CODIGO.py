import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ----------------------------
# Crear / Conectar BD
# ----------------------------
conexion = sqlite3.connect("finanzas.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    monto REAL,
    descripcion TEXT,
    fecha TEXT
)
""")
conexion.commit()

# ----------------------------
# Función: Registrar
# ----------------------------
def registrar():
    tipo = tipo_var.get()
    monto = monto_entry.get()
    descripcion = desc_entry.get()
    fecha = fecha_entry.get()

    if tipo == "" or monto == "":
        messagebox.showerror("Error", "Completa los campos obligatorios")
        return

    cursor.execute("""
        INSERT INTO transacciones (tipo, monto, descripcion, fecha)
        VALUES (?, ?, ?, ?)
    """, (tipo, monto, descripcion, fecha))

    conexion.commit()
    messagebox.showinfo("Éxito", "Transacción registrada")
    limpiar()
    mostrar()

# ----------------------------
# Limpiar campos
# ----------------------------
def limpiar():
    monto_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)
    fecha_entry.delete(0, tk.END)
    fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

# ----------------------------
# Mostrar registros
# ----------------------------
def mostrar():
    for fila in tabla.get_children():
        tabla.delete(fila)

    cursor.execute("SELECT * FROM transacciones")
    for row in cursor.fetchall():
        tabla.insert("", tk.END, values=row)

# ----------------------------
# Interfaz gráfica
# ----------------------------
ventana = tk.Tk()
ventana.title("Control de Ingresos y Gastos")
ventana.geometry("700x500")

# Tipo
tk.Label(ventana, text="Tipo").pack()
tipo_var = tk.StringVar()
tipo_combo = ttk.Combobox(
    ventana,
    textvariable=tipo_var,
    values=["Ingreso", "Gasto"]
)
tipo_combo.pack()

# Monto
tk.Label(ventana, text="Monto").pack()
monto_entry = tk.Entry(ventana)
monto_entry.pack()

# Descripción
tk.Label(ventana, text="Descripción").pack()
desc_entry = tk.Entry(ventana)
desc_entry.pack()

# Fecha
tk.Label(ventana, text="Fecha").pack()
fecha_entry = tk.Entry(ventana)
fecha_entry.pack()
fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

# Botón registrar
tk.Button(
    ventana,
    text="Registrar",
    command=registrar
).pack(pady=10)

# Tabla
columnas = ("ID", "Tipo", "Monto", "Descripción", "Fecha")
tabla = ttk.Treeview(
    ventana,
    columns=columnas,
    show="headings"
)

for col in columnas:
    tabla.heading(col, text=col)

tabla.pack(fill="both", expand=True)

mostrar()

ventana.mainloop()
