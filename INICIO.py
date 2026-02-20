import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime

# LIBRERIAS EXPORTACION
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook


# -----------------------
# BASE DE DATOS
# -----------------------

def conectar():
    return sqlite3.connect("banco.db")

def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        valor REAL,
        fecha TEXT
    )
    """)

    conn.commit()
    conn.close()


# -----------------------
# FUNCIONES
# -----------------------

def actualizar_listas():

    lista_depositos.delete(0, tk.END)
    lista_retiros.delete(0, tk.END)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id, tipo, valor FROM transacciones")

    for id, tipo, valor in cursor.fetchall():

        texto = f"{id} - {valor}"

        if tipo == "INGRESO":
            lista_depositos.insert(tk.END, texto)
        else:
            lista_retiros.insert(tk.END, texto)

    conn.close()
    actualizar_saldo()


def actualizar_saldo():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
        SUM(CASE WHEN tipo='INGRESO' THEN valor ELSE 0 END),
        SUM(CASE WHEN tipo='RETIRO' THEN valor ELSE 0 END)
        FROM transacciones
    """)

    ingresos, retiros = cursor.fetchone()

    ingresos = ingresos or 0
    retiros = retiros or 0

    saldo = ingresos - retiros

    entry_saldo.config(state="normal")
    entry_saldo.delete(0, tk.END)
    entry_saldo.insert(0, str(saldo))
    entry_saldo.config(state="readonly")

    conn.close()


# -----------------------
# TRANSACCIONES
# -----------------------

def depositar():

    try:

        valor = float(entry_valor.get())

        if valor <= 0:
            messagebox.showerror("Error", "Valor inválido")
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO transacciones(tipo, valor, fecha) VALUES (?, ?, ?)",
            ("INGRESO", valor, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()
        conn.close()

        entry_valor.delete(0, tk.END)

        actualizar_listas()

    except:
        messagebox.showerror("Error", "Ingrese un número válido")


def retirar():

    try:

        valor = float(entry_valor.get())

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
            SUM(CASE WHEN tipo='INGRESO' THEN valor ELSE 0 END),
            SUM(CASE WHEN tipo='RETIRO' THEN valor ELSE 0 END)
            FROM transacciones
        """)

        ingresos, retiros_db = cursor.fetchone()

        ingresos = ingresos or 0
        retiros_db = retiros_db or 0

        saldo = ingresos - retiros_db

        if valor > saldo:
            messagebox.showerror("Error", "Saldo insuficiente")
            return

        cursor.execute(
            "INSERT INTO transacciones(tipo, valor, fecha) VALUES (?, ?, ?)",
            ("RETIRO", valor, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()
        conn.close()

        entry_valor.delete(0, tk.END)

        actualizar_listas()

    except:
        messagebox.showerror("Error", "Ingrese un número válido")


# -----------------------
# ELIMINAR
# -----------------------

def eliminar_transaccion():

    seleccion_dep = lista_depositos.curselection()
    seleccion_ret = lista_retiros.curselection()

    if seleccion_dep:
        texto = lista_depositos.get(seleccion_dep)

    elif seleccion_ret:
        texto = lista_retiros.get(seleccion_ret)

    else:
        messagebox.showerror("Error", "Seleccione una transacción")
        return

    id = texto.split(" - ")[0]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transacciones WHERE id=?", (id,))

    conn.commit()
    conn.close()

    actualizar_listas()


# -----------------------
# NUEVO
# -----------------------

def nuevo():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transacciones")

    conn.commit()
    conn.close()

    actualizar_listas()


# -----------------------
# EXPORTAR PDF
# -----------------------

def exportar_pdf():

    ruta = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivo PDF", "*.pdf")]
    )

    if not ruta:
        return

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id, tipo, valor, fecha FROM transacciones")

    datos = cursor.fetchall()

    conn.close()

    doc = SimpleDocTemplate(ruta)

    elementos = []

    estilos = getSampleStyleSheet()

    elementos.append(Paragraph("Reporte de Transacciones", estilos["Heading1"]))

    tabla_datos = [["ID", "Tipo", "Valor", "Fecha"]]

    for fila in datos:
        tabla_datos.append(fila)

    tabla = Table(tabla_datos)

    tabla.setStyle([
        ("GRID", (0,0), (-1,-1), 1, "black")
    ])

    elementos.append(tabla)

    doc.build(elementos)

    messagebox.showinfo("Éxito", "PDF guardado correctamente")


# -----------------------
# EXPORTAR EXCEL
# -----------------------

def exportar_excel():

    ruta = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Archivo Excel", "*.xlsx")]
    )

    if not ruta:
        return

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id, tipo, valor, fecha FROM transacciones")

    datos = cursor.fetchall()

    conn.close()

    wb = Workbook()

    ws = wb.active

    ws.title = "Transacciones"

    ws.append(["ID", "Tipo", "Valor", "Fecha"])

    for fila in datos:
        ws.append(fila)

    wb.save(ruta)

    messagebox.showinfo("Éxito", "Excel guardado correctamente")


# -----------------------
# INTERFAZ
# -----------------------

crear_tabla()

ventana = tk.Tk()
ventana.title("Cuenta De Nicolas")
ventana.geometry("500x450")
ventana.config(bg="#FFFFFF")


# FRAME DATOS

frame_datos = tk.LabelFrame(ventana, text="Ingrese Datos", bg="#FFFFFF")
frame_datos.pack(fill="x", padx=10, pady=5)

tk.Label(frame_datos, text="Cliente:", bg="#FFFFFF").grid(row=0, column=0)

entry_cliente = tk.Entry(frame_datos)
entry_cliente.insert(0, "Hola Campeon")
entry_cliente.grid(row=0, column=1)

tk.Label(frame_datos, text="Monto:", bg="#FFFFFF").grid(row=1, column=0)

entry_valor = tk.Entry(frame_datos)
entry_valor.grid(row=1, column=1)


# FRAME TRANSACCIONES

frame_trans = tk.LabelFrame(ventana, text="Transacciones", bg="#FFFFFF")
frame_trans.pack(fill="x", padx=10, pady=5)

tk.Button(frame_trans, text="Depósitos", width=15, command=depositar).pack(side="left", padx=20)

tk.Button(frame_trans, text="Retiros", width=15, command=retirar).pack(side="left", padx=20)


# FRAME CUENTA

frame_cuenta = tk.LabelFrame(ventana, text="Cuenta de Ahorros", bg="#FFFFFF")
frame_cuenta.pack(fill="both", expand=True, padx=10, pady=5)


# RETIROS

tk.Label(frame_cuenta, text="Retiros", bg="#FFFFFF").grid(row=0, column=0)

lista_retiros = tk.Listbox(frame_cuenta, width=20, height=10)
lista_retiros.grid(row=1, column=0)


# DEPOSITOS

tk.Label(frame_cuenta, text="Depósitos", bg="#FFFFFF").grid(row=0, column=1)

lista_depositos = tk.Listbox(frame_cuenta, width=20, height=10)
lista_depositos.grid(row=1, column=1)


# SALDO

tk.Label(frame_cuenta, text="Saldo:", bg="#FFFFFF").grid(row=1, column=2)

entry_saldo = tk.Entry(frame_cuenta, state="readonly")
entry_saldo.grid(row=1, column=3)


# BOTONES

tk.Button(frame_cuenta, text="Nuevo", command=nuevo).grid(row=0, column=3)

tk.Button(frame_cuenta, text="Eliminar", command=eliminar_transaccion).grid(row=4, column=3)

tk.Button(frame_cuenta, text="Exportar PDF", command=exportar_pdf).grid(row=4, column=0
)

tk.Button(frame_cuenta, text="Exportar Excel", command=exportar_excel).grid(row=4, column=1)


# INICIAR

actualizar_listas()

ventana.mainloop()